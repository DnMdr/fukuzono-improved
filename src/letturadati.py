import pandas as pd
from src.config import parametri

def processa_dataset(params:parametri):
    """
    Funzione per caricare e processare il dataset.

    Parameters
    ----------
    params : parametri
        Parametri di configurazione di pandas.

    Returns
    -------
    pd.DataFrame
        DataFrame processato con i dati pronti per l'analisi.
    """

        # L'encoding non è utf-8 ma latin1 nel caso del csv fornito dallo studio geologico
    df = pd.read_csv(params.file_csv, encoding='latin1')
    df = pd.read_csv(params.file_csv, encoding=params.encoding_csv)
    
    # Conversione Data, necessaria per convertire il valore della cella Data del csv da stringa a timestamp
    # errors='coerce' applica NaT alle celle con valori errati eliminandole
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    
    # Il filtro temporale elimina le righe antecedenti la data decisa per l'analisi, 
    # sort_values le pone in ordine cronologico e reset_index fa ripartire l'indice in caso di righe eliminate
    df = df[df['Data'] >= params.inizio_analisi].sort_values('Data').reset_index(drop=True)
    
    # Calcolo tempo trascorso in ore (utile per la regressione)
    # t_start identifica la prima lettura temporale che viene succesivamente sottratta ad ogni valore temporale
    # essendo il valore in secondi si divide per 3600.0 per ottenere i secondi di ogni misura a partire dallo zero prefissato
    # la funzione di regressione lineare di Fukuzono ha bisogno di uno zero a partenza
    t_start = df['Data'].iloc[0]
    df['hours_elapsed'] = (df['Data'] - t_start).dt.total_seconds() / 3600.0
    
    return df