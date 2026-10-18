import json, urllib.request, re

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "zh-CN,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()

# reviews with schinese
for appid in [1091500, 1551360]:
    ru = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=all&purchase_type=all&num_per_page=0&l=schinese"
    rev = json.loads(get(ru))
    q = rev.get("query_summary", {})
    print("review l=schinese", appid, q)

# store page tags
html = get("https://store.steampowered.com/app/1091500/?l=schinese").decode("utf-8", "replace")
# look for popular tags
m = re.search(r"InitAppTagModal\(\s*\d+\s*,\s*(\[[\s\S]*?\])\s*,", html)
if m:
    tags = json.loads(m.group(1))
    print("InitAppTagModal count", len(tags))
    print("top", tags[:8])
else:
    print("no InitAppTagModal")
    # try other patterns
    for pat in [r"\"tags\":\s*(\[[^\]]+\])", r"app_tags[^\n]{0,200}", r"glance_tags([\s\S]{0,800})"]:
        mm = re.search(pat, html)
        if mm:
            print("alt", pat[:40], mm.group(0)[:300])
            break
    # glance_tags HTML
    mm = re.search(r'class="glance_tags[^"]*"([\s\S]*?)</div>\s*<div', html)
    if mm:
        print("glance snippet", mm.group(0)[:500])
    apps = re.findall(r'class="app_tag"[^>]*>([^<]+)<', html)
    print("app_tag texts", [a.strip() for a in apps[:12]])

# steamspy
try:
    spy = json.loads(get("https://steamspy.com/api.php?request=appdetails&appid=1091500"))
    print("spy tags", list(spy.get("tags", {}).keys())[:10] if isinstance(spy.get("tags"), dict) else spy.get("tags"))
except Exception as e:
    print("spy fail", e)

# write sample appdetails to file to verify Chinese
data = json.loads(get("https://store.steampowered.com/api/appdetails?appids=1091500&l=schinese"))
open("qa/_sample_cp.json","w",encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2)[:2500])
print("wrote sample")
