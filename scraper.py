import requests
from episode import Episode
from bs4 import BeautifulSoup

base_url = "https://doughboys.fandom.com"
episodes = "/wiki/Episodes"


def scrub_string(text):
    return ' '.join(text.split())


# finding generic episode info inside article
def find_gen_info(article, attr_val):
    gross_obj = article.find('div', {"data-source": attr_val})
    value = gross_obj.find('div', {"class": "pi-data-value pi-font"}).text
    return value


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
        rating = scrub_string(entries[-1].text)
        fork_ratings[person] = rating

    return fork_ratings


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


if __name__ == "__main__":
    for ep in get_episode_list():
        print("=====================")
        print(str(ep))
    # get_episode(base_url+last_ep)