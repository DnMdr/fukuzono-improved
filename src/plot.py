import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Optional

from src.config import GraphicsParams, FailurePrevision

def _plot_inverse_velocity(ax, df_res: pd.DataFrame, df_fit: pd.DataFrame, 
                           previsione: Optional[FailurePrevision], config: GraphicsParams):
    """Gestisce il plot della Velocità Inversa (1/V) e della retta di regressione."""
    
    # 1. Dati storici calcolati (Grigio)
    ax.plot(df_res['data'], df_res['inv_v'], 'o', markersize=2, 
            color='gray', alpha=0.3, label='Dati Storici')
    
    # 2. Punti utilizzati per il calcolo (Blu)
    if not df_fit.empty:
        ax.plot(df_fit['data'], df_fit['inv_v'], '.', 
                color='blue', label='Fase Accelerazione (>Soglia)')

    # 3. Retta di Previsione (Rosso) - Solo se esiste una previsione valida
    if previsione:
        # Generiamo i punti della retta dal primo punto di fit fino al tempo lineare previsto
        hours_range = np.linspace(
            df_fit['hours_elapsed'].min(),
            (previsione.t_linear - df_res['data'].iloc[0]).total_seconds() / 3600,
            num=10
        )
        
        # y = mx + q
        y_pred = previsione.slope * hours_range + previsione.intercept
        x_dates = [df_res['data'].iloc[0] + timedelta(hours=h) for h in hours_range]
        
        ax.plot(x_dates, y_pred, 'r--', linewidth=2, label='Regressione Lineare')
        
        # Linea verticale e testo data crollo
        ax.axvline(previsione.t_corrected, color='red', linewidth=2)
        
        # Posizionamento dinamico del testo (90% dell'altezza asse Y)
        y_pos = ax.get_ylim()[1] * 0.9 if ax.get_ylim()[1] > 0 else 1
        ax.text(previsione.t_corrected, y_pos, 
                f" CROLLO PREVISTO\n {previsione.t_corrected.strftime('%d/%m/%y %H:%M')}", 
                color='red', fontweight='bold', ha='left')

    ax.set_ylabel('Velocità Inversa 1/V [h/mm]', fontweight='bold')
    ax.set_title(f"Analisi Fukuzono ({config.filter_name}) + correzione Qi et al.", fontsize=14)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

def _plot_alpha(ax, df_res: pd.DataFrame, config: GraphicsParams):
    """Gestisce il plot dell'Angolo Tangente e le fasce colorate di allerta."""
    
    ax.plot(df_res['data'], df_res['alpha'], color='orange', linewidth=1.5, label='Angolo α')

    # Fasce semantiche (Sicurezza -> Allerta -> Emergenza)
    ax.axhspan(0, 80, color='green', alpha=0.1)
    ax.axhspan(80, 85, color='yellow', alpha=0.2)
    ax.axhspan(85, 90, color='red', alpha=0.2)

    ax.set_ylabel('Angolo Tangente [°]', fontweight='bold')
    ax.set_ylim(config.ylim_emergenza)
    ax.grid(True, alpha=0.5)

def _plot_environment(ax, df_main: pd.DataFrame, config: GraphicsParams):
    """
    Temperatura (asse SX, basso) e Pioggia Inversa (asse DX, alto).
    """
    # Temperatura (Asse Sinistro)
    color_temp = 'tab:red'
    # Disegniamo la linea dello zero termico (importante per il gelo)
    ax.axhline(0, color='blue', linestyle=':', alpha=0.5, linewidth=1)
    
    ax.plot(df_main['data'], df_main['temp_C'], color=color_temp, linewidth=1.2, label='Temperatura')
    
    # Impostiamo i limiti della temperatura nei 2/3 superiori
    t_min = df_main['temp_C'].min()
    t_max = df_main['temp_C'].max()
    t_range = t_max - t_min
    # Aggiunta spazio per visualizzare la pioggia
    ax.set_ylim(t_min - 2, t_max + (t_range * 0.5)) 
    
    ax.set_ylabel('Temp [°C]', color=color_temp, fontweight='bold')
    ax.tick_params(axis='y', labelcolor=color_temp)
    ax.grid(True, alpha=0.3)

    # Pioggia (Asse Destro)
    ax_rain = ax.twinx()
    color_rain = 'tab:blue'
    
    # Calcolo cumulata temporale 24h
    if not df_main.index.name == 'data': 
        df_temp = df_main.set_index('data') # Serve indice datetime per rolling temporale
    else:
        df_temp = df_main
        
    rain_cum = df_temp['pioggia_mm'].fillna(0).rolling('24h', min_periods=1).sum().values
    
    # Plot a barre o area
    ax_rain.fill_between(df_main['data'], rain_cum, 0, color=color_rain, alpha=0.3, label='Pioggia 24h')
    
    # Scala Pioggia 1/3 superiore
    max_rain = np.nanmax(rain_cum)
    top_lim = max_rain * 3 if max_rain > 10 else 30 # Default un po' più alto
    
    # Impostiamo i limiti della pioggia per farla stare nel 1/3 superiore
    ax_rain.set_ylim(top_lim, 0)
    
    ax_rain.set_ylabel('Pioggia Cumulata 24h [mm]', color=color_rain, fontweight='bold')
    ax_rain.tick_params(axis='y', labelcolor=color_rain)
    
    # Eliminiamo griglia asse pioggia
    ax_rain.grid(False)

def plot_fukuzono(df_res: pd.DataFrame, df_main: pd.DataFrame, df_fit: pd.DataFrame, 
                  previsione: Optional[FailurePrevision], config: GraphicsParams) -> plt.Figure:
    """
    Genera il report grafico completo 
    con 3 pannelli: Velocità Inversa, Angolo Tangente, Dati ambientali (Temp + Pioggia).
    """
    
    fig = plt.figure(figsize=config.figsize)
    # Layout a griglia: 3 righe, la prima è alta il doppio delle altre
    gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.15)
    
    # Creazione assi
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax3 = fig.add_subplot(gs[2], sharex=ax1)

    # Esecuzione funzioni di plot
    _plot_inverse_velocity(ax1, df_res, df_fit, previsione, config)
    _plot_alpha(ax2, df_res, config)
    _plot_environment(ax3, df_main, config)
    
    # Formattazione asse X (solo sull'ultimo grafico per pulizia)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H'))
    
    return fig