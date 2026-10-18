import re, json, urllib.request

text = open("src/cardTexture.ts", encoding="utf-8").read()
ids = re.findall(r"id:\s*'([^']+)'[\s\S]*?source:\s*'([^']+)'", text)
print("entries", len(ids))
steam = []
nosteam = []
for i, s in ids:
    m = re.search(r"app/(\d+)", s)
    if m:
        steam.append((i, int(m.group(1))))
    else:
        nosteam.append((i, s[:80]))
print("steam", len(steam), "nosteam", len(nosteam))
print("sample steam", steam[:8])
print("nosteam:")
for x in nosteam:
    print(" ", x)

for appid in [1174180, 1091500, 1245620, 1551360]:
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=schinese"
    with urllib.request.urlopen(url, timeout=25) as r:
        data = json.load(r)
    d = data[str(appid)]["data"]
    genres = [g["description"] for g in d.get("genres", [])]
    cats = [c["description"] for c in d.get("categories", [])][:8]
    rel = d.get("release_date", {})
    print("---", appid, d.get("name"))
    print("genres", genres)
    print("cats", cats)
    print("release", rel)
    ru = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=all&purchase_type=all&num_per_page=0"
    with urllib.request.urlopen(ru, timeout=25) as r:
        rev = json.load(r)
    q = rev.get("query_summary", {})
    print("review", q.get("review_score_desc"), q.get("total_reviews"), q.get("review_score"))
