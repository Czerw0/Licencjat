# Wykres charts/comments_number_2012_2024.png (APA 7). Samodzielny plik: python charts/code/comments_number_2012_2024.py
# Czyta tylko processed/eda/*.parquet (wynik scripts/generate_eda.py + notebooków eda_<subreddit>.ipynb).
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "processed" / "eda"
OUTPUT = ROOT / "charts" / "comments_number_2012_2024.png"

SUBREDDITS = ["democrats", "Liberal", "Republican", "Conservative", "running", "languagelearning"]
COLOR = {"democrats": "#1f77b4", "Liberal": "#08306b", "Republican": "#fd8d3c",
         "Conservative": "#a63603", "running": "#31a354", "languagelearning": "#756bb1"}
MIN_PER_WEEK = 50
MAX_PER_WEEK = 300
MIN_WORDS = 5

# rok pliku: (pierwszy poniedziałek, ostatnia niedziela)
WINDOWS = {2012: ("2011-03-21", "2013-03-17"), 2024: ("2023-03-20", "2025-03-16")}
ELECTIONS = {2012: "2012-11-06", 2024: "2024-11-05"}

# flagi zapisane jako bity jednej liczby: deleted, moderator, bot, no_text, duplicate
DROPPED = 1 | 2 | 4 | 8 | 16

# liczba ważnych komentarzy na tydzień
weekly_parts = []
for subreddit in SUBREDDITS:
    for year, (start, end) in WINDOWS.items():
        part = pd.read_parquet(CACHE / f"r_{subreddit}_comments_{year}.parquet", columns=["created_utc", "flags", "n_words"])
        valid = ((part["flags"].values & DROPPED) == 0) & (part["n_words"].values >= MIN_WORDS)
        first_day = (pd.Timestamp(start) - pd.Timestamp(0)).days
        week_nr = (part["created_utc"].values // 86400 - first_day) // 7
        n_weeks = (pd.Timestamp(end) - pd.Timestamp(start)).days // 7 + 1
        # tygodnie bez komentarzy dostają 0
        n_valid = pd.Series(valid).groupby(week_nr).sum().reindex(range(n_weeks), fill_value=0)
        weekly_parts.append(pd.DataFrame({"week_nr": n_valid.index, "n_valid": n_valid.values, "subreddit": subreddit, "year": year}))
weekly = pd.concat(weekly_parts, ignore_index=True)

election_week = {y: (pd.Timestamp(ELECTIONS[y]) - pd.Timestamp(WINDOWS[y][0])).days // 7 for y in WINDOWS}

# %% Wykres
# APA 7: czcionka bezszeryfowa 8–14 pt, białe tło, bez siatki, bez tytułu w samym obrazku
sns.set_theme(
    style="ticks",
    context="paper",
    font="Arial",
    rc={
        "axes.titlesize": 11,
        "axes.labelsize": 11,
        "axes.titlepad": 6,
        "legend.fontsize": 10,
        "legend.title_fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.linewidth": 0.8,
        "axes.edgecolor": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "text.color": "black",
        "axes.labelcolor": "black",
        "figure.dpi": 140,
        "savefig.dpi": 300,
    },
)

g = sns.relplot(
    data=weekly,
    x="week_nr",
    y="n_valid",
    hue="subreddit",
    hue_order=SUBREDDITS,
    palette=COLOR,
    kind="line",
    col="year",
    col_wrap=2,
    height=3.2,
    aspect=1.3,
    linewidth=1.2,
    errorbar=None,
    facet_kws={"sharey": True},
)

g.set(yscale="symlog")
g.set_axis_labels("Tydzień od początku okna", "Liczba ważnych komentarzy na tydzień")
g.set_titles("{col_name}")  # etykiety paneli, tytuł rysunku idzie do tekstu pracy

for y, ax in g.axes_dict.items():
    ax.set_ylim(0, max(weekly["n_valid"].max() * 1.5, 1))
    # progi w szarości, żeby nie myliły się z liniami subredditów
    ax.axhline(MAX_PER_WEEK, color="0.4", lw=0.9, ls="--")
    ax.axhline(MIN_PER_WEEK, color="0.4", lw=0.9, ls="--")
    ax.axvline(election_week[y], color="black", lw=0.9, ls=":")
    sns.despine(ax=ax)
    ax.grid(False)

# legenda w obrębie figury (współrzędne figury), żeby była widoczna także w oknie plt.show()
sns.move_legend(g, "center left", bbox_to_anchor=(0.84, 0.5), title="Subreddit", frameon=False)

g.tight_layout(rect=(0, 0, 0.84, 1))
g.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.show()
