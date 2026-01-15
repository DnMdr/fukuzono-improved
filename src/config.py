import datetime
import pandas as pd
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

"""Configurazioni e parametri per l'analisi dei dati tramite @dataclass."""

@dataclass
class Parametri:
    inizio_analisi: datetime.datetime
    encoding_csv: str
    v_stazionaria: float
    soglia_fit_alpha: float
    coeff_correzione: float
    file_csv: Path
    col_data: str
    col_velocita: str
    col_temp: str
    col_pioggia: str

@dataclass
class FilteringParams:
    smoothing_technique: int
    finestra_savgol: int
    polinomio_savgol: int
    finestra_media_mobile: int
    kalman_q: float
    kalman_r: float

@dataclass
class GraphicsParams:
    filter_name: str
    figsize: tuple
    col_velocita: str
    col_temp: str
    col_pioggia: str
    ylim_emergenza: tuple
    
@dataclass
class FailurePrevision:
    t_linear: datetime
    t_corrected: datetime
    slope: float
    intercept: float

@dataclass
class FukuzonoAnalysisResult:
    df_calc: pd.DataFrame
    df_fit: pd.DataFrame
    previsione: Optional[FailurePrevision]
    smoothing_name: str