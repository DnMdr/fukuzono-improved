import datetime
from dataclasses import dataclass
from pathlib import Path

"""Configurazioni e parametri per l'analisi dei dati tramite @dataclass."""

@dataclass
class parametri:
    inizio_analisi: datetime.datetime
    encoding_csv: str
    smoothing_technique: int
    finestra_savgol: int
    polinomio_savgol: int
    finestra_media_mobile: int
    v_stazionaria: float
    soglia_fit_alpha: float
    coeff_correzione: float
    col_velocita: str
    file_csv: Path

@dataclass
class configurazione_grafico:
    filter_name: str
    figsize: tuple
    col_velocita: str
    col_temp: str
    col_pioggia: str
    ylim_emergenza: tuple