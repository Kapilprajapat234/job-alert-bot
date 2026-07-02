"""
Job Alert Bot - Main Runner

Ye script:
1. Config me enabled saare platforms (LinkedIn, Naukri, Indeed, Wellfound) scrape karta hai
2. seen_jobs.csv se compare karke sirf NAYE jobs nikalta hai (link = unique key)
3. seen_jobs.csv update karta hai (sab jobs ka permanent record)
4. new_jobs_latest_run.csv banata hai (sirf isi run ke naye jobs)
5. dashboard (docs/index.html) regenerate karta hai

Run: python main.py
"""
import csv
import os
from datetime import datetime

import config
from scrapers import linkedin_scraper, naukri_scraper, indeed_scraper, wellfound_scraper
from dashboard_generator import generate_dashboard

CSV_FIELDS = ["platform", "title", "company", "location", "link", "posted", "first_seen"]

SCRAPER_MAP = {
    "linkedin": linkedin_scraper,
    "naukri": naukri_scraper,
    "indeed": indeed_scraper,
    "wellfound": wellfound_scraper,
}


def load_seen_links(path: str) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return {row["link"] for row in reader if row.get("link")}


def append_rows(path: str, rows: list, write_header_if_missing: bool = True):
    file_exists = os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists and write_header_if_missing:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def overwrite_rows(path: str, rows: list):
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run():
    print(f"=== Job Alert Bot run started: {datetime.now().isoformat()} ===")

    all_scraped = []
    for platform, enabled in config.PLATFORMS.items():
        if not enabled:
            continue
        scraper = SCRAPER_MAP[platform]
        print(f"--- Scraping {platform} ---")
        results = scraper.scrape_all(config.KEYWORDS, config.LOCATION)
        print(f"    {platform}: {len(results)} listings found (raw, before dedupe)")
        all_scraped.extend(results)

    seen_links = load_seen_links(config.SEEN_JOBS_CSV)

    new_jobs = []
    seen_this_run = set()
    for job in all_scraped:
        link = job.get("link")
        if not link or link in seen_links or link in seen_this_run:
            continue
        job["first_seen"] = datetime.now().isoformat(timespec="seconds")
        new_jobs.append(job)
        seen_this_run.add(link)

    print(f"=== {len(new_jobs)} NEW jobs found this run ===")

    if new_jobs:
        append_rows(config.SEEN_JOBS_CSV, new_jobs)
        overwrite_rows(config.NEW_JOBS_CSV, new_jobs)
    else:
        # still write an empty new_jobs file so dashboard shows "no new jobs"
        overwrite_rows(config.NEW_JOBS_CSV, [])

    generate_dashboard(config.SEEN_JOBS_CSV, config.NEW_JOBS_CSV, config.DASHBOARD_PATH)
    print(f"Dashboard updated: {config.DASHBOARD_PATH}")
    print("=== Run complete ===")


if __name__ == "__main__":
    run()
