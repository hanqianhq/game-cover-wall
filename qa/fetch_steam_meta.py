"""Cache official Steam store fields for games that have an app id.

Writes games/steam-meta.json:
  tags        — top 2–4 user tags (store page, l=schinese)
  review      — review_score_desc
  reviewCount — total_reviews
  year        — release year

Missing fields are omitted. Games without a Steam app id are skipped.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "games" / "manifest.json"
OUT = ROOT / "games" / "steam-meta.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5",
    "Cookie": (
        "birthtime=628473601; lastagecheckage=1-0-1990; "
        "wants_mature_content=1; Steam_Language=schinese"
    ),
}

# Official Steam schinese labels. Used only when the API returns the English phrase.
EN_REVIEW = {
    "Overwhelmingly Positive": "好评如潮",
    "Very Positive": "特别好评",
    "Positive": "好评",
    "Mostly Positive": "多半好评",
    "Mixed": "褒贬不一",
    "Mostly Negative": "多半差评",
    "Negative": "差评",
    "Very Negative": "特别差评",
    "Overwhelmingly Negative": "差评如潮",
}
SKIP_REVIEW = {
    "无用户评测",
    "暂无评测",
    "需要更多评测",
    "No user reviews",
    "No User Reviews",
    "Need more user reviews",
    "Not enough reviews",
}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    last: Exception | None = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                return resp.read()
        except urllib.error.HTTPError as err:
            last = err
            if err.code in (429, 500, 502, 503):
                time.sleep(1.5 + attempt * 1.6)
                continue
            if err.code == 403 and attempt < 4:
                time.sleep(1.2 + attempt)
                continue
            raise
        except Exception as err:  # noqa: BLE001 — network flake
            last = err
            time.sleep(0.8 + attempt * 0.7)
    raise RuntimeError(f"failed {url}: {last}")


def extract_tags(html: str) -> list[str]:
    key = "InitAppTagModal("
    i = html.find(key)
    if i >= 0:
        j = html.find("[", i)
        if j >= 0:
            depth = 0
            in_str = False
            esc = False
            for k in range(j, len(html)):
                ch = html[k]
                if in_str:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == '"':
                        in_str = False
                    continue
                if ch == '"':
                    in_str = True
                elif ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth == 0:
                        try:
                            raw = json.loads(html[j : k + 1])
                        except json.JSONDecodeError:
                            raw = None
                        if isinstance(raw, list):
                            ranked = sorted(
                                raw,
                                key=lambda t: int(t.get("count") or 0),
                                reverse=True,
                            )
                            names: list[str] = []
                            for tag in ranked:
                                name = str(tag.get("name") or "").strip()
                                if not name or name == "+":
                                    continue
                                if tag.get("browseable") is False:
                                    continue
                                names.append(name)
                                if len(names) == 4:
                                    break
                            if names:
                                return names
                        break
    glance = re.findall(r'class="app_tag"[^>]*>\s*([^<]+?)\s*<', html)
    names = []
    for name in glance:
        name = name.strip()
        if not name or name == "+":
            continue
        if name not in names:
            names.append(name)
        if len(names) == 4:
            break
    return names


def year_of(release: dict | None) -> int | None:
    if not isinstance(release, dict) or release.get("coming_soon"):
        return None
    match = re.search(r"(?:19|20)\d{2}", str(release.get("date") or ""))
    return int(match.group(0)) if match else None


def review_of(summary: dict) -> tuple[str, int] | None:
    count = int(summary.get("total_reviews") or 0)
    desc = str(summary.get("review_score_desc") or "").strip()
    if count < 10 or not desc or desc in SKIP_REVIEW:
        return None
    if re.fullmatch(r"\d+\s+user reviews?", desc, flags=re.I):
        return None
    return EN_REVIEW.get(desc, desc), count


def fetch_release_year(appid: int) -> int | None:
    url = (
        "https://store.steampowered.com/api/appdetails"
        f"?appids={appid}&l=schinese&filters=release_date"
    )
    try:
        payload = json.loads(get(url).decode("utf-8"))
    except Exception as err:  # noqa: BLE001
        print(f"year fail {appid} {err}")
        return None
    node = payload.get(str(appid)) or {}
    if not node.get("success"):
        return None
    return year_of((node.get("data") or {}).get("release_date"))


def fetch_release_years(appids: list[int]) -> dict[int, int]:
    # Store appdetails rejects comma-separated appids (HTTP 400). One id per call.
    years: dict[int, int] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(fetch_release_year, appid): appid for appid in appids}
        for fut in as_completed(futs):
            appid = futs[fut]
            year = fut.result()
            if year:
                years[appid] = year
    return years


def fetch_one(appid: int) -> dict:
    entry: dict = {"appid": appid}
    rev_url = (
        f"https://store.steampowered.com/appreviews/{appid}"
        "?json=1&language=all&purchase_type=all&num_per_page=0&l=schinese"
    )
    page_url = f"https://store.steampowered.com/app/{appid}/?l=schinese"
    errors = []
    try:
        rev = json.loads(get(rev_url).decode("utf-8"))
        parsed = review_of(rev.get("query_summary") or {})
        if parsed:
            entry["review"], entry["reviewCount"] = parsed
    except Exception as err:  # noqa: BLE001
        errors.append(f"review:{err}")
    try:
        html = get(page_url).decode("utf-8", "replace")
        tags = extract_tags(html)
        if tags:
            entry["tags"] = tags
    except Exception as err:  # noqa: BLE001
        errors.append(f"tags:{err}")
    if errors:
        entry["_errors"] = errors
    return entry


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    groups: dict[int, list[str]] = {}
    for game in manifest:
        steam = game.get("steam")
        if isinstance(steam, int):
            groups.setdefault(steam, []).append(game["id"])
    appids = list(groups)
    print(f"steam apps {len(appids)} games {sum(len(v) for v in groups.values())}")
    years = fetch_release_years(appids)
    print(f"years {len(years)}")

    fetched: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = {pool.submit(fetch_one, appid): appid for appid in appids}
        done = 0
        for fut in as_completed(futs):
            appid = futs[fut]
            done += 1
            try:
                fetched[appid] = fut.result()
            except Exception as err:  # noqa: BLE001
                fetched[appid] = {"appid": appid, "_errors": [str(err)]}
            if done % 15 == 0 or done == len(appids):
                print(f"progress {done}/{len(appids)}")

    out: dict[str, dict] = {}
    missing = []
    for appid, ids in groups.items():
        src = dict(fetched.get(appid) or {"appid": appid})
        errors = src.pop("_errors", None)
        if appid in years:
            src["year"] = years[appid]
        keep = {
            key: src[key]
            for key in ("appid", "tags", "review", "reviewCount", "year")
            if key in src and src[key] not in (None, "", [])
        }
        if "review" in keep and "reviewCount" not in keep:
            keep.pop("review", None)
        for gid in ids:
            if len(keep) > 1:
                out[gid] = keep
            else:
                missing.append(gid)
        if errors:
            print(f"warn {appid} {ids} {errors}")

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tagged = sum(1 for v in out.values() if v.get("tags"))
    reviewed = sum(1 for v in out.values() if v.get("review"))
    yeared = sum(1 for v in out.values() if v.get("year"))
    print(f"wrote {len(out)} tagged {tagged} reviewed {reviewed} yeared {yeared} empty {len(missing)}")
    if missing:
        print("empty", ",".join(missing))


if __name__ == "__main__":
    main()
