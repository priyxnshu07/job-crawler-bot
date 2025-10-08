Job Crawler Bot 🤖
This project is a job aggregator and search engine that scrapes job listings from various portals and centralizes them into a single, searchable dashboard. The goal is to provide users with a streamlined way to find job openings that match their skills and preferences.

✨ Key Features
Based on the project plan, the key features are:

Multi-Site Scraping: Collects job data from multiple online portals.

Centralized Database: Stores all job listings in a local SQLite database.

Personalized Filtering: (Future Goal) Allows users to upload a resume to get personalized job matches.

Advanced Search: Users can search for jobs by title, company, or location.

Direct Apply Links: Provides direct links to the original job postings.

🛠️ Technology Stack
Backend: Python, Flask

Scraping: Requests, BeautifulSoup

Database: SQLite

Frontend: HTML, CSS, JavaScript

🚀 Getting Started
Follow these instructions to get a local copy up and running.

Prerequisites
Python 3.x

Pip

Installation & Setup
Clone the repository:

git clone <your-repository-url>

Navigate to the project directory:

cd jobcrawlerprototype-copy

Create and activate a virtual environment:

# Create
python -m venv venv
# Activate (macOS/Linux)
source venv/bin/activate
# Activate (Windows)
.\venv\Scripts\activate

Install the required packages:

pip install -r requirements.txt

Set up the database:

python database_setup.py

Run the scraper to populate the database:

python scraper.py

Run the Flask application:

flask run

Open your browser and navigate to http://127.0.0.1:5000.