"""
Wellfound (ex-AngelList) Scraper.

Wellfound ek React/Next.js app hai - jobs data page load ke baad JS se render
hota hai, isliye simple requests+BeautifulSoup se seedha HTML se job cards
nahi milte. Trick: Next.js apps aksar page ke <script id="__NEXT_DATA__">
tag me poora initial JSON state chhupa dete hain - hum wahi parse karte hain.

RELIABILITY WARNING: Ye sabse fragile scraper hai in charo me se, kyunki
Wellfound apna internal JSON structure kabhi bhi change kar sakta hai.
Agar ye 0 results de, matlab structure change ho gaya - tab is file ko
update karna padega ya Selenium based approach pe switch karna padega.
"""
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from config import HEADERS, REQUEST_TIMEOUT, RESULTS_PER_SEARCH

BASE_URL = "https://wellfound.com/jobs"


def _find_jobs_in_json(obj, found=None):
    """Recursively search the Next.js JSON blob for anything that looks like a job listing."""
    if found is None:
        found = []
    if isinstance(obj, dict):
        if {"title"}.issubset(obj.keys()) and ("company" in obj or "companyName" in obj) and (
            "slug" in obj or "id" in obj
        ):
            found.append(obj)
        for v in obj.values():
            _find_jobs_in_json(v, found)
    elif isinstance(obj, list):
        for item in obj:
            _find_jobs_in_json(item, found)
    return found


def scrape(keyword: str, location: str) -> list:
    jobs = []
    url = f"{BASE_URL}?keywords={quote_plus(keyword)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            print(f"[Wellfound] '{keyword}' -> HTTP {resp.status_code}, skipping")
            return jobs

        soup = BeautifulSoup(resp.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag or not script_tag.string:
            print(f"[Wellfound] '{keyword}' -> no __NEXT_DATA__ found, page structure may have changed")
            return jobs

        data = json.loads(script_tag.string)
        raw_jobs = _find_jobs_in_json(data)

        for job in raw_jobs[:RESULTS_PER_SEARCH]:
            slug = job.get("slug") or job.get("id")
            if not slug:
                continue
            link = f"https://wellfound.com/jobs/{slug}" if not str(slug).startswith("http") else slug

            company = job.get("company")
            company_name = company.get("name") if isinstance(company, dict) else job.get("companyName", "N/A")

            jobs.append({
                "platform": "Wellfound",
                "title": job.get("title", "N/A"),
                "company": company_name or "N/A",
                "location": job.get("locationNames", ["N/A"])[0] if isinstance(job.get("locationNames"), list) else "N/A",
                "link": link,
                "posted": job.get("createdAt", "N/A"),
            })

    except Exception as e:
        print(f"[Wellfound] Error for '{keyword}': {e}")

    time.sleep(1.5)
    return jobs


def scrape_all(keywords: list, location: str) -> list:
    all_jobs = []
    for kw in keywords:
        all_jobs.extend(scrape(kw, location))
    return all_jobs
