# scraper.py
import requests
from bs4 import BeautifulSoup
import sqlite3

def scrape_jobs():
    url = "https://realpython.github.io/fake-jobs/"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    job_cards = soup.find_all("div", class_="card-content")

    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    for card in job_cards:
        title = card.find("h2", class_="title").text.strip()
        company = card.find("h3", class_="company").text.strip()
        location = card.find("p", class_="location").text.strip()
        link_tag = card.find_all("a")[-1]
        apply_link = link_tag['href']

        cursor.execute('''
        INSERT OR IGNORE INTO jobs (title, company, location, apply_link)
        VALUES (?, ?, ?, ?)
        ''', (title, company, location, apply_link))

        print(f"Saved job: {title} at {company}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    scrape_jobs()