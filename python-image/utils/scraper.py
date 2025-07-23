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

# from bs4 import BeautifulSoup
# import requests

# url = "https://archive.org/details/movies"
# page = requests.get(url)
# soup = BeautifulSoup(page.text, "html.parser")


# movies = soup.select("div.item-ttl a")

# for movie in movies:
#     title = movie.text.strip()  # Uzimamo tekst linka (naziv filma)
#     print(title)
