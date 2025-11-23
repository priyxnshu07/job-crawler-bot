# tasks.py
import requests
from bs4 import BeautifulSoup
import psycopg2
import psycopg2.extras
from config import DATABASE_CONFIG
import time
import random
from urllib.parse import urlencode, quote_plus
import re

# --- Helper Functions ---

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
    ]
    return random.choice(user_agents)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

# --- Scrapers ---

def scrape_indeed(query, location, max_jobs=10):
    """
    Scrapes real jobs from Indeed.com.
    """
    print(f"🔎 Scraping Indeed for '{query}' in '{location}'...")
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    params = {
        'q': query,
        'l': location,
        'sort': 'date',
        'limit': 50
    }
    
    jobs = []
    try:
        # Try Indian domain first for better results in India
        domain = "in.indeed.com" if "india" in location.lower() or "bangalore" in location.lower() or "delhi" in location.lower() else "www.indeed.com"
        url = f"https://{domain}/jobs"
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"⚠️ Indeed returned status {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Indeed changes classes often, try multiple selectors
        job_cards = soup.find_all('div', class_=lambda x: x and 'job_seen_beacon' in x)
        if not job_cards:
            job_cards = soup.find_all('td', class_='resultContent')
            
        print(f"ℹ️ Found {len(job_cards)} job cards on Indeed")
        
        for card in job_cards:
            try:
                # Title
                title_elem = card.find('h2', class_='jobTitle') or card.find('a', class_=lambda x: x and 'jobtitle' in x)
                title = title_elem.text.strip() if title_elem else "Unknown Title"
                
                # Company
                company_elem = card.find('span', class_='companyName') or card.find('span', attrs={'data-testid': 'company-name'})
                company = company_elem.text.strip() if company_elem else "Unknown Company"
                
                # Location
                loc_elem = card.find('div', class_='companyLocation') or card.find('div', attrs={'data-testid': 'text-location'})
                loc = loc_elem.text.strip() if loc_elem else location
                
                # Link
                link_elem = card.find('a', href=True)
                if link_elem and link_elem['href'].startswith('/'):
                    link = f"https://{domain}" + link_elem['href']
                elif link_elem:
                    link = link_elem['href']
                else:
                    link = "#"
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'apply_link': link,
                    'source': 'Indeed'
                })
                
                if len(jobs) >= max_jobs:
                    break
            except Exception as e:
                continue
            
    except Exception as e:
        print(f"❌ Error scraping Indeed: {e}")

    return jobs

def scrape_linkedin(query, location, max_jobs=10):
    """
    Scrapes public LinkedIn job search page.
    """
    print(f"🔎 Scraping LinkedIn for '{query}' in '{location}'...")
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    jobs = []
    try:
        # LinkedIn public jobs URL structure
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        params = {
            'keywords': query,
            'location': location,
            'start': 0
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ LinkedIn returned status {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('li')
        
        print(f"ℹ️ Found {len(job_cards)} job cards on LinkedIn")
        
        for card in job_cards:
            try:
                title_elem = card.find('h3', class_='base-search-card__title')
                title = clean_text(title_elem.text) if title_elem else "Unknown Title"
                
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                company = clean_text(company_elem.text) if company_elem else "Unknown Company"
                
                loc_elem = card.find('span', class_='job-search-card__location')
                loc = clean_text(loc_elem.text) if loc_elem else location
                
                link_elem = card.find('a', class_='base-card__full-link')
                link = link_elem['href'] if link_elem else "#"
                
                # Clean up tracking params from link
                if '?' in link:
                    link = link.split('?')[0]
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'apply_link': link,
                    'source': 'LinkedIn'
                })
                
                if len(jobs) >= max_jobs:
                    break
            except Exception:
                continue
                
    except Exception as e:
        print(f"❌ Error scraping LinkedIn: {e}")
        
    return jobs

def scrape_timesjobs(query, location, max_jobs=10):
    """
    Scrapes TimesJobs (good for India).
    """
    print(f"🔎 Scraping TimesJobs for '{query}' in '{location}'...")
    
    headers = {
        'User-Agent': get_random_user_agent()
    }
    
    jobs = []
    try:
        # TimesJobs search URL
        base_url = "https://www.timesjobs.com/candidate/job-search.html"
        params = {
            'searchType': 'personalizedSearch',
            'from': 'submit',
            'txtKeywords': query,
            'txtLocation': location
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_cards = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
        
        print(f"ℹ️ Found {len(job_cards)} job cards on TimesJobs")
        
        for card in job_cards:
            try:
                title_elem = card.find('h2').find('a')
                title = clean_text(title_elem.text) if title_elem else "Unknown Title"
                
                company_elem = card.find('h3', class_='joblist-comp-name')
                company = clean_text(company_elem.text) if company_elem else "Unknown Company"
                # Remove "(More Jobs)" text if present
                company = company.replace('(More Jobs)', '').strip()
                
                loc_elem = card.find('ul', class_='top-jd-dtl').find('span')
                loc = clean_text(loc_elem.text) if loc_elem else location
                
                link = title_elem['href'] if title_elem else "#"
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': loc,
                    'apply_link': link,
                    'source': 'TimesJobs'
                })
                
                if len(jobs) >= max_jobs:
                    break
            except Exception:
                continue
                
    except Exception as e:
        print(f"❌ Error scraping TimesJobs: {e}")
        
    return jobs

def scrape_jobs(query, location, max_jobs=20):
    """
    Aggregator function that scrapes jobs from multiple platforms.
    """
    all_jobs = []
    
    # 1. Scrape Indeed
    try:
        indeed_jobs = scrape_indeed(query, location, max_jobs=10)
        if indeed_jobs:
            all_jobs.extend(indeed_jobs)
    except Exception as e:
        print(f"Error in Indeed scraper: {e}")
        
    # 2. Scrape LinkedIn
    try:
        # Add small delay
        time.sleep(random.uniform(1, 3))
        linkedin_jobs = scrape_linkedin(query, location, max_jobs=10)
        if linkedin_jobs:
            all_jobs.extend(linkedin_jobs)
    except Exception as e:
        print(f"Error in LinkedIn scraper: {e}")
        
    # 3. Scrape TimesJobs
    try:
        # Add small delay
        time.sleep(random.uniform(1, 3))
        times_jobs = scrape_timesjobs(query, location, max_jobs=10)
        if times_jobs:
            all_jobs.extend(times_jobs)
    except Exception as e:
        print(f"Error in TimesJobs scraper: {e}")
        
    # Deduplicate based on link
    unique_jobs = []
    seen_links = set()
    
    for job in all_jobs:
        if job['apply_link'] not in seen_links:
            seen_links.add(job['apply_link'])
            unique_jobs.append(job)
            
    # Shuffle to mix sources
    random.shuffle(unique_jobs)
    
    return unique_jobs[:max_jobs]


def build_search_queries_from_skills(skills):
    """
    Build search queries based on user skills.
    """
    if not skills:
        return []
    
    # Basic logic to combine top skills into queries
    # Take top 3 skills
    top_skills = skills[:3]
    queries = []
    
    # Single skill queries
    for skill in top_skills:
        queries.append(f"{skill} developer")
        queries.append(f"{skill} engineer")
        
    # Combined queries if multiple skills
    if len(top_skills) >= 2:
        queries.append(f"{top_skills[0]} {top_skills[1]} developer")
        
    return list(set(queries))[:5]
