import json

import requests
import sys
from episode import Episode
from bs4 import BeautifulSoup

from person import PersonOrChain
from rating import Rating

base_url = "https://doughboys.fandom.com"
episodes = "/wiki/Episodes"

rss_feed = "https://rss.art19.com/doughboys"

current_scores = None


def scrub_string(text):
    return ' '.join(text.split())


# finding generic episode info inside article
def find_gen_info(article, attr_val):
    gross_obj = article.find('div', {"data-source": attr_val})
    value = gross_obj.find('div', {"class": "pi-data-value pi-font"}).text
    return value


def get_duration(number):
    html = requests.get(rss_feed).text
    soup = BeautifulSoup(html, 'html.parser')
    this_ep = soup.find('itunes:episode', text=number)
    duration = this_ep.parent.find('itunes:duration').text
    return get_sec(duration)


def get_sec(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def get_latest_rating(episode_num):
    fb = requests.get("https://doughpedia.firebaseio.com/ratings.json")
    ratings = list(fb.json().items())
    highest_value = 0
    episode = ""
    for rating in ratings:
        num = int(rating[0].strip("_"))
        if num > highest_value:
            highest_value = num
            episode = int(rating[1]['episode'].strip("_"))

    print(highest_value)
    print(episode)

    #if episode + 1 != int(episode_num):
    #    print("not doing the next episode !!")
    #    return None
    return highest_value


# retrieves fork rating for a given episode
def get_fork_ratings(url):
    html_contents = requests.get(url).text
    soup = BeautifulSoup(html_contents, 'html.parser')
    article = soup.find('article')

    #fork_table = article.find('span', {"id": "Fork_rating"}).findNext('table', {"class": "article-table"})
    fork_table = article.find('table', {"class": "article-table"})

    fork_table_rows = fork_table.find_all('tr')[1:]
    last_row = fork_table_rows[-1]
    last_row_title = last_row.find('td')
    #if "shared" in last_row_title.text or "??" in last_row_title.text:
     #   fork_table_rows.pop(-1)
        #fork_table_rows.pop(-1)

    fork_ratings = {}

    for row in fork_table_rows:
        entries = row.find_all('td')
        person = scrub_string(entries[0].text)
        if "shared" in person:
            continue
        rating = scrub_string(entries[-1].text).split(" ")[0]
        if rating is "":
            continue
        fork_ratings[person] = rating

    return fork_ratings


def get_synopsis(url):
    html_contents = requests.get(url).text
    soup = BeautifulSoup(html_contents, 'html.parser')
    article = soup.find('article')
    return article.find('span', {"id": "Synopsis"}).findNext('p').text


def get_image(url):
    html_contents = requests.get(url).text
    soup = BeautifulSoup(html_contents, 'html.parser')
    article = soup.find('article')

    image_obj = article.find('figure', {"class": "pi-item pi-image"})
    return image_obj.find('a').attrs['href'].split("/revision/")[0]


# returns list of all regular, numbered episodes
def get_episode_list():
    html_contents = requests.get(base_url + episodes).text
    soup = BeautifulSoup(html_contents, 'html.parser')
    ep_table = soup.find('table').find_all('tr')[1:]
    episode_list = []
    for row in ep_table:
        columns = row.find_all('td')
        number = scrub_string(columns[0].text)
        avg_score = scrub_string(columns[2].text)
        # filter out double & tournament episodes
        if number.isdigit() and avg_score.replace('.', '', 1).isdigit():
            a_tag = columns[1].find('a')
            title = scrub_string(a_tag.text)
            print("Fetching Episode " + number + " - " + title)
            href = scrub_string(a_tag.attrs['href'])
            date = scrub_string(columns[3].text)
            fork_ratings = get_fork_ratings(base_url + href)
            episode_list.append(Episode(title, number, href, date, fork_ratings))
    return episode_list


def get_episode(number, new_rating):
    html_contents = requests.get(base_url + episodes).text
    soup = BeautifulSoup(html_contents, 'html.parser')
    ep_table = soup.find('table').find_all('tr')[1:]
    for entry in ep_table:
        columns = entry.find_all('td')
        numFound = scrub_string(columns[0].text)
        avg_score = scrub_string(columns[2].text)
        if numFound == str(number):
            if not numFound.isdigit() and not avg_score.replace('.', '', 1).isdigit():
                return None
            a_tag = entry.find_all('td')[1].find('a')
            title = scrub_string(a_tag.text).replace("Rockaroundtheclockdoughberfest: ", "")
            title = title.replace("Tropical Freeze: ", "")
            print("Fetching Episode " + numFound + " - " + title)
            href = scrub_string(a_tag.attrs['href'])
            date = scrub_string(columns[3].text)
            fork_ratings = get_fork_ratings(base_url + href)
            global current_scores
            current_scores = fork_ratings
            image = scrub_string(get_image(base_url + href))
            synopsis = scrub_string(get_synopsis(base_url + href))
            duration = get_duration(numFound.strip())
            current_ep = Episode(title, numFound, date, duration, fork_ratings, image, new_rating, synopsis)
            print(json.dumps(current_ep.__dict__, indent=4))

            return current_ep


def get_ratings(episode, next_rating_number):
    global current_scores
    ratings = {}
    for person, score in current_scores.items():
        new_rating = Rating(episode.number, episode.date, episode.epoch, person, episode.restaurant, score)
        ratings["_" + str(next_rating_number)] = new_rating
        next_rating_number += 1

    return ratings


def get_people(episode):
    people = []
    for person in (episode.people.keys()):
        new_person = PersonOrChain()
        print(person)


def check_person_existence(name):
    response = requests.get("https://doughpedia.firebaseio.com/people/" + name + ".json")
    if response.json() is None:
        return False
    else:
        return True


def check_restaurant_existence(name):
    response = requests.get("https://doughpedia.firebaseio.com/restaurants/" + name + ".json")
    if response.json() is None:
        return False
    else:
        return True


def set_flag_true(url):
    requests.put(url, data="true")


def add_episode_number(episode):
    body = json.dumps(episode.__dict__)
    requests.put("https://doughpedia.firebaseio.com/episodes/_" + episode.number + ".json", data=body)


def make_put_call(url, pojo):
    body = json.dumps(pojo.__dict__)
    requests.put(url, data=body)


if __name__ == "__main__":
    # getting single episode
    if sys.argv[1] == "test":
        get_latest_rating("5")
        exit()

    if sys.argv[1] is not None:
        testing = False
        for num in range(276, 280):
            latest_rating = get_latest_rating(num)
            if latest_rating is None:
                print("numbering is off")
                exit(0)
            next_rating_number = latest_rating + 1

            # add episode obj
            new_episode = get_episode(num, next_rating_number)
            if new_episode is None:
                print("tourney or DD called")
                exit()
            if not testing:
                make_put_call("https://doughpedia.firebaseio.com/episodes/_" + str(new_episode.number) + ".json",
                              new_episode)

            # add ratings and update them for each episode + person
            new_ratings = get_ratings(new_episode, next_rating_number)
            count = 0
            for index, rating in new_ratings.items():
                print(index)
                print(json.dumps(rating.__dict__, indent=4))

                rating_url = "https://doughpedia.firebaseio.com/ratings/" + index + ".json"
                print(rating_url)
                if not testing:
                    make_put_call(rating_url, rating)

                # update person rating
                person_url = "https://doughpedia.firebaseio.com/people/" + rating.person + "/ratings/" + index + ".json"
                print(person_url)
                if not testing:
                    set_flag_true(person_url)

                # update person appearance
                person_ep_url = "https://doughpedia.firebaseio.com/people/" + rating.person + "/episodes/_" + str(
                    new_episode.number) + ".json"
                print(person_ep_url)
                if not testing:
                    set_flag_true(person_ep_url)

                # update chain rating
                chain_url = "https://doughpedia.firebaseio.com/restaurants/" + rating.restaurant + "/ratings/" + index + ".json"
                print(chain_url)
                if not testing:
                    set_flag_true(chain_url)

                # update chain appearance
                chain_ep_url = "https://doughpedia.firebaseio.com/restaurants/" + rating.restaurant + "/episodes/_" + str(
                    new_episode.number) + ".json"
                print(chain_ep_url)
                if not testing:
                    set_flag_true(chain_ep_url)

        # set_flag_true("https://doughpedia.firebaseio.com/people/Demi Moore/ratings/_8.json")

        # for rating_num in new_episode.ratings.keys():
        #    print(rating_num)

        # people = get_people(new_episode)
        # chains = get_chains(new_episode)

    else:
        for ep in get_episode_list():
            print("=====================")
            print(str(ep))
    # get_episode(base_url+last_ep)
