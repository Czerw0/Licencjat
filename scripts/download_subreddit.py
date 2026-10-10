import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:                                        
    raise SystemExit("Brak pakietu tqdm. Zainstaluj go: pip install tqdm")

API = "https://arctic-shift.photon-reddit.com/api/comments/search"
RAW_DIR = Path(__file__).resolve().parent.parent / "data"


WINDOWS = {
    2012: ("2011-03-21", "2013-03-17"),
    2016: ("2015-03-16", "2017-03-19"),
    2020: ("2019-03-18", "2021-03-21"),
    2024: ("2023-03-20", "2025-03-16"),
}
LIMIT = 100           # komentarzy na jedno zapytanie (maksimum API)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) licencjat-pobieranie/1.0",
    "Accept": "application/json",
}
WEEK = 7 * 86400      # sekund w tygodniu
PAUSE = 0.5           # sekundy między zapytaniami, żeby nie obciążać serwera


def to_seconds(data):
    return int(datetime.strptime(data, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())


def query_api(subreddit, after, before):
    params = urllib.parse.urlencode({
        "subreddit": subreddit, "after": after, "before": before, "limit": LIMIT, "sort": "asc",
    })
    request = urllib.request.Request(f"{API}?{params}", headers=HEADERS)
    attempt = 0
    while True:
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read())["data"]
        except urllib.error.HTTPError as error:
            body_text = error.read()[:300].decode("utf-8", "ignore")
            transient = error.code in (429, 500, 502, 503, 504) or (error.code == 422 and "Timeout" in body_text)
            if not transient:                                
                raise SystemExit(f"Serwer odmówił (HTTP {error.code}). Odpowiedź: {body_text}")
            attempt += 1
            if attempt > 8:
                raise
            wait = min(5 * 2 ** attempt, 300)                  
            print(f"  HTTP {error.code}, ponawiam za {wait} s")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            attempt += 1
            if attempt > 8:
                raise
            wait = min(2 ** attempt, 120)         
            print(f"  błąd ({error}), ponawiam za {wait} s")
            time.sleep(wait)


def last_saved(path):
    last, ids = None, set()
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if last is None or r["created_utc"] > last:
                    last, ids = r["created_utc"], {r["id"]}
                elif r["created_utc"] == last:
                    ids.add(r["id"])
    return last, ids


def download_window(subreddit, start, end, target):
    last, seen = last_saved(target)
    after = start - 1 if last is None else last - 1      
    weeks = (end - start) // WEEK
    count = 0
    bar = tqdm(total=weeks, desc=target.name.replace(".jsonl.part", ""), unit="tydz.",
               bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} tyg. "
                          "[{elapsed}<{remaining}{postfix}]")
    bar.update(max(0, (after + 1 - start) // WEEK))      
    with open(target, "a", encoding="utf-8") as f:
        while True:
            batch = query_api(subreddit, after, end)
            new = [r for r in batch if r["id"] not in seen]
            if not new:
                break                                     
            for r in new:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            count += len(new)
            newest = max(r["created_utc"] for r in new)
            seen = {r["id"] for r in batch if r["created_utc"] >= newest - 1}
            after = newest - 1
            bar.update(min(weeks, (newest - start) // WEEK) - bar.n)
            day = datetime.fromtimestamp(newest, timezone.utc).date()
            bar.set_postfix_str(f"{count:,} kom., {day}".replace(",", " "))
            time.sleep(PAUSE)
    bar.update(weeks - bar.n)
    bar.close()
    return count


def test(subreddit):
    start = to_seconds("2024-10-01")
    data = query_api(subreddit, start, start + 86400)
    print(f"r/{subreddit}, 1 października 2024: {len(data)} komentarzy (maks. {LIMIT} w jednym zapytaniu)")
    if data:
        fields = sorted(data[0].keys())
        print(f"pól: {len(fields)}")
        for key in ["id", "created_utc", "retrieved_on", "body", "author", "link_id", "parent_id",
                    "score", "distinguished", "subreddit", "_meta"]:
            print(f"  {key:<14} {'jest' if key in fields else 'BRAK'}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit", nargs="?", default="Liberal",
                        help="nazwa bez r/ (domyślnie Liberal; wielkość liter jak na Reddicie)")
    parser.add_argument("--test", action="store_true", help="pobierz tylko 1 dzień i pokaż pola")
    parser.add_argument("--years", type=int, nargs="*", default=list(WINDOWS), help="np. --years 2012 2024")
    args = parser.parse_args()

    if args.test:
        test(args.subreddit)
        return

    RAW_DIR.mkdir(exist_ok=True)
    for year in args.years:
        final_path = RAW_DIR / f"r_{args.subreddit}_comments_{year}.jsonl"
        if final_path.exists():
            print(f"{final_path.name}: już jest, pomijam")
            continue
        part_path = final_path.with_name(final_path.name + ".part")
        start = to_seconds(WINDOWS[year][0])
        end = to_seconds(WINDOWS[year][1]) + 86400         
        n = download_window(args.subreddit, start, end, part_path)
        part_path.replace(final_path)                          
        mb = final_path.stat().st_size / 1e6
        print(f"  zapisano {final_path.name} ({mb:.1f} MB, {n:,} komentarzy w tym przebiegu)".replace(",", " "))


if __name__ == "__main__":
    main()
