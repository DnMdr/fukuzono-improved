
def stampa_report_testuale(df_res, df_fit_used, previsione, params):
    """
    Stampa un report testuale con i risultati dell'analisi previsionale.

    Parameters
    ----------
    df_res : pd.DataFrame
        DataFrame con i risultati dell'analisi.
    df_fit_used : pd.DataFrame
        DataFrame con i dati usati per il fitting.
    prev : dict or None
        Dizionario con le previsioni calcolate o None se non calcolabili.
    params : parametri
        Parametri di configurazione.
    """
    print("-" * 50)
    print("REPORT ANALISI PREVISIONALE")
    print("-" * 50)

    if previsione:
        # Formattazione date
        data_ultimo = df_res['Data'].iloc[-1].strftime('%d-%m-%Y %H:%M:%S')
        data_linear = previsione['t_linear'].strftime('%d-%m-%Y %H:%M:%S')
        data_corr = previsione['t_corrected'].strftime('%d-%m-%Y %H:%M:%S')
        
        # Per la differenza di tempo, usiamo la divisione intera per togliere i microsecondi
        anticipo = previsione['t_corrected'] - df_res['Data'].iloc[-1]
        # Trasformiamo in stringa e tagliamo i decimali
        durata_str = str(anticipo).split(".")[0] 

        print(f"Data Ultimo Dato Disponibile:{data_ultimo}")
        print(f"Previsione Lineare (Fukuzono):{data_linear}")
        print(f"Previsione Corretta (Fattore {params.coeff_correzione}):{data_corr}")
        print(f"Differenza tra previsione e crollo effettivo:{durata_str}")
    else:
        print("Non è stato possibile calcolare una previsione.")
        
        # Calcoliamo il massimo angolo per mostrarlo comunque
        max_alpha_rilevato = df_res['alpha'].max()
        
        # CASO 1: Nessun punto ha mai superato la soglia
        if len(df_fit_used) == 0:
            print(f"Motivo: L'angolo tangente non ha mai superato la soglia minima impostata ({params.soglia_fit_alpha}°).")
            print(f"Massimo angolo rilevato: {max_alpha_rilevato:.2f}°")
            
        # CASO 2: La soglia è stata superata ma per troppo poco tempo
        elif len(df_fit_used) <= 10:
            print(f"Motivo: CRITICITÀ RILEVATA (Max: {max_alpha_rilevato:.2f}°), ma i dati sono insufficienti per una stima affidabile.")
            print(f"Dettaglio: Trovati solo {len(df_fit_used)} punti sopra la soglia.")
            print("Suggerimento: La frana sta accelerando molto velocemente o il filtro è troppo aggressivo.")
            
        # CASO 3: Ci sono i punti, ma la retta punta dalla parte sbagliata
        else:
            print("Motivo: Punti sufficienti, ma la tendenza non indica un crollo (velocità in diminuzione?).")