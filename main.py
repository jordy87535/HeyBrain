import math
import re
import string
import requests
from bs4 import BeautifulSoup
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt



class HTMLParser:
    def __init__(self, url):
        self.url = url

    def parse_html(self):
        try:
            # Make a GET request to the URL
            response = requests.get(self.url)
            # Check if request was successful
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extract text from each component tag
                components = {}
                for tag in soup.find_all():
                    tag_text = tag.get_text()
                    if tag_text:
                        if tag.name in components:
                            components[tag.name].append(tag_text)
                        else:

                            components[tag.name] = [tag_text]
                return components
            else:
                print("Failed to retrieve HTML content from the URL")
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None
            
    
    def split_and_format_paragraph(self, paragraph):
        def remove_x(word):
            # check if the last char is a closing square bracket
            l,r = len(word), len(word)
            for ind, i in enumerate(word):
                if i not in string.punctuation:
                    l = min(l, ind)
                if i in string.punctuation:
                    if l != r:
                        r = ind
                        break
            return word[l:r]

        
        # Split the paragraph into words
        words = paragraph.split()
        formatted_words = []

        for word in words:
            # Convert the word to lowercase and remove punctuation from the end


            formatted_word = remove_x(word)
            formatted_word = formatted_word.lower().rstrip(string.punctuation)
            if formatted_word not in ["", " ", "p", "pp", "ng"] and not formatted_word.isdigit():
                formatted_words.append(formatted_word)
            
        return formatted_words
    
    def count_words(self, components):
        words =  {}
        count = 0
        for key in components:
            for text in components[key]:
                formatted_words = self.split_and_format_paragraph(text)
                
                for word in formatted_words:
                    count += 1
                    if word in words:
                        words[word] += 1
                    else:
                        words[word] = 1

        
        sorted_words = dict(sorted(words.items(), key=lambda item: item[1], reverse=True))
        top_100_words = dict(list(sorted_words.items())[:100])
        return sorted_words, count
    
    def get_phrases(self, components):
        phrases = {}
        count = 0
        
        for text in components['p']:
            formatted_words = self.split_and_format_paragraph(text)
            for i in range(len(formatted_words)):
                # Choosing phrase length to be capped at 5
                for k in range(2,5):
                    if i+k <= len(formatted_words):
                        count += 1
                        phrase = " ".join(formatted_words[i:i+k])
                        if phrase in phrases:
                            phrases[phrase] += 1
                        else:
                            phrases[phrase] = 1
        sorted_phrases = dict(sorted(phrases.items(), key=lambda item: item[1], reverse=True))
        top_100_phrases = dict(list(sorted_phrases.items())[:100])
        return sorted_phrases, count
    
    def merge_phrases(self, phrases, count):
        pass

        

    
    def calculate_tfidf(self, phrases, count_phrases, sorted_words, count_words):
        
        filepath = "corpus.pkl"
        with open(filepath, "rb") as file:
            corpus = pickle.load(file)

        def tf(word):
            return sorted_words[word] / count_words
        def idf(word):
            number = 1
            for doc, length in corpus:
                if word in doc:
                    number += 1
            return math.log10((len(corpus)+1) / number)

        tf_idf = {}
        
        for word in sorted_words:
            tf_idf[word] = tf(word) * idf(word)
        
        for phrase in phrases:
            # Geometric mean here
            words = phrase.split()
            score = 1
            for word in words:
                score *= tf(word) * idf(word)
            score = score ** (1/len(words))
            score *= phrases[phrase]

            tf_idf[phrase] = score

        sorted_tfidf = dict(sorted(tf_idf.items(), key=lambda item: item[1], reverse=True))
        top_100_tfidf = dict(list(sorted_tfidf.items())[:100])

        return sorted_tfidf
    
    def score_url(self):
        result = self.parse_html()
        sorted_words, count_words = self.count_words(result)
        sorted_phrases, count_phrases = self.get_phrases(result)
        scores = self.calculate_tfidf(sorted_phrases, count_phrases, sorted_words, count_words)
        top_100_scores = dict(list(scores.items())[:100])

        return top_100_scores
    
    def make_wordcloud(self):
        
        word_scores = self.score_url()
        word_freq = word_scores
    
        # Generate the word cloud
        wordcloud = WordCloud(width=800, height=400, background_color ='white').generate_from_frequencies(word_freq)
        
        # Display the word cloud using matplotlib
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()



if __name__ == "__main__":
    # Example usage
    url = "https://www.nytimes.com/"
    html_parser = HTMLParser(url)
    result = html_parser.parse_html()
    print(html_parser.score_url())
    html_parser.make_wordcloud()

