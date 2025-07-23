from bs4 import BeautifulSoup
import requests

page_to_scrape = requests.get("https://letterboxd.com/film/barbie/")
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

movies = soup.findAll()
