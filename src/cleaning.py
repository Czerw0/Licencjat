import html
import json

import pandas as pd
from lingua import Language, LanguageDetectorBuilder
from tqdm.auto import tqdm

from src.config import (BOT_ACCOUNTS, CHUNK_SIZE, HIGH_VOLUME_MIN_COMMENTS, LANGUAGE_CONFIDENCE, LINK_MEDIA_PATTERN,
                        MIN_WORDS_DUPLICATE, MIN_WORDS_LANGUAGE, RAW_DIR, SUBREDDITS, WINDOWS)
from src.weeks import assign_phase, to_week_start

FLAGS = ["f_deleted", "f_moderator", "f_bot", "f_high_volume", "f_no_text", "f_media", "f_not_english", "f_duplicate"]
RAW_FIELDS = ["id", "author", "body", "created_utc", "retrieved_on", "link_id", "parent_id", "distinguished"]


def clean_text(body):
    """Usuwa encje HTML, cytaty, linki, markdown i nadmiarowe spacje zwraca Series z tekstem"""
    text = body.fillna("").astype(str)
    has_entity = text.str.contains("&", regex=False)
    text.loc[has_entity] = text[has_entity].map(html.unescape)
    text = text.str.replace(r"(?m)^[ \t]*>.*$", "", regex=True)
    text = text.str.replace(r"\[([^\]]*)\]\([^)]*\)", r"\1", regex=True)
    text = text.str.replace(r"https?://\S+|www\.\S+", "", regex=True)
    text = text.str.replace(r"[*~^`#]", "", regex=True)
    return text.str.replace(r"\s+", " ", regex=True).str.strip()


def add_text_flags(df):
    """Flagi liczone na porcji: f_deleted, f_moderator, f_bot, f_no_text, f_media oraz text i n_words"""
    body = df["body"].fillna("").astype(str)
    df["f_deleted"] = body.str.strip().isin(["[deleted]", "[removed]"])
    df["f_moderator"] = df["distinguished"].eq("moderator")
    df["f_bot"] = df["author"].fillna("").str.lower().isin(BOT_ACCOUNTS)
    df["text"] = clean_text(body)
    df["n_words"] = df["text"].str.split().str.len().astype("int64")
    df["f_no_text"] = df["n_words"].eq(0)
    df["f_media"] = body.str.contains(LINK_MEDIA_PATTERN, regex=True)
    return df


def add_language(df, detector):
    """lang, lang_conf i f_not_english; język liczony tylko dla rekordów, które nie odpadły wcześniej (oszczędność czasu)."""
    df["lang"] = pd.Series(None, index=df.index, dtype="object")
    df["lang_conf"] = float("nan")
    df["f_not_english"] = False
    earlier = df[["f_deleted", "f_moderator", "f_bot", "f_no_text", "f_media"]].any(axis=1)
    rows = df.index[~earlier & (df["n_words"] >= MIN_WORDS_LANGUAGE)]
    texts = df.loc[rows, "text"].str.lower().tolist()
    top = [values[0] for values in detector.compute_language_confidence_values_in_parallel(texts)]
    df.loc[rows, "lang"] = [value.language.iso_code_639_1.name.lower() for value in top]
    df.loc[rows, "lang_conf"] = [value.value for value in top]
    df.loc[rows, "f_not_english"] = [value.language != Language.ENGLISH and value.value >= LANGUAGE_CONFIDENCE
                                     for value in top]
    return df


def add_week_and_phase(df):
    """week_start (poniedziałek UTC) i phase; potrzebuje kolumn cycle i created_utc."""
    df["week_start"] = to_week_start(df["created_utc"])
    df["phase"] = assign_phase(df["week_start"], df["cycle"])
    return df


def add_high_volume(df, min_comments=HIGH_VOLUME_MIN_COMMENTS):
    """f_high_volume: konto (bez [deleted]) z co najmniej min_comments komentarzy z treścią w pliku; None = wszędzie False."""
    df["f_high_volume"] = False
    if min_comments is None:
        return df
    with_content = df[~df["f_deleted"] & ~df["author_deleted"]]
    counts = with_content["author"].value_counts()
    high_volume = counts.index[counts >= min_comments]
    df["f_high_volume"] = df["author"].isin(high_volume) & ~df["f_deleted"] & ~df["author_deleted"]
    return df


def add_duplicates(df):
    """f_duplicate: ten sam tekst (małe litery) w subreddicie i tygodniu, od MIN_WORDS_DUPLICATE słów; zostaje pierwszy."""
    long_enough = df["n_words"] >= MIN_WORDS_DUPLICATE
    key = df["subreddit"] + "|" + df["week_start"].astype(str) + "|" + df["text"].str.lower()
    ordered = df.sort_values("created_utc", kind="stable")
    duplicated = key.loc[ordered.index].duplicated(keep="first")
    df["f_duplicate"] = (duplicated & long_enough.loc[ordered.index]).reindex(df.index)
    return df


def make_funnel(df, n_outside, n_bad_lines=0):
    """Lejek: kolejne flagi w ustalonej kolejności; dropped = nowo odrzucone, flag_total = ile rekordów ma flagę."""
    rows = [{"step": "uszkodzone_linie", "dropped": n_bad_lines, "remaining": len(df) + n_outside, "flag_total": n_bad_lines},
            {"step": "poza_oknem", "dropped": n_outside, "remaining": len(df), "flag_total": n_outside}]
    alive = pd.Series(True, index=df.index)
    for flag in FLAGS:
        dropped = int((alive & df[flag]).sum())
        alive &= ~df[flag]
        rows.append({"step": flag, "dropped": dropped, "remaining": int(alive.sum()), "flag_total": int(df[flag].sum())})
    return pd.DataFrame(rows)


def make_weekly_counts(df, window_weeks):
    """Tabela tygodniowa: każdy tydzień okna (także pusty, z zerami)."""
    kept = df[df["keep"]]
    weekly = pd.DataFrame(index=window_weeks)
    weekly["n_raw"] = df.groupby("week_start").size()
    weekly["share_deleted"] = df.groupby("week_start")["f_deleted"].mean()
    weekly["n_keep"] = kept.groupby("week_start").size()
    for words in (3, 5, 10):
        weekly[f"n_valid_{words}w"] = kept[kept["n_words"] >= words].groupby("week_start").size()
    weekly["n_authors"] = kept[~kept["author_deleted"]].groupby("week_start")["author"].nunique()
    weekly = weekly.fillna({"n_raw": 0, "n_keep": 0, "n_valid_3w": 0, "n_valid_5w": 0, "n_valid_10w": 0, "n_authors": 0})
    weekly.index.name = "week_start"
    return weekly.reset_index()


def clean_file(subreddit, cycle, limit=None):
    """Czyści jeden plik .jsonl: zwraca (clean, weekly_counts, funnel). limit = tylko pierwsze rekordy (do testów)."""
    path = RAW_DIR / f"r_{subreddit}_comments_{cycle}.jsonl"
    start, end = WINDOWS[cycle]
    start_ts = pd.Timestamp(start).timestamp()
    end_ts = pd.Timestamp(end).timestamp() + 86400
    detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

    chunks, rows, n_outside, n_bad_lines, n_read = [], [], 0, 0, 0
    with open(path, encoding="utf-8") as file:
        for line in tqdm(file, desc=f"{subreddit} {cycle}", unit=" rek", unit_scale=True):
            n_read += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                n_bad_lines += 1
                continue
            if not start_ts <= int(record["created_utc"]) < end_ts:
                n_outside += 1
            else:
                row = [record.get(field) for field in RAW_FIELDS]
                row[2] = (row[2] or "").encode("utf-8", "ignore").decode("utf-8")
                row.append(bool((record.get("_meta") or {}).get("removal_type")))
                rows.append(row)
            if len(rows) == CHUNK_SIZE:
                chunks.append(process_chunk(rows, detector, subreddit, cycle))
                rows = []
            if limit is not None and n_read >= limit:
                break
    if rows:
        chunks.append(process_chunk(rows, detector, subreddit, cycle))

    df = pd.concat(chunks, ignore_index=True)
    df = add_week_and_phase(df)
    df = add_high_volume(df)
    df = add_duplicates(df)
    df["keep"] = ~df[FLAGS].any(axis=1)

    window_weeks = pd.date_range(start, end, freq="7D").astype("datetime64[s]")
    weekly = make_weekly_counts(df, window_weeks)
    weekly.insert(1, "cycle", cycle)
    weekly.insert(2, "phase", assign_phase(weekly["week_start"], weekly["cycle"]))
    funnel = make_funnel(df, n_outside, n_bad_lines)

    columns = ["id", "link_id", "parent_id", "subreddit", "camp", "cycle", "week_start", "phase", "created_utc",
               "retrieved_on", "text", "n_words", "lang", "lang_conf", "author_deleted", "removed_later"] + FLAGS + ["keep"]
    return df[columns], weekly, funnel


def process_chunk(rows, detector, subreddit, cycle):
    df = pd.DataFrame(rows, columns=RAW_FIELDS + ["removed_later"])
    df["subreddit"] = subreddit
    df["camp"] = SUBREDDITS[subreddit]
    df["cycle"] = cycle
    df["author_deleted"] = df["author"].eq("[deleted]")
    df = add_text_flags(df)
    df = add_language(df, detector)
    return df.drop(columns=["body", "distinguished"])
