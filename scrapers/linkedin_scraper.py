"""
LinkedIn Scraper - uses LinkedIn's public "guest" job search endpoint.
Isme LOGIN ki zaroorat NAHI hai, isliye ye GitHub Actions pe safe chalta hai
(login wale Selenium scrapers LinkedIn account ko ban/restrict kar sakte hain
agar cloud server se baar baar login karoge - isliye jaanbujh kar avoid kiya).

Limitation: guest search sirf limited results deta hai (~25 per keyword) aur
kabhi kabhi LinkedIn structure change kar deta hai - agar 0 results aaye,
selectors check karne padenge.
"""
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from config import HEADERS, REQUEST_TIMEOUT, RESULTS_PER_SEARCH

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


def _parse_card(card):
    try:
        title_tag = card.find("h3", class_="base-search-card__title")
        company_tag = card.find("h4", class_="base-search-card__subtitle")
        location_tag = card.find("span", class_="job-search-card__location")
        link_tag = card.find("a", class_="base-card__full-link")
        time_tag = card.find("time")

        link = link_tag["href"].split("?")[0] if link_tag else None
        if not link:
            return None

        return {
            "platform": "LinkedIn",
            "title": title_tag.get_text(strip=True) if title_tag else "N/A",
            "company": company_tag.get_text(strip=True) if company_tag else "N/A",
            "location": location_tag.get_text(strip=True) if location_tag else "N/A",
            "link": link,
            "posted": time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else "N/A",
        }
    except Exception:
        return None


def scrape(keyword: str, location: str) -> list:
    """Search LinkedIn guest jobs API for a given keyword + location."""
    jobs = []
    params = {
        "keywords": keyword,
        "location": location,
        "start": 0,
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            print(f"[LinkedIn] '{keyword}' -> HTTP {resp.status_code}, skipping")
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")

        for card in cards[:RESULTS_PER_SEARCH]:
            parsed = _parse_card(card)
            if parsed:
                jobs.append(parsed)

    except Exception as e:
        print(f"[LinkedIn] Error for '{keyword}': {e}")

    time.sleep(1.5)  # polite delay
    return jobs


def scrape_all(keywords: list, location: str) -> list:
    all_jobs = []
    for kw in keywords:
        all_jobs.extend(scrape(kw, location))
    return all_jobs
