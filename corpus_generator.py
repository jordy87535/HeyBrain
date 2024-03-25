import requests
from bs4 import BeautifulSoup
from main import HTMLParser
import pickle

class Corpus_generator:
    def get_popular_wikipedia_pages(self):
        url = "https://en.wikipedia.org/wiki/Wikipedia:Popular_pages"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='wikitable')
            
            if table:
                rows = table.find_all('tr')[1:]  # Exclude header row
                popular_pages = []
                links = [
                    "https://en.wikipedia.org/wiki/Dog",
                    "https://en.wikipedia.org/wiki/Frog",

                ]
                
                a = 1
                for row in rows:
                    
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                    
                        page_title = cells[1].text.strip()
                        if "Special" not in page_title and "x" not in page_title and "iki" not in page_title:
                            page = "https://en.wikipedia.org" + cells[1].find('a')['href']
                            parser = HTMLParser(page)
                            result = parser.parse_html()
                            if result:
                                data, count = parser.count_words(result)
                                if count >= 100000:
                                    a += 1
                                    popular_pages.append(page_title)
                                    print(page_title)
                                    links.append("https://en.wikipedia.org" + cells[1].find('a')['href'])
                    if a > 10:
                        break
                
                return links
            else:
                print("Failed to find the table on the page.")
        else:
            print("Failed to fetch the Wikipedia page.")

    def test_works(self):
        url = "https://en.wikipedia.org/wiki/George_Washington"
        parser = HTMLParser(url)
        result = parser.parse_html()
        if result:
            data = parser.count_words(result)
            return data


    def compile_corpus(self):
        popular_pages = self.get_popular_wikipedia_pages()

        if popular_pages:
            corpus = []
            for page in popular_pages:
                parser = HTMLParser(page)
                result = parser.parse_html()
                if result:
                    data = parser.count_words(result)
                    corpus.append(data)
            return corpus
        else:
            return None
        
if __name__ == "__main__":
    corpus_generator = Corpus_generator()
    corpus = corpus_generator.compile_corpus()
    if corpus:
        with open("corpus.pkl", "wb") as f:
            pickle.dump(corpus, f)
        print("Corpus saved successfully.")
    else:
        print("Failed to compile the corpus.")