"""
Job Alert Bot - Configuration
Yaha apni search preferences set karo. Ye sab scrapers isi file se keywords/location lete hain.
"""

# Roles jo tu target kar raha hai (LinkedIn pipeline se hi liye hain)
KEYWORDS = [
    "Data Analyst",
    "Python Developer",
    "Data Science Intern",
    "Software Engineer Intern",
]

# Location - "India" rakha hai broad, chahe to specific city daal sakta hai e.g. "Jaipur" / "Remote"
LOCATION = "India"

# Kitne purane jobs tak dekhna hai (Indeed/LinkedIn me posted date filter, days)
MAX_JOB_AGE_DAYS = 3

# Kaunse platforms on/off karne hai
PLATFORMS = {
    "linkedin": True,
    "naukri": True,
    "indeed": True,
    "wellfound": True,
}

# Per keyword per platform kitne results uthaane hai (zyada mat rakhna, rate-limit se bachne ke liye)
RESULTS_PER_SEARCH = 15

# CSV jaha saare "already seen" jobs store honge (duplicate notify na ho isliye)
SEEN_JOBS_CSV = "data/seen_jobs.csv"

# Dashboard HTML output path (GitHub Pages isi docs/ folder se serve hoga)
DASHBOARD_PATH = "docs/index.html"

# Naya job CSV bhi banega har run me (sirf is run ke naye jobs), ye 'diff' ke tarah kaam karega
NEW_JOBS_CSV = "data/new_jobs_latest_run.csv"

# HTTP request headers - real browser jaisa dikhne ke liye (blocking kam hogi)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 15  # seconds
