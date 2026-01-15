import numpy as np
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from src.config import Parametri
from src.config import FilteringParams

def applica_fukuzono_qi(df, params:Parametri, filtering_params:FilteringParams):
    """
        Applica il metodo di Fukuzono con correzione statistica di Qi et al. ed angolo tangente.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame con i dati di data, velocità, temperatura, pioggia e hours_elapsed.
        params : parametri
            Parametri di configurazione per l'analisi.

        Returns
        -------
        df_calc : pd.DataFrame
            DataFrame con le colonne calcolate.
        previsione : dict or None
            Dizionario con le previsioni calcolate.
        df_fit : pd.DataFrame
            DataFrame con i dati usati per il fitting (alpha > 80).
        smoothing_name : str
            Nome del filtro applicato.
    """


    smoothing_name = "Filtro SG" if filtering_params.smoothing_technique == 1 else "Media Pesata"
    if filtering_params.smoothing_technique == 1:
        df['v_smooth'] = savgol_filter(v_clean, window_length=filtering_params.finestra_savgol, polyorder=filtering_params.polinomio_savgol)
    else:
        df['v_smooth'] = v_clean.rolling(window=filtering_params.finestra_media_mobile).mean()
    # Rimuoviamo valori negativi o nulli (fisicamente impossibili o fermi) per 1/V la soglia viene posta a 0.001 mm
    # Usiamo una copia per non corrompere l'indice
    df_calc = df[df['v_smooth'] > 0.001].copy()
    
    # 2. Calcolo Velocità Inversa (1/V)
    df_calc['inv_v'] = 1.0 / df_calc['v_smooth']
    
    # 3. Calcolo Angolo Tangente (Alpha)
    # Modello descritto da Qi et al. l'angolo Alpha quantifica la ripidità dell'accelerazione
    # Formula: arctan(V_corrente / V_stazionaria) convertita in gradi
    df_calc['alpha'] = np.degrees(np.arctan(df_calc['v_smooth'] / params.v_stazionaria))
    
    # 4. Identificazione Fase di Accelerazione per il Fitting
    # La variabile SOGLIA_FIT_ALPHA è dichiarata dall'utente
    mask_fit = (df_calc['alpha'] >= params.soglia_fit_alpha)
    df_fit = df_calc[mask_fit].copy()
    
    # Dichiarazione variabili per la predizione
    previsione = None
    model = None
    
    # Eseguiamo la regressione solo se abbiamo abbastanza punti in zona critica (>10 punti)
    # ovvero abbiamo abbastanza punti che soddisfino il valore minimo di angolo dichiarato in SOGLIA_FIT_ALPHA
    if len(df_fit) > 10:
        X = df_fit['hours_elapsed'].values.reshape(-1, 1)
        y = df_fit['inv_v'].values
        
        # Il codice modella i punti (tempo,1/V) come una retta (y=mx+q).
        model = LinearRegression()
        model.fit(X, y)
        
        # Se la pendenza (coef_) è negativa, la velocità inversa sta scendendo, ci si avvicina al crollo e la funzione di previsione di attiva
        # onset point
        # nel grafico si nota il punto di flesso antecedente al crollo
        if model.coef_[0] < 0:
            # Calcolo intersezione asse X (1/V = 0)
            t_zero_hours = -model.intercept_ / model.coef_[0]
            
            # Calcolo orario data base
            t_start_date = df['Data'].iloc[0]
            t_linear_date = t_start_date + timedelta(hours=t_zero_hours)
            
            # Applicazione coefficiente correttivo secondo Qi et al.
            last_observed_date = df_calc['Data'].iloc[-1]
            #Calcola quante ore mancano al crollo secondo la retta calcolata con Fukuzono
            hours_remaining_linear = t_zero_hours - df_calc['hours_elapsed'].iloc[-1]
            
            if hours_remaining_linear > 0:
                # Moltiplica il tempo rimanente per il coefficiente di correzione dichiarato
                hours_corrected = hours_remaining_linear * params.coeff_correzione
                # Enuncia la predizione corretta e crea un dizionario con tutte le date calcolate in funzione
                t_final_prediction = last_observed_date + timedelta(hours=hours_corrected)
                
                previsione = {
                    't_linear': t_linear_date,
                    't_corrected': t_final_prediction,
                    'slope': model.coef_[0],
                    'intercept': model.intercept_
                }
    # La funzione ritorna il dataframe pandas con tutte le colonne calcolate, il dizionario con le date di previsione
    return df_calc, previsione, df_fit, smoothing_name
    # il dataframe con i soli punti utilizzati per il calcolo della previsione (alpha>80) e il nome del filtro