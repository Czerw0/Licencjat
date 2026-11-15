# Licencjat

Cykliczność emocji oraz polaryzacja afektywna i językowa w komentarzach z politycznych subredditów
w czterech cyklach wyborów prezydenckich w USA (2012, 2016, 2020, 2024).

Pipeline prowadzi od surowych komentarzy z archiwum Arctic Shift do wyników czterech hipotez:

| | Hipoteza | Folder |
|---|---|---|
| H1 | w trakcie kampanii więcej emocji negatywnych niż przed nią | `h1/` |
| H2 | w trakcie kampanii więcej emocji o wysokim pobudzeniu | `h2/` |
| H3 | po kampanii emocje negatywne wracają do poziomu bazowego | `h3/` |
| H4a | polaryzacja afektywna (WPA) wyższa w cyklach 2020–2024 niż 2012–2016 | `h4a/` |
| H4b | polaryzacja językowa (trafność klasyfikacji obozów) wyższa w 2020–2024 niż 2012–2016 | `h4b/` |

## Struktura repozytorium

### Foldery, które są w repozytorium

| Folder | Zawartość |
|---|---|
| `src/` | kod wspólny dla notebooków: `config.py` (subreddity, okna czasowe, fazy, modele, style wykresów), `cleaning.py` (czyszczenie jednego pliku), `weeks.py` (przypisanie do tygodnia), `terms.py` (słowniki obozów), `nli.py` (prawdopodobieństwa modelu NLI) |
| `scripts/` | `download_subreddit.py` – pobieranie komentarzy z API Arctic Shift do `data/` |
| `eda/` | eksploracja danych na kolejnych etapach: skan surowych plików (`01`), EDA surowych danych (`02`), po czyszczeniu (`03`), próby tygodniowej (`04`) i emocji (`05`) |
| `cleaning/` | czyszczenie wszystkich 30 plików (`01_cleaning_all`) |
| `features/` | próba tygodniowa (`01_sample`), klasyfikacja emocji i sentymentu (`02_emotions`), agregacja tygodniowa i fazowa (`03_weekly_emotions`) |
| `extra/` | analizy pomocnicze: boty (`01`), słowa obozów (`02`), walidacja modelu emocji (`03`), walidacja modelu NLI (`04`), walidacja modelu H4b (`05`), tematy (`06`) |
| `h1/` `h2/` `h3/` `h4a/` `h4b/` | po jednym folderze na hipotezę: `*_analysis` (tabele i wykresy robocze) oraz `*_statistics` (analiza statystyczna, na razie szkielety). W `h4a/` dodatkowo `h4a_mentions` i `h4a_stance` |
| `charts/` | notebooki generujące rysunki do pracy wyniki trafiają do `charts/figures/` |
| `labels/` | ręczne etykiety (tylko `id`, tekst/termin i etykieta) obecnie `stance_to_label.csv` |
| `validation_csv/` | arkusze `.xlsx` do ręcznego etykietowania: `emotion_to_label.xlsx` (emocje), `stance_to_label.xlsx` (nastawienie wobec obozu) |

### Foldery, które istnieją tylko lokalnie (poza gitem)

| Folder | Dlaczego go nie ma w repozytorium |
|---|---|
| `data/` | surowe pliki `.jsonl` z Arctic Shift. GitHub ma limit 100 MB na plik, a pliki są dużo większe. Folder tworzy `scripts/download_subreddit.py` przed pobraniem go nie ma |
| `processed/` | wyniki pośrednie (parquety, tabele, wyniki modeli) – duże i w całości odtwarzalne notebookami, więc ignorowane przez `.gitignore`. `RESULTS_DIR` (`processed/results/`) to miejsce na wszystkie tabele wynikowe |
| `git_exclude/` | prywatne notatki robocze i archiwum starego kodu |

## Uruchamianie lokalnie

```
uv sync
```

Wymagany Python ≥ 3.13. Notebooki otwiera się z katalogu ich folderu (importy `from src...` zakładają, że katalog nadrzędny to katalog repozytorium).
`torch` jest instalowany z indeksu CUDA 12.8 (`pytorch-cu128`).

Surowe dane pobiera się skryptem:

```
python scripts/download_subreddit.py
```

## Uruchamianie w Google Colab

Cały folder repozytorium (razem z `data/` i `processed/`) leży na Dysku Google w `MyDrive/Licencjat`.
Pierwsza komórka wersji `_colab` montuje Dysk i przechodzi do folderu notebooka. Do Colaba wystarczą `src/`, `labels/`,
`processed/sample.parquet`, `processed/h4a/mentions.parquet` i sam notebook. Wyniki skopiuj z powrotem do lokalnego `processed/`.

## Kolejność uruchamiania

L – lokalnie, C – Google Colab z GPU (lub lokalnie, jeśli jest karta).
Kroki w tej samej grupie, które nie zależą od siebie, można uruchamiać w dowolnej kolejności.

| # | Notebook / skrypt | Gdzie | Co robi | Zapisuje | Wymaga |
|---|---|---|---|---|---|
| 0 | `scripts/download_subreddit.py` | L | pobranie komentarzy z API | `data/*.jsonl` | – |
| 1.1 | `eda/01_raw_scan` | L | skan surowych plików: rekordy, daty, schemat, autorzy | `processed/phases.csv`, `processed/scan/` | 0 |
| 1.2 | `eda/02_raw_eda` | L | liczebności, braki i długości w surowych danych | `processed/eda/raw_*.csv` | 1.1 |
| 1.3 | `extra/01_bots` | L | wybór kont botów i progu liczby komentarzy na konto | `processed/bot_candidates.csv`, `bots_review.csv` | 1.1 |
| – | ręcznie | – | lista botów i próg w `src/config.py` | – | 1.3 |
| 2.1 | `cleaning/01_cleaning_all` | L (kilka–kilkanaście godzin) | czyszczenie 30 plików pomija pliki, które już istnieją | `processed/clean/`, `weekly_counts/`, `funnel/` | 0, lista botów |
| 2.2 | `eda/03_clean_eda` | L | wykonalność, lejek, retencja po czyszczeniu | `processed/eda/*.csv` | 2.1 |
| 3.1 | `features/01_sample` | L | losuje do `MAX_PER_WEEK` komentarzy na subreddit i tydzień | `processed/sample.parquet` | 2.1 |
| 3.2 | `eda/04_sample_eda` | L | liczebność i długość próby | `processed/eda/` | 3.1 |
| 3.3 | `features/02_emotions` | C (GPU) | emocje (7 prawdopodobieństw) i sentyment (3 klasy) | `processed/emotions/`, `processed/sentiment/` | 3.1 |
| 3.4 | `features/03_weekly_emotions` | L | agregacja tygodniowa i fazowa | `weekly_emotions.csv`, `phase_emotions*.csv` | 3.3 |
| 3.5 | `eda/05_emotions_eda` | L | emocje i usunięte komentarze w czasie i fazach | `processed/eda/` | 3.4 |
| 4.1 | `extra/03_validation_emotions` (sekcja 2) | L | eksport 400 komentarzy do ręcznego etykietowania | `processed/validation/` | 3.3 |
| 4.2 | ręcznie (`validation_csv/emotion_to_label.xlsx`) | – | etykietowanie, zapis `labels/emotion_labels.csv` | `labels/` | 4.1 |
| 4.3 | `extra/03_validation_emotions` (sekcje 4–5) | L | F1, macierz pomyłek, korelacja z sentymentem | `processed/results/validation_*.csv` | 3.4, 4.2 |
| 5.1 | `h1/h1_analysis` | L | tabele H1 | `processed/results/h1_*.csv` | 3.4 |
| 5.2 | `h2/h2_analysis` | L | tabele H2 | `processed/results/h2_*.csv` | 3.4 |
| 5.3 | `h3/h3_analysis` | L | tabele H3 | `processed/results/h3_*.csv` | 3.4 |
| 6.1 | `extra/02_camp_terms` | L | liczba komentarzy z każdym terminem obozu | `processed/results/camp_terms_*.csv` | 3.1 |
| 6.2 | `h4a/h4a_mentions` | L | komentarze wspominające dokładnie jeden obóz | `processed/h4a/mentions.parquet` | 3.1, 6.1 |
| 6.3 | `extra/04_validation_stance` lub `_colab` | C (GPU) | kappa i F1 modelu NLI na etykietach ręcznych | `processed/results/validation_stance.csv` | `labels/stance_*.csv` |
| 6.4 | `h4a/h4a_stance` lub `h4a_stance_colab` | C (GPU) | `p_entail`, `critical` dla wzmianek | `processed/h4a/stance_*.parquet` | 6.2 (po 6.3) |
| 6.5 | `h4a/h4a_analysis` | L | WPA, porównanie 2020 + 2024 z 2012 + 2016 | `processed/results/h4a_*.csv` | 6.4 |
| 7.1 | `h4b/h4b_analysis` | L (długi, `n_jobs=-1`) | TF-IDF + regresja logistyczna, powtórzenia dla 4 cykli | `processed/results/h4b_*.csv` | 3.1 |
| 7.2 | `extra/05_validation_h4b_model` | L | porównanie modeli, krzywa uczenia, poziom przypadku | `processed/results/h4b_check_*.csv` | 3.1 |
| 8 | `extra/06_topics` lub `_colab` (opcjonalnie) | L lub C | tematy (BERTopic, eksploracyjnie) | `processed/results/topics_*.csv` | 3.1 |
| 9.1 | `charts/01_cycle_design` | L | schemat cyklu i fazy | `charts/figures/` | – |
| 9.2 | `charts/02_eda_figures` | L | rysunki EDA | `charts/figures/` | 1.2, 2.1 |
| 9.3 | `charts/03_emotions_figures` | L | rysunki emocji | `charts/figures/` | 3.4, 5.3 |
| 9.4 | `charts/04_polarization_figures` | L | rysunki polaryzacji | `charts/figures/` | 6.5, 7.1 |
| 10 | `h1/h1_statistics` … `h4b/h4b_statistics` | L | analiza statystyczna – szkielety, uruchamiać po wyborze testów | – | odpowiednia analiza |
