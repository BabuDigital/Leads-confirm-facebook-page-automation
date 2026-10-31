# Daily Facebook + Instagram auto-post (GitHub Actions + Zapier)

Every day at 10:00 AM IST, GitHub runs `post.py`. It reads today's caption from `posts.json`,
builds a public image link from `images/dayNN.jpg`, and sends both to a Zapier webhook.
Zapier publishes to the Leads Confirm Solution Facebook Page and Instagram account only.

## Setup (one time)
1. Create a **public** GitHub repo (raw image links only work on public repos). Upload everything in this folder.
2. Put 30 JPG images (1080x1350) in `images/`, named `day01.jpg` ... `day30.jpg`.
3. In Zapier, create a Zap:
   - Trigger: **Webhooks by Zapier > Catch Hook** (paid Zapier feature). Copy the webhook URL.
   - Action 1: **Facebook Pages > Create Page Photo** - Page: Leads Confirm Solution. Photo: `image_url`. Message: `caption`.
   - Action 2: **Instagram for Business > Publish Photo(s)** - Account: leads confirm solution. Media: `image_url`. Caption: `caption`.
   - Use the working "#2" connections. Turn the Zap on.
4. In GitHub: Settings > Secrets and variables > Actions > New secret. Name `ZAPIER_WEBHOOK_URL`, value = the webhook URL.
5. Test: Actions tab > "Daily Facebook + Instagram post" > Run workflow. Use the optional date box to pick a day.

## Notes
- Scheduled runs can start a few minutes late. GitHub may pause schedules in repos with no activity for 60 days.
- A day with no matching date in `posts.json` is skipped. Re-running the same day posts it again.
- Local preview: `DRY_RUN=1 POST_DATE=2026-10-26 GITHUB_REPOSITORY=you/repo python post.py`
