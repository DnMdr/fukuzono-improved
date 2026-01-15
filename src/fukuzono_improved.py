import numpy as np
import pandas as pd
from typing import Optional, Tuple
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from src.config import FailurePrevision, Parametri, FilteringParams, FukuzonoAnalysisResult

def kalman_filter_1d(series: pd.Series, q: float, r: float) -> pd.Series:
    """Implementazione lineare del filtro di Kalman per segnali monodimensionali."""
    n = len(series)
    x_hat = np.zeros(n)      # Stima dello stato
    p = np.zeros(n)          # Errore di stima
    
    x_hat_minus = 0.0        # Stima a priori
    p_minus = 1.0            # Errore a priori
    
    # Valore iniziale
    x_hat[0] = series.iloc[0]
    p[0] = 1.0
    
    for k in range(1, n):
        # Fase di Predict
        x_hat_minus = x_hat[k-1]
        p_minus = p[k-1] + q
        
        # Fase di Update (Correction)
        k_gain = p_minus / (p_minus + r)
        x_hat[k] = x_hat_minus + k_gain * (series.iloc[k] - x_hat_minus)
        p[k] = (1 - k_gain) * p_minus
        
    return pd.Series(x_hat, index=series.index)

def applica_smoothing(series: pd.Series, f_params: FilteringParams) -> Tuple[pd.Series, str]:
    if f_params.smoothing_technique == 1:
        v_smooth = savgol_filter(series, f_params.finestra_savgol, f_params.polinomio_savgol)
        return pd.Series(v_smooth, index=series.index), "Filtro Savitzky-Golay"
    
    elif f_params.smoothing_technique == 2:
        v_smooth = series.rolling(window=f_params.finestra_media_mobile, center=True).mean()
        return v_smooth, "Media Mobile"
    
    elif f_params.smoothing_technique == 3:
        v_smooth = kalman_filter_1d(series, f_params.kalman_q, f_params.kalman_r)
        return v_smooth, "Filtro di Kalman"
    
    return series, "Nessun Filtro"

def calcola_regressione_critica(df_fit: pd.DataFrame, df_calc: pd.DataFrame, params: Parametri) -> Optional[FailurePrevision]:
    """Isola la logica matematica della regressione di Qi et al."""
    if len(df_fit) <= 10:
        return None

    X = df_fit['hours_elapsed'].values.reshape(-1, 1)
    y = df_fit['inv_v'].values
    
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0]

    # Procediamo solo se c'è accelerazione (pendenza negativa di 1/V)
    if slope >= 0:
        return None

    t_zero_hours = -model.intercept_ / slope
    t_start_date = df_calc['data'].iloc[0] # Assumiamo Data sia presente
    
    # Logica di correzione Qi et al.
    last_h = df_calc['hours_elapsed'].iloc[-1]
    hours_remaining_linear = t_zero_hours - last_h
    
    if hours_remaining_linear <= 0:
        return None

    hours_corrected = hours_remaining_linear * params.coeff_correzione
    last_date = df_calc['data'].iloc[-1]

    return FailurePrevision(
        t_linear=t_start_date + timedelta(hours=t_zero_hours),
        t_corrected=last_date + timedelta(hours=hours_corrected),
        slope=slope,
        intercept=model.intercept_
    )

def fukuzono_qi(df: pd.DataFrame, params: Parametri, f_params: FilteringParams) -> FukuzonoAnalysisResult:
    """Funzione orchestratrice: pulita e leggibile."""
    
    # 1. Smoothing (Utilizziamo v_clean che deve essere passato o calcolato)
    v_clean = df["v_clean"] # o la logica di pulizia precedente
    v_smooth, smoothing_name = applica_smoothing(v_clean, f_params)
    
    # 2. Feature Engineering (Metodo chaining per essere Pythonic)
    df_calc = (df.assign(v_smooth=v_smooth)
               .query("v_smooth > 0.001")
               .assign(
                   inv_v = lambda x: 1.0 / x.v_smooth,
                   alpha = lambda x: np.degrees(np.arctan(x.v_smooth / params.v_stazionaria))
               )).copy()

    # 3. Identificazione fase accelerazione
    df_fit = df_calc[df_calc['alpha'] >= params.soglia_fit_alpha].copy()
    
    # 4. Regressione e Previsione
    previsione = calcola_regressione_critica(df_fit, df_calc, params)

    return FukuzonoAnalysisResult(
        df_calc=df_calc,
        df_fit=df_fit,
        previsione=previsione,
        smoothing_name=smoothing_name
    )