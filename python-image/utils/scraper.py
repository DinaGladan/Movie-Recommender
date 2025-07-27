# from bs4 import BeautifulSoup
# import requests


# page_to_scrape = requests.get("https://letterboxd.com/films/popular/")
# soup = BeautifulSoup(page_to_scrape.text, "html.parser")

# # movies = soup.findAll("div", attrs={"class":"name js-widont prettify"})
# movies = soup.select(
#     "div.film-poster"
# )  # uzmi sve one divove koji imaju klasu film-poster
# for movie in movies:
#     title = movie.get("data-film-name")
#     print(title)

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from utils.db import get_db_connection, close_db_connection


chrome_options = Options()
chrome_options.add_argument("--headless")  # VAŽNO: bez GUI
chrome_options.add_argument("--no-sandbox")  # omogućuje rad u kontejneru
chrome_options.add_argument("--disable-dev-shm-usage")  # sprječava pad na low-memory
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)

# koristi potrebnu verziju chroma bez rucnog instaliranja
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)
url = "https://www.imdb.com/chart/top/"

driver.get(url)
print("Page title:", driver.title)
conn = get_db_connection()
cur = conn.cursor()

movies = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
for movie in movies:
    try:
        title_with_rank = movie.find_element(By.CSS_SELECTOR, "h3.ipc-title__text").text
        movie_title = title_with_rank.split(".")[1]
        year_and_duratin = movie.find_elements(
            By.CSS_SELECTOR, "span.cli-title-metadata-item"
        )
        movie_year = year_and_duratin[0].text
        movie_duration = year_and_duratin[1].text
        movie_rating = movie.find_element(
            By.CSS_SELECTOR, "span.ipc-rating-star--rating"
        ).text
        print(movie_rating, movie_title, movie_year, movie_duration)

        cur.execute(
            """
                INSERT INTO movies (title, year, duration, rating)
                VALUES (%s, %s, %s, %s)
            """,
            (movie_title, movie_year, movie_duration, movie_rating),
        )
        time.sleep(2)

    except Exception as er:
        print(f"Doslo je do :{er}")

conn.commit()
cur.close()
close_db_connection(conn)
driver.quit()
