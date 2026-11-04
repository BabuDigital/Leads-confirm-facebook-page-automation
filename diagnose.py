#!/usr/bin/env python3
"""Safe diagnostics for the Meta token stored in the META_PAGE_TOKEN secret. Never prints the token."""
import json, os, sys, urllib.parse, urllib.request, urllib.error
API = "https://graph.facebook.com/v26.0"
T = os.environ.get("META_PAGE_TOKEN")
FB, IG = os.environ.get("FB_PAGE_ID"), os.environ.get("IG_USER_ID")
if not T:
    sys.exit("META_PAGE_TOKEN secret is empty or missing.")
print("Token length:", len(T), "| starts with:", T[:4], "(first 4 characters only)")

def get(path, params):
    params = dict(params); 
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try: body = json.loads(e.read().decode())
        except Exception: body = {}
        err = body.get("error", {})
        return {"ERROR": f"{e.code} code={err.get('code')} sub={err.get('error_subcode')} msg={err.get('message')}"}

print("\n1) Token details (debug_token):")
d = get("debug_token", {"input_token": T, "access_token": T})
if "ERROR" in d: print("   ", d["ERROR"])
else:
    x = d.get("data", {})
    for k in ("app_id", "type", "is_valid", "expires_at", "data_access_expires_at", "scopes", "profile_id"):
        print(f"    {k}: {x.get(k)}")
    if x.get("error"): print("    token error:", x["error"])
print("\n2) Who am I (/me):");        print("   ", get("me", {"fields": "id,name", "access_token": T}))
print("\n3) Facebook page:");         print("   ", get(FB, {"fields": "name,instagram_business_account", "access_token": T}))
print("\n4) Page token lookup:");
r = get(FB, {"fields": "access_token", "access_token": T}); print("    got page token:", "access_token" in r, r.get("ERROR", ""))
print("\n5) Instagram account:");     print("   ", get(IG, {"fields": "username,media_count", "access_token": T}))
