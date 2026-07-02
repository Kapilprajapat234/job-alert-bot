# 📋 Job Alert Bot

LinkedIn, Naukri, Indeed aur Wellfound pe naye jobs automatically track karta hai
aur ek live dashboard (website) pe dikhata hai. GitHub Actions pe free me
24x7 chalta hai — tera PC on hona bhi zaroori nahi.

## Kaise kaam karta hai

1. Har 6 ghante me (customizable) GitHub Actions apne aap `main.py` chalata hai
2. Ye script LinkedIn/Naukri/Indeed/Wellfound pe teri keywords search karta hai
3. `data/seen_jobs.csv` se compare karke sirf **naye** jobs pakadta hai
4. Naye jobs CSV me save hote hain + dashboard (`docs/index.html`) update ho jata hai
5. GitHub Pages us dashboard ko ek live URL pe serve karta hai — bas wo link
   phone/laptop pe bookmark kar lo, jab bhi khologe naye jobs "NEW" badge ke
   saath dikhenge

## Setup (ek baar karna hai)

### 1. GitHub pe repo banao
```
- github.com pe "New repository" -> naam do e.g. "job-alert-bot"
- Public rakho (Pages free tier ke liye)
```

### 2. Ye saari files us repo me push karo
```bash
cd job_alert_bot
git init
git add .
git commit -m "Initial job alert bot setup"
git branch -M main
git remote add origin https://github.com/Kapilprajapat234/job-alert-bot.git
git push -u origin main
```

### 3. GitHub Pages ON karo
```
Repo -> Settings -> Pages -> Source: "Deploy from a branch"
Branch: main, Folder: /docs -> Save
```
2-3 minute me tera dashboard live ho jayega:
`https://kapilprajapat234.github.io/job-alert-bot/`

### 4. Actions permission check karo
```
Repo -> Settings -> Actions -> General -> Workflow permissions
-> "Read and write permissions" select karo -> Save
```
(Ye zaroori hai kyunki bot khud CSV/dashboard commit karta hai)

### 5. Pehli baar manually run karo (test ke liye)
```
Repo -> Actions tab -> "Job Alert Bot" workflow -> "Run workflow" button
```
2-3 min me complete hoga, phir `docs/index.html` update dikhega aur Pages
link pe live jobs aa jayenge.

Uske baad ye automatically har 6 ghante me chalta rahega, koi manual kaam nahi.

## Customize karna ho to

`config.py` khol ke edit karo:
- `KEYWORDS` — job titles jo search karne hain
- `LOCATION` — city ya "India" / "Remote"
- `PLATFORMS` — koi platform off karna ho to `False` kar do
- Cron schedule change karni ho to `.github/workflows/job_alert.yml` me
  `cron: "0 */6 * * *"` line edit karo (har 6 ghante ki jagah har 3 ghante
  ke liye `"0 */3 * * *"`)

## Important Notes

- **LinkedIn**: Login ki zaroorat nahi (guest search API use kiya hai) —
  ye jaanbujh kar kiya hai kyunki cloud server se baar-baar login karne pe
  LinkedIn account restrict/ban kar sakta hai.
- **Indeed**: Sabse zyada bot-protection wala platform hai. Kabhi kabhi
  block/0-results aa sakta hai — baaki 3 platforms tab bhi normally chalte
  rahenge, pura pipeline nahi rukega.
- **Wellfound**: React-based site hai isliye scraping thoda fragile hai.
  Agar future me 0 results aane lage, iska matlab unka page structure
  change hua hai — `scrapers/wellfound_scraper.py` update karni padegi.
- Websites apni HTML/API structure kabhi bhi change kar sakti hain. Agar
  koi ek platform kaam karna band kar de, sirf uski scraper file check
  karni hogi — baaki system waisa hi chalega.

## Local testing (optional)

```bash
pip install -r requirements.txt
python main.py
```
Ye `docs/index.html` local bana dega jise browser me directly khol sakte ho.
