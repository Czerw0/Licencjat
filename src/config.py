# Stałe projektu: ścieżki, dane, okna i fazy, progi czyszczenia, próba, modele, H4, styl rysunków.
# Zwykłe stałe, bez logiki. Uzasadnienia wartości są w pracy (rozdziały „Metoda” i „Procedura badania”).
from pathlib import Path

# --- Ścieżki ---
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data"
PROCESSED_DIR = ROOT / "processed"
LABELS_DIR = ROOT / "labels"
CHARTS_DIR = ROOT / "charts"

# --- Dane ---
# subreddit -> obóz; pliki: r_<subreddit>_comments_<rok>.jsonl
SUBREDDITS = {
    "democrats": "dem",
    "Liberal": "dem",
    "Republican": "rep",
    "Conservative": "rep",
    "running": "reference",
    "languagelearning": "reference",
}
CYCLES = [2012, 2016, 2020, 2024]
REFERENCE_YEARS = [2014, 2018, 2022]     # tylko r/running i r/languagelearning

# rok pliku -> (pierwszy poniedziałek, ostatnia niedziela), UTC, daty włącznie
WINDOWS = {
    2012: ("2011-03-21", "2013-03-17"),
    2014: ("2013-12-30", "2015-01-04"),
    2016: ("2015-03-16", "2017-03-19"),
    2018: ("2018-01-01", "2019-01-06"),
    2020: ("2019-03-18", "2021-03-21"),
    2022: ("2021-12-27", "2023-01-01"),
    2024: ("2023-03-20", "2025-03-16"),
}

# cykl -> [(faza, początek, koniec)], daty włącznie; tydzień należy do fazy, w której wypada jego czwartek
PHASES = {
    2012: [("bazowa", "2011-03-21", "2011-06-12"), ("przedwyborcza", "2011-06-13", "2012-09-02"),
           ("szczytowa", "2012-09-03", "2012-11-05"), ("przejsciowa", "2012-11-06", "2013-01-19"),
           ("powyborcza", "2013-01-20", "2013-03-16")],
    2016: [("bazowa", "2015-03-21", "2015-08-05"), ("przedwyborcza", "2015-08-06", "2016-07-20"),
           ("szczytowa", "2016-07-21", "2016-11-07"), ("przejsciowa", "2016-11-08", "2017-01-19"),
           ("powyborcza", "2017-01-20", "2017-03-16")],
    2020: [("bazowa", "2019-03-21", "2019-06-25"), ("przedwyborcza", "2019-06-26", "2020-08-23"),
           ("szczytowa", "2020-08-24", "2020-11-02"), ("przejsciowa", "2020-11-03", "2021-01-19"),
           ("powyborcza", "2021-01-20", "2021-03-16")],
    2024: [("bazowa", "2023-03-21", "2023-08-22"), ("przedwyborcza", "2023-08-23", "2024-08-18"),
           ("szczytowa", "2024-08-19", "2024-11-04"), ("przejsciowa", "2024-11-05", "2025-01-19"),
           ("powyborcza", "2025-01-20", "2025-03-16")],
}
PHASE_ORDER = ["bazowa", "przedwyborcza", "szczytowa", "przejsciowa", "powyborcza"]
ELECTION_DAYS = {2012: "2012-11-06", 2016: "2016-11-08", 2020: "2020-11-03", 2024: "2024-11-05"}

# --- Czyszczenie ---
BOT_ACCOUNTS = {"automoderator"}         # małe litery; znane boty dopisze Karol po Etapie 1
HIGH_VOLUME_MIN_COMMENTS = None          # próg do ustalenia po Etapie 1; None = flaga wszędzie False
# link (http, https, www), link w markdownie [tekst](url) albo znacznik mediów ![img](...), ![gif](...)
LINK_MEDIA_PATTERN = r"https?://|www\.|\[[^\]]*\]\([^)]*\)"
MIN_WORDS_LANGUAGE = 3
LANGUAGE_CONFIDENCE = 0.9
MIN_WORDS_DUPLICATE = 5
CHUNK_SIZE = 200_000

# --- Próba ---
MIN_WORDS_SAMPLE = 5
MAX_PER_WEEK = 300
RANDOM_STATE = 42

# --- Modele ---
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
NLI_MODEL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
NLI_HYPOTHESIS = "The author criticizes {}."
NLI_THRESHOLD = 0.5

# --- H4 ---
# obóz -> typ terminu -> lista terminów; na razie pusty, uzupełni Karol
CAMP_TERMS = {"dem": {"party": [], "politician": []}, "rep": {"party": [], "politician": []}}
WPA_MIN_PER_GROUP = 50
H4B_PER_CAMP = 5000

# --- Rysunki do pracy (APA 7): plt.rcParams.update(APA_STYLE) ---
APA_STYLE = {
    "font.family": "Arial",
    "font.size": 10,
    "axes.labelsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "text.color": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "axes.linewidth": 0.8,
    "axes.grid": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "figure.dpi": 140,
    "savefig.dpi": 300,
}
