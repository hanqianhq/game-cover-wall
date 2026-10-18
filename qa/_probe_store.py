import json, urllib.request, re, http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "birthtime=628473601; lastagecheckage=1-0-1990; wants_mature_content=1; Steam_Language=schinese",
    })
    with opener.open(req, timeout=25) as r:
        return r.read()

html = get("https://store.steampowered.com/app/1091500/?l=schinese").decode("utf-8", "replace")
open("qa/_cp_store.html","w",encoding="utf-8").write(html)
print("html len", len(html), "title check", "2077" in html)
apps = re.findall(r'class="app_tag"[^>]*>([^<]+)<', html)
print("app_tag", [a.strip() for a in apps[:15]])
m = re.search(r"InitAppTagModal\(\s*\d+\s*,\s*(\[[\s\S]*?\])\s*,", html)
print("modal", bool(m))
if m:
    tags = json.loads(m.group(1))
    open("qa/_cp_tags.json","w",encoding="utf-8").write(json.dumps(tags[:15], ensure_ascii=False, indent=2))
    print("wrote tags", len(tags))
# also try featuredtags in JSON-LD or application_config
for pat in [r"\[\{[^\]]{0,40}\"tagid\"[\s\S]{0,2000}?\}]", r"popular_tags[\s\S]{0,500}"]:
    mm = re.search(pat, html)
    if mm:
        print("pat hit", mm.group(0)[:200])
