import pandas as pd
from src.config import Parametri

def dataframe_init(parametri:Parametri) -> pd.DataFrame:
    """
    Inizializza il DataFrame con le colonne necessarie per l'analisi.

    Parameters
    ----------
    parametri : parametri
        Parametri di configurazione.

    Returns
    -------
    pd.DataFrame
        DataFrame inizializzato con le colonne richieste.
    """
    # Creazione DataFrame con le colonne specificate nei parametri      
    cols_raw = [parametri.col_data,
               parametri.col_velocita,
               parametri.col_temp,
               parametri.col_pioggia] 
    
    df = pd.read_csv(parametri.file_csv,
                     usecols=cols_raw,
                     encoding=parametri.encoding_csv)
    
    mappa_nomi = {
        parametri.col_data: 'data',
        parametri.col_velocita: 'v_clean',
        parametri.col_temp: 'temp_C',
        parametri.col_pioggia: 'pioggia_mm'
    }
    df = df.rename(columns=mappa_nomi)

    df['data'] = pd.to_datetime(df['data'])
        
    # Filtro temporale in base alla data di inizio analisi
    maschera = df['data'] >= parametri.inizio_analisi
    df = df.loc[maschera].reset_index(drop=True).copy()   
     
    # Calcolo del tempo trascorso in ore
    MINUTES_PER_ROW = 5
    MINUTES_IN_HOUR = 60
    df['hours_elapsed'] = (df.index * MINUTES_PER_ROW) / MINUTES_IN_HOUR

    # Gestione valori mancanti
    df['pioggia_mm'] = df['pioggia_mm'].fillna(0.0)
    df['temp_C'] = df['temp_C'].interpolate(method='linear')
    df['v_clean'] = df['v_clean'].interpolate(method='linear')  
        
    return df