# Leads Confirm Solution – automatic daily Facebook + Instagram posting (3 Nov – 2 Dec 2026)

Every day at 10:00 AM IST, GitHub Actions posts that day's caption and image to the
Leads Confirm Solution Facebook Page and the leads confirm solution Instagram account.

## What is in this folder
- `post.py` – the posting script
- `.github/workflows/daily-post.yml` – the daily schedule (10:00 AM IST)
- `posts.json` – 30 captions with dates (Day 11 = 3 Nov ... Day 40 = 2 Dec 2026)
- `images/day11.jpg ... day40.jpg` – 30 images (1080x1350 JPG)
- `captions-3Nov-2Dec.md` – all captions in a readable list

## Upload to GitHub
1. Repo must be **Public**.
2. Upload `post.py`, `posts.json`, `README.md`, and the whole `images` folder (drag the folder in).
3. Create `.github/workflows/daily-post.yml`: Add file > Create new file, type `.github/workflows/daily-post.yml` as the name, paste the file contents, commit.

## One-time secret
Settings > Secrets and variables > Actions > New repository secret: name `META_PAGE_TOKEN`, value = your never-expiring Page access token
(see the guide doc for how to get it). Never share this token.

## Daily check and manual run
- Actions tab shows a green tick when both posts went out.
- To post a missed day: Actions > Daily Facebook + Instagram post > Run workflow > type the date (YYYY-MM-DD).
- Re-running a day posts it again, so only run a date that has not posted.
