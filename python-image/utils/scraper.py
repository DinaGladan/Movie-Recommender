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


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# koristi potrebnu verziju chroma bez rucnog instaliranja
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
url = "https://www.imdb.com/chart/top/"

driver.get(url)

movies = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
for movie in movies:
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

driver.quit()
