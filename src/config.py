from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data"
PROCESSED_DIR = ROOT / "processed"
RESULTS_DIR = PROCESSED_DIR / "results"
LABELS_DIR = ROOT / "labels"
CHARTS_DIR = ROOT / "charts"
FIGURES_DIR = CHARTS_DIR / "figures"

SUBREDDITS = {
    "democrats": "dem",
    "Liberal": "dem",
    "Republican": "rep",
    "Conservative": "rep",
    "running": "reference",
    "languagelearning": "reference",
}
POLITICAL_SUBREDDITS = ["democrats", "Liberal", "Republican", "Conservative"]
REFERENCE_SUBREDDITS = ["running", "languagelearning"]
CYCLES = [2012, 2016, 2020, 2024]
REFERENCE_YEARS = [2014, 2018, 2022]

STUDY_FILES = (
    [(s, c) for s in POLITICAL_SUBREDDITS for c in CYCLES]
    + [(s, c) for s in REFERENCE_SUBREDDITS for c in sorted(CYCLES + REFERENCE_YEARS)]
)

WINDOWS = {
    2012: ("2011-03-21", "2013-03-17"),
    2014: ("2013-12-30", "2015-01-04"),
    2016: ("2015-03-16", "2017-03-19"),
    2018: ("2018-01-01", "2019-01-06"),
    2020: ("2019-03-18", "2021-03-21"),
    2022: ("2021-12-27", "2023-01-01"),
    2024: ("2023-03-20", "2025-03-16"),
}
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
PHASE_LABELS = {"bazowa": "Bazowa", "przedwyborcza": "Przedwyborcza", "szczytowa": "Szczytowa",
                "przejsciowa": "Przejściowa", "powyborcza": "Powyborcza"}
PHASE_COLORS = {"bazowa": "#d9d9d9", "przedwyborcza": "#9ecae1", "szczytowa": "#2171b5",
                "przejsciowa": "#fdae6b", "powyborcza": "#74c476"}
SUBREDDIT_STYLES = {"democrats": ("black", "-"), "Liberal": ("0.45", "--"), "Republican": ("black", ":"),
                    "Conservative": ("0.45", "-."), "running": ("black", "-"), "languagelearning": ("0.45", "--")}
CAMP_COLORS = {"dem": "#2166ac", "rep": "#b2182b", "reference": "#6b6b6b"}
CAMP_LABELS = {"dem": "Demokraci", "rep": "Republikanie", "reference": "Odniesienia"}
EDA_SUBREDDIT_STYLES = {"democrats": ("#2166ac", "-"), "Liberal": ("#2166ac", "--"), "Republican": ("#b2182b", "-"),
                        "Conservative": ("#b2182b", "--"), "running": ("#6b6b6b", "-"), "languagelearning": ("#6b6b6b", "--")}
EDA_STYLE = {"figure.dpi": 110}
PEAK_COLOR = "#f2e5c6"
GROUP_LABELS = {"democrats": "r/democrats", "Liberal": "r/Liberal", "Republican": "r/Republican", "Conservative": "r/Conservative",
                "dem": "Demokraci", "rep": "Republikanie", "all": "Demokraci i republikanie razem"}
GROUP_COLORS = {"democrats": "#2166ac", "Liberal": "#2166ac", "Republican": "#b2182b", "Conservative": "#b2182b",
                "dem": "#2166ac", "rep": "#b2182b", "all": "#333333"}
GROUP_LINESTYLES = {"democrats": "-", "Liberal": "--", "Republican": "-", "Conservative": "--", "dem": "-", "rep": "-", "all": "-"}
APA_STYLE = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Calibri", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.dpi": 300,
    "axes.edgecolor": "#111111",
    "axes.linewidth": 1,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.size": 4,
    "ytick.major.size": 4,
}
ELECTION_DAYS = {2012: "2012-11-06", 2016: "2016-11-08", 2020: "2020-11-03", 2024: "2024-11-05"}

BOT_ACCOUNTS = ['automoderator', 'autotldr', 'autowikibot', 
                'converter-bot', 'dadbot_3000', 'election_info_bot', 
                'haikusbot', 'helperbot_', 'languagelearning-modteam', 'nogoogleampbot', 
                'remindmebot', 'robotsfromthefuture', 'sneakpeekbot', 'userleansbot', 
                'wikisummarizerbot', 'youtubefactsbot']
HIGH_VOLUME_MIN_COMMENTS = None
LINK_MEDIA_PATTERN = r"https?://|www\.|\[[^\]]*\]\([^)]*\)"
MIN_WORDS_LANGUAGE = 3
LANGUAGE_CONFIDENCE = 0.9
MIN_WORDS_DUPLICATE = 5
CHUNK_SIZE = 200_000

MIN_WORDS_SAMPLE = 5
MAX_PER_WEEK = 300
RANDOM_STATE = 42

EMOTIONS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
NLI_MODEL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
NLI_HYPOTHESIS = "The author criticizes {}."
NLI_THRESHOLD = 0.5
FINETUNE_FOLDS = 5
FINETUNE_EPOCHS = 3
FINETUNE_LEARNING_RATE = 1e-5
FINETUNE_BATCH_SIZE = 8
FINETUNE_WARMUP_RATIO = 0.1
FINETUNED_MODEL_DIR = PROCESSED_DIR / "h4a" / "nli_finetuned"

CAMP_TERMS = {
    "dem": {"party": ["democrat", "democrats", "dem", "dems", "dnc", "liberals"],
            "politician": ["obama", "barack", "biden", "clinton", "hillary", "kaine", "harris", "kamala", "walz"]},
    "rep": {"party": ["republican", "republicans", "gop", "rnc", "conservatives"],
            "politician": ["romney", "mitt", "ryan", "trump", "pence", "vance"]},
}
WPA_MIN_PER_GROUP = 50
H4B_PHASES = ["szczytowa", "przejsciowa"]
H4B_PER_CELL = None
H4B_REPEATS = 100


