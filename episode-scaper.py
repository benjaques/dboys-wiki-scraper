from bs4 import BeautifulSoup

base_url = "https://doughboys.fandom.com/"
first_ep = "wiki/Chili’s_with_Eva_Anderson"
# read initial html from url

# used for local testing...
file_path = "res/episode-page.html"
#file_path = "res/multiple-guests.html"

html_contents = open(file_path).read()
soup = BeautifulSoup(html_contents, 'html.parser')

articles = soup.find('article')
gross_title = articles.find('h2').text
title = ' '.join(gross_title.split())
print(title)


# finding generic episode info
def findgeninfo(attr_val):
    gross_obj = articles.find('div', {"data-source": attr_val})
    value = gross_obj.find('div', {"class": "pi-data-value pi-font"}).text
    return value


number = findgeninfo("ep_number")
print('Episode ' + number)
date = findgeninfo("release_date")
print('Released ' + date)
guests = findgeninfo("guest")
print('Guests: ' + guests)

fork_table = articles.find('table', {"class": "article-table"})
fork_table_rows = fork_table.find_all('tr')[1:]
last_row = fork_table_rows[-1]
last_row_title = last_row.find('td')
if "shared" in last_row_title.text:
    fork_table_rows.pop(-1)

print("\n-----Fork Ratings-----")
for row in fork_table_rows:
    entries = row.find_all('td')
    person = ' '.join(entries[0].text.split())
    rating = ' '.join(entries[-1].text.split())
    print(person + ": " + rating)
