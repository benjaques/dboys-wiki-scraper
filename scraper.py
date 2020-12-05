import json

import requests
import sys
from episode import Episode
from bs4 import BeautifulSoup

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


def get_latest_rating():
    fb = requests.get("https://doughpedia.firebaseio.com/ratings.json")
    list_of_keys = list(fb.json().keys())
    last_key = list_of_keys[-1].strip("_")
    return int(last_key)


# retrieves fork rating for a given episode
def get_fork_ratings(url):
    html_contents = requests.get(url).text
    soup = BeautifulSoup(html_contents, 'html.parser')
    article = soup.find('article')

    fork_table = article.find('table', {"class": "article-table"})
    fork_table_rows = fork_table.find_all('tr')[1:]
    last_row = fork_table_rows[-1]
    last_row_title = last_row.find('td')
    if "shared" in last_row_title.text:
        fork_table_rows.pop(-1)

    fork_ratings = {}

    for row in fork_table_rows:
        entries = row.find_all('td')
        person = scrub_string(entries[0].text)
        rating = scrub_string(entries[-1].text).split(" ")[0]
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
        if numFound == str(number):
            a_tag = entry.find_all('td')[1].find('a')
            title = scrub_string(a_tag.text)
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

def get_ratings(episode):
    global current_scores
    ratings = {}
    print(current_scores)
    for obj in current_scores:
        print(obj)
        #print(score)

    return ratings



if __name__ == "__main__":
    if sys.argv[1] is not None:
        latest_rating = get_latest_rating()
        next_rating_number = latest_rating + 1
        new_episode = get_episode(sys.argv[1], next_rating_number)
        new_ratings = get_ratings(new_episode)
    else:
        for ep in get_episode_list():
            print("=====================")
            print(str(ep))
    # get_episode(base_url+last_ep)
