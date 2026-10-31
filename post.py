#!/usr/bin/env python3
"""Send today's post (caption + public image URL) to a Zapier webhook.
Zapier then publishes it to the Facebook Page and Instagram account."""
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
today = os.environ.get("POST_DATE") or datetime.now(IST).date().isoformat()

with open("posts.json", encoding="utf-8") as f:
    posts = json.load(f)
post = next((p for p in posts if p["date"] == today), None)
if not post:
    print(f"No post scheduled for {today}. Nothing to do.")
    sys.exit(0)

repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
branch = os.environ.get("IMAGE_BRANCH") or os.environ.get("GITHUB_REF_NAME") or "main"
image_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{post['image']}"
if not os.path.exists(post["image"]) and os.environ.get("DRY_RUN") != "1":
    sys.exit(f"ERROR: image file {post['image']} is missing from the repo. Nothing was posted.")

payload = {"date": today, "day": post["day"], "caption": post["caption"], "image_url": image_url}
if os.environ.get("DRY_RUN") == "1":
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(0)

hook = os.environ.get("ZAPIER_WEBHOOK_URL")
if not hook:
    sys.exit("ERROR: ZAPIER_WEBHOOK_URL secret is not set.")
req = urllib.request.Request(hook, data=json.dumps(payload).encode("utf-8"),
                             headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print("Sent day", post["day"], "->", r.status, r.read().decode()[:200])
except urllib.error.HTTPError as e:
    sys.exit(f"Webhook error {e.code}: {e.read().decode()[:200]}")
