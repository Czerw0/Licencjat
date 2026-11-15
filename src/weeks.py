import pandas as pd

from src.config import PHASES, REFERENCE_YEARS


def to_week_start(created_utc):
    """Poniedziałek (UTC) tygodnia, w którym wypada znacznik czasu"""
    created = pd.to_datetime(created_utc, unit="s")
    return (created.dt.normalize() - pd.to_timedelta(created.dt.weekday, unit="D")).astype("datetime64[s]")


def assign_phase(week_start, cycle):
    """Faza tygodnia wg jego czwartku; week_start i cycle to serie o tym samym indeksie"""
    phase = pd.Series(None, index=week_start.index, dtype="object")
    thursday = week_start + pd.Timedelta(days=3)
    for phase_cycle, rows in PHASES.items():
        for name, start, end in rows:
            phase.loc[(cycle == phase_cycle) & (thursday >= start) & (thursday <= end)] = name
    phase.loc[cycle.isin(REFERENCE_YEARS) & (thursday.dt.year == cycle)] = "rok_referencyjny"
    return phase
