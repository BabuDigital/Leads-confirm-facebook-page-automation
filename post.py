#!/usr/bin/env python3
"""Post today's caption + image to the Facebook Page and Instagram account.
Mode 1 (free): META_PAGE_TOKEN set  -> posts directly through Meta's Graph API.
Mode 2: ZAPIER_WEBHOOK_URL set      -> sends caption + image_url to a Zapier webhook.
Images: any .jpg/.jpeg/.png inside images/ whose name contains dayNN (e.g. day09). JPG is best for Instagram."""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

API = "https://graph.facebook.com/v26.0"
IST = timezone(timedelta(hours=5, minutes=30))
today = os.environ.get("POST_DATE") or datetime.now(IST).date().isoformat()
DRY = os.environ.get("DRY_RUN") == "1"

with open("posts.json", encoding="utf-8") as f:
    posts = json.load(f)
post = next((p for p in posts if p["date"] == today), None)
if not post:
    print(f"No post scheduled for {today}. Nothing to do.")
    sys.exit(0)

def find_image(day):
    pat = re.compile(rf"day0*{day}(?!\d)", re.I)
    if os.path.isdir("images"):
        names = [n for n in sorted(os.listdir("images")) if pat.search(n) and n.lower().endswith((".jpg", ".jpeg", ".png"))]
        names.sort(key=lambda n: 0 if n.lower().endswith((".jpg", ".jpeg")) else 1)  # prefer JPG
        if names:
            return f"images/{names[0]}"
    return None

img_path = find_image(post["day"]) or (post["image"] if DRY else None)
if not img_path:
    sys.exit(f"ERROR: no image for day {post['day']} in the images folder (file name must contain 'day{post['day']:02d}'). Nothing was posted.")

repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
branch = os.environ.get("IMAGE_BRANCH") or os.environ.get("GITHUB_REF_NAME") or "main"
image_url = f"https://raw.githubusercontent.com/{repo}/{branch}/" + urllib.parse.quote(img_path)
caption = post["caption"]

if DRY:
    print(json.dumps({"date": today, "day": post["day"], "caption": caption, "image_url": image_url}, ensure_ascii=False, indent=2))
    sys.exit(0)

class ApiError(Exception):
    pass

def graph(path, params, method="POST"):
    url = f"{API}/{path}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise ApiError(f"{e.code}: {e.read().decode()[:400]}")

token = os.environ.get("META_PAGE_TOKEN") or None
hook = os.environ.get("ZAPIER_WEBHOOK_URL") or None

if token:
    fb_id, ig_id = os.environ.get("FB_PAGE_ID"), os.environ.get("IG_USER_ID")
    if not fb_id or not ig_id:
        sys.exit("ERROR: FB_PAGE_ID and IG_USER_ID must be set.")
    errors = []
    # Facebook needs a PAGE token. If a user token was saved, swap it for the page token automatically.
    page_token = token
    try:
        pt = graph(fb_id, {"fields": "access_token", "access_token": token}, "GET").get("access_token")
        if pt:
            page_token = pt
    except ApiError:
        pass
    try:
        r = graph(f"{fb_id}/photos", {"url": image_url, "caption": caption, "access_token": page_token})
        print("Facebook posted:", r.get("post_id") or r.get("id"))
    except ApiError as e:
        errors.append(f"Facebook failed - {e}")
    try:
        cid = graph(f"{ig_id}/media", {"image_url": image_url, "caption": caption, "access_token": token})["id"]
        for _ in range(12):
            st = graph(cid, {"fields": "status_code", "access_token": token}, "GET").get("status_code")
            if st == "FINISHED":
                break
            if st in ("ERROR", "EXPIRED"):
                raise ApiError(f"Instagram media status {st}")
            time.sleep(5)
        r = graph(f"{ig_id}/media_publish", {"creation_id": cid, "access_token": token})
        print("Instagram posted:", r.get("id"))
    except ApiError as e:
        errors.append(f"Instagram failed - {e}")
    if errors:
        sys.exit("\n".join(errors))
elif hook:
    payload = {"date": today, "day": post["day"], "caption": caption, "image_url": image_url}
    req = urllib.request.Request(hook, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            print("Sent day", post["day"], "->", r.status)
    except urllib.error.HTTPError as e:
        sys.exit(f"Webhook error {e.code}: {e.read().decode()[:200]}")
else:
    sys.exit("ERROR: set the META_PAGE_TOKEN secret (or ZAPIER_WEBHOOK_URL).")
