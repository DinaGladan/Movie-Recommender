# from bs4 import BeautifulSoup
# import requests
# za static HTML i jednostavno skrejpanje

# page_to_scrape = requests.get("https://letterboxd.com/films/popular/")
# soup = BeautifulSoup(page_to_scrape.text, "html.parser")

# # movies = soup.findAll("div", attrs={"class":"name js-widont prettify"})
# movies = soup.select(
#     "div.film-poster"
# )  # uzmi sve one divove koji imaju klasu film-poster
# for movie in movies:
#     title = movie.get("data-film-name")
#     print(title)

# bolji za stranice koje su automatizirane, dinamicne i koriste se JSom
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from utils.db import get_db_connection, close_db_connection


chrome_options = Options()
chrome_options.add_argument("--headless")  # VAŽNO: pokrece Chrom bez GUI prozora
chrome_options.add_argument("--no-sandbox")  # omogućuje rad u Docker kontejneru
chrome_options.add_argument("--disable-dev-shm-usage")  # sprječava pad na low-memory
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)  # dolazimo s neke konkretne adrese kao pravi korisnik, da nas stranica ne blokira

# koristi potrebnu verziju chroma bez rucnog instaliranja
service = Service("/usr/bin/chromedriver")  # putanja do chromdrivera
driver = webdriver.Chrome(service=service, options=chrome_options)  # pokreće ga
url = "https://www.imdb.com/chart/top/"

driver.get(url)
print("Page title:", driver.title)
conn = get_db_connection()
cur = conn.cursor()

movies = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
# print(f"Br pronadjenih {len(movies)}")
for movie in movies:
    try:
        # print("Uslo")
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
        movie_link = movie.find_element(By.TAG_NAME, "a").get_attribute("href")
        # print(f"{movie_link}")

        cur.execute(
            """
                SELECT id FROM movies WHERE title = %s AND year = %s
            """,
            (movie_title, movie_year),
        )
        result = cur.fetchone()

        if not result:
            cur.execute(
                """
                    INSERT INTO movies (title, year, duration, rating)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """,
                (movie_title, movie_year, movie_duration, movie_rating),
            )
            movie_id = cur.fetchone()[0]
        else:
            movie_id = result[0]

        driver.execute_script("window.open('');")  # otvori novi prozor
        driver.switch_to.window(driver.window_handles[1])  # prebaci se na njega
        driver.get(movie_link)  # otvori stranicu filma u njemu
        time.sleep(2)
        # genre_elements = driver.find_elements(By.CSS_SELECTOR, "span.ipc-chip__text")
        # detaljnije
        genre_elements = driver.find_elements(
            By.CSS_SELECTOR, "div.ipc-chip-list__scroller span.ipc-chip__text"
        )
        genres = [g.text for g in genre_elements]
        # print(f"Broj pronađenih žanrova: {len(genre_elements)}")
        # print(f"Lista žanrova: {genres}")  # prazna(krivi tag)
        for genre in genres:
            # provjera je li vec postoji taj zanr u tablici
            cur.execute("SELECT id FROM genres WHERE genre=%s", (genre,))
            genre_result = cur.fetchone()

            if genre_result is None:
                cur.execute(
                    """
                        INSERT INTO genres (genre) VALUES (%s) RETURNING id
                    """,
                    (genre,),
                )
                genre_id = cur.fetchone()[0]
            else:
                genre_id = genre_result[0]

            cur.execute(
                """
                    INSERT INTO movie_genre (movie_id, genre_id)
                    VALUES (%s, %s)
                """,
                (movie_id, genre_id),
            )
            # print(f"{movie_id} {genre_id}")

        sections = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list__item")
        for section in sections:
            try:
                label_elem = section.find_elements(By.CSS_SELECTOR, "span, a")[
                    0
                ]  # uzmi span ili a sta prvo dodje
                label = label_elem.text.lower()
                # if "director" not in label:
                #     continue
                names = [
                    a.text.strip()
                    for a in section.find_elements(By.TAG_NAME, "a")
                    if a.text.strip()
                ]
                # print(label)
                # print(names)
                if "director" in label:
                    for name in names:
                        cur.execute(
                            """
                                SELECT id FROM directors WHERE name=%s
                            """,
                            (name,),
                        )
                        result = cur.fetchone()
                        if not result:
                            cur.execute(
                                """
                                    INSERT INTO directors (name)
                                    VALUES (%s) RETURNING id
                                """,
                                (name,),
                            )
                            director_id = cur.fetchone()[0]
                        else:
                            director_id = result[0]
                        cur.execute(
                            """
                                INSERT INTO movie_director (movie_id, director_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING
                            """,
                            (movie_id, director_id),
                        )
                        # print(f" Direktor {movie_id} {director_id}")
                elif "writer" in label:
                    for name in names:
                        cur.execute(
                            """
                                SELECT id FROM writers WHERE name=%s
                            """,
                            (name,),
                        )
                        result = cur.fetchone()
                        if not result:
                            cur.execute(
                                """
                                    INSERT INTO writers (name)
                                    VALUES (%s) RETURNING id
                                """,
                                (name,),
                            )
                            writer_id = cur.fetchone()[0]
                        else:
                            writer_id = result[0]
                        cur.execute(
                            """
                                INSERT INTO movie_writer (movie_id, writer_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING
                            """,
                            (movie_id, writer_id),
                        )
                        # print(f"Pisac {movie_id} {writer_id}")

                if "star" in label:
                    full_cast_link = driver.find_element(
                        By.CSS_SELECTOR, "a[aria-label='See full cast and crew']"
                    ).get_attribute("href")
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[2])
                    print(full_cast_link)
                    driver.get(full_cast_link)
                    time.sleep(1)

                    casts = driver.find_elements(
                        By.CSS_SELECTOR,
                        'div[data-testid="sub-section-cast"] li.full-credits-page-list-item',
                    )
                    # print(casts)

                    for i, cast in enumerate(casts):
                        if i >= 10:
                            break
                        actor_link = cast.find_element(
                            By.CSS_SELECTOR, "a.name-credits--title-text"
                        )
                        actor_name = actor_link.text.strip()
                        print(actor_name)
                        if not actor_name:
                            continue

                        cur.execute(
                            """
                                SELECT id FROM actors WHERE name=%s
                            """,
                            (actor_name,),
                        )
                        result = cur.fetchone()
                        if not result:
                            cur.execute(
                                """
                                    INSERT INTO actors (name)
                                    VALUES (%s) RETURNING id
                                """,
                                (actor_name,),
                            )
                            actor_id = cur.fetchone()[0]
                        else:
                            actor_id = result[0]
                        cur.execute(
                            """
                                INSERT INTO movie_actor (movie_id, actor_id)
                                VALUES (%s, %s)
                                ON CONFLICT DO NOTHING
                            """,
                            (movie_id, actor_id),
                        )
                    print(f"{actor_name} {actor_id} {movie_id}")

                elif "director" or "writer" or "star" not in label:
                    continue

            except Exception as e:
                print(f"Greska unutra : {e}")
                break

        driver.close()  # zatvori taj novi tab
        driver.switch_to.window(driver.window_handles[0])  # vrati se na glavnu
        time.sleep(1)

    except Exception as er:
        import traceback

        print("Doslo je do greške:")
        traceback.print_exc()


conn.commit()
cur.close()
close_db_connection(conn)
driver.quit()
