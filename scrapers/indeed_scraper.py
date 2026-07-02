"""
Indeed Scraper - public search results page (in.indeed.com) scrape karta hai.

IMPORTANT: Indeed sabse zyada bot-protection wala site hai in charo me se.
Kabhi kabhi captcha/block aa sakta hai, especially cloud IPs (GitHub Actions)
se. Agar consistently 0 results ya 403 aaye, to iska matlab Indeed ne
block kar diya - us case me ye scraper skip ho jayega but baaki 3 platforms
(LinkedIn, Naukri, Wellfound) chalte rahenge, pura pipeline nahi rukega.
"""
import time
import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_TIMEOUT, RESULTS_PER_SEARCH, MAX_JOB_AGE_DAYS

BASE_URL = "https://in.indeed.com/jobs"


def scrape(keyword: str, location: str) -> list:
    jobs = []
    params = {
        "q": keyword,
        "l": location,
        "fromage": MAX_JOB_AGE_DAYS,
        "sort": "date",
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            print(f"[Indeed] '{keyword}' -> HTTP {resp.status_code}, skipping (possible block)")
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="job_seen_beacon") or soup.find_all("div", class_="cardOutline")

        for card in cards[:RESULTS_PER_SEARCH]:
            title_tag = card.find("h2", class_="jobTitle")
            company_tag = card.find("span", {"data-testid": "company-name"}) or card.find("span", class_="companyName")
            location_tag = card.find("div", {"data-testid": "text-location"}) or card.find("div", class_="companyLocation")
            link_tag = title_tag.find("a") if title_tag else None
            date_tag = card.find("span", class_="date")

            if not link_tag or not link_tag.has_attr("href"):
                continue

            href = link_tag["href"]
            link = "https://in.indeed.com" + href if href.startswith("/") else href

            jobs.append({
                "platform": "Indeed",
                "title": title_tag.get_text(strip=True) if title_tag else "N/A",
                "company": company_tag.get_text(strip=True) if company_tag else "N/A",
                "location": location_tag.get_text(strip=True) if location_tag else "N/A",
                "link": link,
                "posted": date_tag.get_text(strip=True) if date_tag else "N/A",
            })

    except Exception as e:
        print(f"[Indeed] Error for '{keyword}': {e}")

    time.sleep(1.5)
    return jobs


def scrape_all(keywords: list, location: str) -> list:
    all_jobs = []
    for kw in keywords:
        all_jobs.extend(scrape(kw, location))
    return all_jobs
