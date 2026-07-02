"""
Naukri.com Scraper - unke internal search JSON API (jobapi/v3/search) ko
directly hit karta hai jo unki website khud use karti hai. Login ki zaroorat nahi.

Note: Naukri kabhi kabhi extra headers (appid/systemid) require karta hai.
Agar future me API response format/headers change ho jaaye to sirf ye file
update karni padegi, baaki sab as-is chalega.
"""
import time
import requests

from config import HEADERS, REQUEST_TIMEOUT, RESULTS_PER_SEARCH

BASE_URL = "https://www.naukri.com/jobapi/v3/search"

NAUKRI_HEADERS = {
    **HEADERS,
    "Accept": "application/json",
    "appid": "109",
    "systemid": "Naukri",
    "Referer": "https://www.naukri.com/",
}


def scrape(keyword: str, location: str) -> list:
    jobs = []
    params = {
        "noOfResults": RESULTS_PER_SEARCH,
        "urlType": "search_by_keyword",
        "searchType": "adv",
        "keyword": keyword,
        "location": location,
        "k": keyword,
        "l": location,
        "seoKey": f"{keyword.lower().replace(' ', '-')}-jobs",
        "src": "jobsearchDesk",
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=NAUKRI_HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            print(f"[Naukri] '{keyword}' -> HTTP {resp.status_code}, skipping")
            return jobs

        data = resp.json()
        job_details = data.get("jobDetails", [])

        for job in job_details[:RESULTS_PER_SEARCH]:
            link = job.get("jdURL") or job.get("staticUrl")
            if link and link.startswith("/"):
                link = "https://www.naukri.com" + link
            if not link:
                continue

            jobs.append({
                "platform": "Naukri",
                "title": job.get("title", "N/A"),
                "company": job.get("companyName", "N/A"),
                "location": job.get("placeholders", [{}])[0].get("label", "N/A")
                if job.get("placeholders") else job.get("location", "N/A"),
                "link": link,
                "posted": job.get("footerPlaceholderLabel", "N/A"),
            })

    except Exception as e:
        print(f"[Naukri] Error for '{keyword}': {e}")

    time.sleep(1.5)
    return jobs


def scrape_all(keywords: list, location: str) -> list:
    all_jobs = []
    for kw in keywords:
        all_jobs.extend(scrape(kw, location))
    return all_jobs
