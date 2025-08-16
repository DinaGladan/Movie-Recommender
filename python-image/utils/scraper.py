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
import json
import traceback
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from utils.db import get_db_connection, close_db_connection

TMDB_API_KEY = (
    "a5912e9d93f3ab3d10f2b48de0f2dc91"  # registracijom u tmdb daju besplatni api kljuc
)

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
conn = get_db_connection()
cur = conn.cursor()


def scrape_tmdb(tmdb_id):
    """Uzmi podatke s TMDB API-ja"""
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
    r = requests.get(url)
    if r.status_code != 200:
        return {}
    data = r.json()
    return {
        "tmdb_id": tmdb_id,
        "tmdb_audience_rating": data.get("vote_average"),
        "popularity": data.get("popularity"),
        "vote_count_tmdb": data.get("vote_count"),
        "adult": data.get("adult"),
        "original_language": data.get("original_language"),
        "release_date": data.get("release_date"),
        "countries": ", ".join(
            [c["name"] for c in data.get("production_countries", [])]
        ),
        "studio": (
            data["production_companies"][0]["name"]
            if data.get("production_companies")
            else None
        ),
    }


def scrape_rottentomatoes(rt_url):
    """Uzmi critic i audience score s RottenTomatoes"""
    driver.get(rt_url)
    time.sleep(2)
    try:
        critic = driver.find_element(By.CSS_SELECTOR, "score-board").get_attribute(
            "tomatometerscore"
        )
    except:
        critic = None
    try:
        audience = driver.find_element(By.CSS_SELECTOR, "score-board").get_attribute(
            "audiencescore"
        )
    except:
        audience = None
    return {
        "rt_critic_rating": critic,
        "rt_audience_rating": audience,
    }


def scrape_letterboxd(lb_url):
    """Uzmi user rating s Letterboxda"""
    driver.get(lb_url)
    time.sleep(2)
    try:
        rating = driver.find_element(By.CSS_SELECTOR, "span.average-rating").text
    except:
        rating = None
    return {"user_rating": rating}


def scrape_imdb(imdb_url, imdb_id):
    """Izvuci IMDb podatke kao do sad + dodaci"""
    driver.get(imdb_url)
    time.sleep(2)
    data = {"imdb_id": imdb_id}

    try:
        data["duration"] = driver.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-techspec_runtime'] div"
        ).text
    except:
        data["duration"] = None

    try:
        data["rating"] = driver.find_element(
            By.CSS_SELECTOR,
            "div[data-testid='hero-rating-bar__aggregate-rating__score'] span",
        ).text
    except:
        data["rating"] = None

    try:
        countries = driver.find_elements(
            By.XPATH, "//li[@data-testid='title-details-origin']//a"
        )
        data["countries"] = (
            ", ".join([c.text for c in countries]) if countries else None
        )
    except:
        data["countries"] = None

    try:
        studio = driver.find_element(
            By.XPATH, "//li[@data-testid='title-details-companies']//a"
        ).text
        data["studio"] = studio
    except:
        data["studio"] = None

    return data


def scrape_movie(movie_link, tmdb_url=None, rt_url=None, lb_url=None):
    try:
        main_window = driver.current_window_handle
        driver.execute_script("window.open('');")  # otvori novi prozor
        new_window = [
            window for window in driver.window_handles if window != main_window
        ][0]
        driver.switch_to.window(new_window)  # prebaci se na njega
        driver.get(movie_link)  # otvori stranicu filma u njemu
        time.sleep(2)
        try:
            title = driver.find_element(
                By.CSS_SELECTOR, "span[data-testid='hero__primary-text']"
            ).text
        except:
            title = "Unknown"

        try:
            year = driver.find_element(By.CSS_SELECTOR, "a[href*='releaseinfo']").text
        except:
            year = "Unknown"

        try:
            duration = driver.find_element(
                By.CSS_SELECTOR, "li[data-testid='title-techspec_runtime'] div"
            ).text
        except:
            duration = "Unknown"

        try:
            rating = driver.find_element(
                By.CSS_SELECTOR,
                "div[data-testid='hero-rating-bar__aggregate-rating__score'] span",
            ).text
        except:
            rating = "Unknown"

        # ako podatak ne postoji
        # find_element baca gresku seleniumu
        # find_elements vraca praznu listu
        rating_element = driver.find_elements(
            By.XPATH,
            "//li[@class='ipc-inline-list__item']/a[contains(@href, 'parental')]",
        )
        if rating_element:
            content_rating = rating_element[0].text.strip()
        else:
            content_rating = "None"
        time.sleep(1)
        print(content_rating)

        users_reviews = driver.find_elements(
            By.XPATH,
            "//span[@class='label' and contains(text(), 'User reviews')]/preceding-sibling::span[@class='score']",
        )
        if users_reviews:
            number_of_users_reviews = users_reviews[0].text.strip()
        else:
            number_of_users_reviews = "None"
        print(f"Number of users reviews: {number_of_users_reviews}")
        time.sleep(1)

        critic_reviews = driver.find_elements(
            By.XPATH,
            "//span[@class='label' and contains(text(), 'Critic reviews')]/preceding-sibling::span[@class='score']",
        )
        if critic_reviews:
            number_of_critic_reviews = critic_reviews[0].text.strip()
        else:
            number_of_critic_reviews = "None"
        print(f"Number of critic reviews: {number_of_critic_reviews}")
        time.sleep(1)

        oscar_nominations_and_awards = driver.find_elements(
            By.XPATH,
            "//li[@data-testid='award_information']//a[contains(@href, 'awards')]",
        )
        if oscar_nominations_and_awards:
            text = oscar_nominations_and_awards[0].text.strip()
            nominations_and_awards = text if text else "No Oscars"
        else:
            nominations_and_awards = "No Oscars"
        print(f"Nominations and awards: {nominations_and_awards}")
        time.sleep(1)
        try:
            # Provjeri postoji li već taj film
            cur.execute(
                """
                        SELECT id FROM movies
                        WHERE title = %s AND year = %s
                    """,
                (title, year),
            )
            movie_result = cur.fetchone()

            if movie_result is None:
                # ne postoji pa ga unesi
                # mislim da se ode lomi
                cur.execute(
                    """
                        INSERT INTO movies (title, year, duration, rating, content_rating, number_of_users_reviews, number_of_critic_reviews, nominations_and_awards)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                    """,
                    (
                        title,
                        year,
                        duration,
                        rating,
                        content_rating,
                        number_of_users_reviews,
                        number_of_critic_reviews,
                        nominations_and_awards,
                    ),
                )
                movie_id = cur.fetchone()[0]
                conn.commit()
                time.sleep(1)

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
                    time.sleep(1)

                sections = driver.find_elements(
                    By.CSS_SELECTOR, "li.ipc-metadata-list__item"
                )
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

                        elif "star" in label:
                            full_cast_link = driver.find_element(
                                By.CSS_SELECTOR,
                                "a[aria-label='See full cast and crew']",
                            ).get_attribute("href")
                            driver.execute_script("window.open('');")
                            cast_window = [
                                window
                                for window in driver.window_handles
                                if window not in [main_window, new_window]
                            ][0]
                            driver.switch_to.window(cast_window)
                            # print(full_cast_link)
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
                            driver.close()  # zatvori taj novi tab
                            driver.switch_to.window(new_window)  # vrati se na glavnu
                            time.sleep(1)
                        elif "director" or "writer" or "star" not in label:
                            continue

                    except Exception as e:
                        print(f"Greska unutra : {e}")
                        if len(driver.window_handles) > 2:
                            driver.close()
                            driver.switch_to.window(new_window)
                        continue
                conn.commit()
                extra_data = {}
                if tmdb_url:
                    match = re.search(r"/movie/(\d+)", tmdb_url)
                    if match:
                        tmdb_id = match.group(1)
                        extra_data.update(scrape_tmdb(tmdb_id))
                        extra_data["tmdb_id"] = tmdb_id

                if rt_url:
                    extra_data.update(scrape_rottentomatoes(rt_url))
                if lb_url:
                    extra_data.update(scrape_letterboxd(lb_url))

                if extra_data:
                    cur.execute(
                        """
                        UPDATE movies
                        SET tmdb_id=%s,
                            tmdb_audience_rating=%s,
                            popularity=%s,
                            vote_count_tmdb=%s,
                            adult=%s,
                            original_language=%s,
                            release_date=%s,
                            countries=%s,
                            studio=%s,
                            rt_critic_rating=%s,
                            rt_audience_rating=%s,
                            user_rating=%s
                        WHERE id=%s
                    """,
                        (
                            extra_data.get("tmdb_id"),
                            extra_data.get("tmdb_audience_rating"),
                            extra_data.get("popularity"),
                            extra_data.get("vote_count_tmdb"),
                            extra_data.get("adult"),
                            extra_data.get("original_language"),
                            extra_data.get("release_date"),
                            extra_data.get("countries"),
                            extra_data.get("studio"),
                            extra_data.get("rt_critic_rating"),
                            extra_data.get("rt_audience_rating"),
                            extra_data.get("user_rating"),
                            movie_id,
                        ),
                    )
                    conn.commit()
            else:
                print(f"Movie already exists: {title} ({year})")
        except Exception as err:
            print(f"Greska {err}")
            traceback.print_exc()
            conn.rollback()

        driver.close()
        driver.switch_to.window(main_window)
        return True
    except Exception as er:
        print(f"Doslo je do greške: {er}")
        traceback.print_exc()
        try:
            if len(driver.window_handles) > 1:
                for handle in driver.window_handles[1:]:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return False


print("Scraping top 250")
url = "https://www.imdb.com/chart/top/"
driver.get(url)
print("Page title:", driver.title)

movies = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
# print(f"Br pronadjenih {len(movies)}")
for idx, movie in enumerate(movies):

    # if 218 < idx or idx < 214:
    #     continue

    print(f"\n Obrada {idx+1}. filma")
    try:
        movie_link = movie.find_element(By.TAG_NAME, "a").get_attribute("href")
        # print(f"{movie_link}")
        scrape_movie(movie_link)
    except Exception as e:
        print(f"Error processing Top 250 movie: {e}")
        continue

print("\nScraping from json")
with open("imdb_ids.json", "r") as f:
    imdb_ids = json.load(f)

for idx, imdb_id in enumerate(imdb_ids):
    print(f"\nProcessing {idx+1}.")
    movie_url = f"https://www.imdb.com/title/{imdb_id}/"
    scrape_movie(movie_url)
    time.sleep(2)

conn.commit()
cur.close()
close_db_connection(conn)
driver.quit()
