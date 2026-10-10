# Wykres charts/cycle_phases.png (APA 7). Samodzielny plik: python charts/code/cycle_phases.py
# Fazy cyklu z src/config.py; granice wynikają z wydarzeń cyklu wyborczego w USA (USAGov, 2026), a nie z liczby tygodni.
import sys
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
from config import APA_STYLE, CHARTS_DIR, ELECTION_DAYS, PHASES

OUTPUT = CHARTS_DIR / "cycle_phases.png"

PHASE_LABELS = {"bazowa": "Bazowa", "przedwyborcza": "Przedwyborcza", "szczytowa": "Szczytowa",
                "przejsciowa": "Przejściowa", "powyborcza": "Powyborcza"}
# kolory rozróżnialne także w odcieniach szarości
PHASE_COLORS = {"bazowa": "#d9d9d9", "przedwyborcza": "#9ecae1", "szczytowa": "#2171b5",
                "przejsciowa": "#fdae6b", "powyborcza": "#74c476"}

plt.rcParams.update(APA_STYLE)

fig, axes = plt.subplots(len(PHASES), 1, figsize=(6.5, 4.8))
for ax, (cycle, phases) in zip(axes, PHASES.items()):
    for phase, start, end in phases:
        left = mdates.datestr2num(start)
        width = mdates.datestr2num(end) + 1 - left  # koniec włącznie
        ax.broken_barh([(left, width)], (0, 1), facecolors=PHASE_COLORS[phase], edgecolor="white", linewidth=1)
    # znaczniki nad paskiem: dzień wyborów (pełny) i zaprzysiężenie (pusty)
    ax.plot(mdates.datestr2num(ELECTION_DAYS[cycle]), 1.25, marker="v", color="black", markersize=5, clip_on=False)
    ax.plot(mdates.datestr2num(phases[-1][1]), 1.25, marker="v", markerfacecolor="white", markeredgecolor="black",
            markersize=5, clip_on=False)

    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_ylabel(f"Cykl {cycle}", rotation=0, ha="right", va="center")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=(4, 7, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.set_xlim(mdates.datestr2num(phases[0][1]), mdates.datestr2num(phases[-1][2]) + 1)

handles = [mpatches.Patch(facecolor=PHASE_COLORS[p], label=PHASE_LABELS[p]) for p in PHASE_LABELS]
handles += [mlines.Line2D([], [], marker="v", color="black", linestyle="", markersize=5, label="Dzień wyborów"),
            mlines.Line2D([], [], marker="v", markerfacecolor="white", markeredgecolor="black", linestyle="",
                          markersize=5, label="Zaprzysiężenie (20 stycznia)")]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=10)
fig.tight_layout(rect=(0, 0.13, 1, 1), h_pad=1.8)
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.show()
