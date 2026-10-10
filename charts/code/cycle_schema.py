# Wykres charts/cycle_schema.png (APA 7). Samodzielny plik: python charts/code/cycle_schema.py
# Schemat ogólnego cyklu prezydenckiego w USA wg opisu procesu wyborczego (USAGov, 2026), bez dokładnych dat.
# Oś X: miesiące od początku okna (marzec roku przed wyborami) do połowy marca roku po wyborach; 0 = 1 marca.
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "charts" / "cycle_schema.png"

END = 24.5  # połowa marca roku po wyborach
ELECTION = 20.15  # początek listopada
INAUGURATION = 22.6  # 20 stycznia roku po wyborach

# (nazwa wiersza, opis czasu, początek, koniec); wydarzenia jednodniowe mają początek = koniec
EVENTS = [
    ("Ogłoszenie startu kandydatów", "wiosna roku przed wyborami", 0, 3),
    ("Prawybory i wstępne debaty", "styczeń – czerwiec", 10, 16),
    ("Konwencje nominacyjne", "lipiec – początek września", 16, 18.33),
    ("Debaty prezydenckie", "wrzesień – październik", 18, 20),
    ("Dzień wyborów", "początek listopada", ELECTION, ELECTION),
    ("Zaprzysiężenie", "20 stycznia", INAUGURATION, INAUGURATION),
]

# granice faz wynikają z wydarzeń: start kampanii, konwencje, dzień wyborów, zaprzysiężenie
PHASES = [("Bazowa", 0, 3, "#d9d9d9"), ("Przedwyborcza", 3, 16, "#9ecae1"), ("Szczytowa", 16, ELECTION, "#2171b5"),
          ("Przejściowa", ELECTION, INAUGURATION, "#fdae6b"), ("Powyborcza", INAUGURATION, END, "#74c476")]

# APA 7: czcionka bezszeryfowa 8–14 pt, białe tło, bez siatki, bez tytułu w samym obrazku
plt.rcParams.update({
    "font.family": "Arial", "font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 10, "ytick.labelsize": 9,
    "text.color": "black", "axes.labelcolor": "black", "xtick.color": "black", "ytick.color": "black",
    "axes.linewidth": 0.8, "figure.dpi": 140, "savefig.dpi": 300,
})

fig, ax = plt.subplots(figsize=(6.5, 4.0))

# wiersz 0 = fazy, kolejne wiersze = wydarzenia
for _, start, end, color in [(p[0], p[1], p[2], p[3]) for p in PHASES]:
    ax.barh(0, end - start, left=start, height=0.6, color=color, edgecolor="white", linewidth=1)
for row, (_, _, start, end) in enumerate(EVENTS, start=1):
    if start == end:
        ax.plot(start, row, marker="D", color="black", markersize=6)
    else:
        ax.barh(row, end - start, left=start, height=0.45, color="#595959")

# przerywane linie pokazują, z jakich wydarzeń wynikają granice faz
for boundary in (3, 16, ELECTION, INAUGURATION):
    ax.axvline(boundary, color="0.5", lw=0.7, ls="--", zorder=0)

ax.set_ylim(len(EVENTS) + 0.6, -0.6)
ax.set_yticks(range(len(EVENTS) + 1))
ax.set_yticklabels(["Fazy badania"] + [f"{name}\n({when})" for name, when, _, _ in EVENTS])
ax.tick_params(axis="y", length=0)

# oś X: początki kwartałów w numerach miesięcy (rzymskie), pod spodem lata cyklu
ax.set_xlim(0, END)
ax.set_xticks([1, 4, 7, 10, 13, 16, 19, 22], ["IV", "VII", "X", "I", "IV", "VII", "X", "I"])
ax.set_xticks(range(0, 25), minor=True)
for boundary in (10, 22):
    ax.axvline(boundary, ymin=-0.19, ymax=-0.125, color="black", lw=0.8, clip_on=False)
for label, center in (("Rok przed wyborami", 5), ("Rok wyborczy", 16), ("Rok po", 23.25)):
    ax.text(center, len(EVENTS) + 1.55, label, ha="center", va="top", fontsize=9)
for side in ("left", "right", "top"):
    ax.spines[side].set_visible(False)

handles = [mpatches.Patch(facecolor=color, label=name) for name, _, _, color in PHASES]
fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=9, columnspacing=1.2, handlelength=1.2)
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
plt.show()
