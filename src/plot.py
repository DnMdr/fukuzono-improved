import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta
from src.config import configurazione_grafico

def plot_fukuzono(df_res, df_main, df_fit_used, previsione, config:configurazione_grafico):
    """
    Genera il set di grafici per l'analisi Fukuzono, l'allerta e i dati ambientali.

    Parameters
    ----------
    df_res : pd.DataFrame
        DataFrame con i risultati dell'analisi Fukuzono.
    df_main : pd.DataFrame
        DataFrame principale con tutti i dati.
    df_fit_used : pd.DataFrame
        DataFrame con i dati usati per il fitting.
    previsione : dict or None
        Dizionario con le previsioni calcolate o None se non calcolabili.
    config : configurazione_grafico
        Configurazione grafica.

    Returns
    -------
    matplotlib.figure.Figure
        File png contenente i grafici generati.
    """

    # Creazione base grafico
    fig = plt.figure(figsize=config.figsize)
    # Divide la tela del grafico in tre righe e 1 colonna, imposta i rapporti e hspace è la distanza in altezza tra i 3 grafici
    gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.3)

    # =============================================================================
    # GRAFICO 1: Velocità Inversa e Previsione
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(df_res['Data'], df_res['inv_v'], 'o', markersize=2, color='gray', alpha=0.3, label='Dati Calcolati')
    # Vengono evidenziati in blu i punti utilizzati per la previsione (alpha>80°)
    # l'if previene l'errore in caso lo script non trovi punti adatti al calcolo nel range previsto
    if not df_fit_used.empty:
        ax1.plot(df_fit_used['Data'], df_fit_used['inv_v'], '.', color='blue', label='Dati Fase Accelerazione (>80°)')

    # Retta di previsione
    if previsione:
        # Creiamo una linea temporale estesa fino alla previsione
        t_future = previsione['t_linear']
        x_range = np.linspace(df_fit_used['hours_elapsed'].min(), 
                            (t_future - df_main['Data'].iloc[0]).total_seconds()/3600, 10)
        y_pred = previsione['slope'] * x_range + previsione['intercept']
        
        # Convertiamo x_range in datetime per il plot
        x_dates = [df_main['Data'].iloc[0] + timedelta(hours=h) for h in x_range]
        
        ax1.plot(x_dates, y_pred, 'r--', linewidth=2, label='Regressione Fukuzono (Lineare)')
        
        # Retta verticale previsione crollo con data
        ax1.axvline(previsione['t_corrected'], color='red', linewidth=2, linestyle='-')
        ax1.text(previsione['t_corrected'], ax1.get_ylim()[1]*0.9, 
                f" CROLLO PREVISTO\n {previsione['t_corrected'].strftime('%d/%m/%y %H:%M')}", 
                color='red', fontweight='bold')

    # Formattazione grafico
    ax1.set_ylabel('Velocità Inversa 1/V [h/mm]', fontweight='bold')
    ax1.set_title(f"Metodo Fukuzono Avanzato ({config.filter_name} + Correzione Qi et al.) - {config.col_velocita}", fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # =============================================================================
    # GRAFICO 2: Angolo Tangente con fasce di allerta 
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    # Plot della variazione dell'angolo alpha
    ax2.plot(df_res['Data'], df_res['alpha'], color='orange', linewidth=1.5)

    # Fasce di allerta
    ax2.axhspan(0, 80, color='green', alpha=0.1, label='Sicurezza')
    ax2.axhspan(80, 85, color='yellow', alpha=0.2, label='Allerta')
    ax2.axhspan(85, 90, color='red', alpha=0.2, label='Emergenza')

    # Formattazione grafico
    ax2.set_ylabel('Angolo Tangente [°]', fontweight='bold')
    # Varia questo intervallo per un focus sulle fasce di allerta ed emergenza
    ax2.set_ylim(config.ylim_emergenza)
    ax2.legend(loc='lower right')
    ax2.grid(True)

    # =============================================================================
    # GRAFICO 3: Contesto Ambientale temperatura roccia e precipitazioni
    ax3 = fig.add_subplot(gs[2], sharex=ax1)

    # Temperatura
    color_temp = 'tab:red'
    # Convertiamo in numeri i valori di temperatura per evitare errori di lettura e uso errors='coerce' per eliminare le celle non valide
    temp_data = pd.to_numeric(df_main[config.col_temp], errors='coerce')
    ax3.plot(df_main['Data'], temp_data, color=color_temp, linewidth=1, label='Temperatura Roccia')
    ax3.set_ylabel('Temp [°C]', color=color_temp)
    ax3.tick_params(axis='y', labelcolor=color_temp)

    # Pioggia
    # .twinx crea un asse x gemello a destra del grafico ax3
    ax3b = ax3.twinx()
    color_rain = 'tab:blue'

    # Applico alle celle NaN il valore 0 altrimenti matplotlib non riesce a creare gli estremi del plot
    pioggia_clean = df_main[config.col_pioggia].fillna(0)

    # Pioggia cumulata sulle 24h
    # min_periods=1 garantisce che calcoli qualcosa anche all'inizio del file
    pioggia_24 = pioggia_clean.rolling(window=288, min_periods=1).sum()

    # Plot
    ax3b.fill_between(df_main['Data'], pioggia_24, color=color_rain, alpha=0.3, label='Pioggia Cumulata 24h')
    ax3b.set_ylabel('Pioggia 24h [mm]', color=color_rain)
    ax3b.tick_params(axis='y', labelcolor=color_rain)

    # Scala asse y, il valore massimo è il valore della cumulata nelle 24h
    max_p = pioggia_24.max()

    # Controllo di sicurezza: se max_p è ancora nan o 0
    if pd.isna(max_p) or max_p == 0:
        ax3b.set_ylim(10, 0) # Scala di default
    else:
        ax3b.set_ylim(max_p * 3, 0) # Scala dinamica (ax3 per lasciare spazio alla temperatura)

    ax3.set_title('Temperatura Roccia e Precipitazioni')
    ax3.grid(True, alpha=0.3)
    
    return fig