import pandas as pd
from datetime import datetime
from src.config import Parametri, FukuzonoAnalysisResult

def stampa_report_calibrazione(risultato: FukuzonoAnalysisResult, params: Parametri) -> None:
    """
    Report ottimizzato per il back-testing. 
    Confronta il crollo reale (ultimo dato) con le stime lineari e corrette.
    """

    nome_file = params.file_csv.name
    
    print("\n" + "="*65)
    print(f"ANALISI DI CALIBRAZIONE: {nome_file}")
    print("="*65)

    if not risultato.previsione:
        print("ANALISI FALLITA: Impossibile generare una previsione per questo dataset.")
        print("Controllare soglia_fit_alpha o la qualità del segnale filtrato.")
        return

    # Estrazione dati per chiarezza
    prev = risultato.previsione
    df = risultato.df_calc
    
    # GROUND TRUTH: Il crollo reale è la fine dei dati
    t_reale = df['data'].iloc[-1]
    
    # CALCOLO ERRORI (Delta)
    # Delta > 0: La previsione è in ritardo rispetto al crollo (pericoloso)
    # Delta < 0: La previsione è in anticipo rispetto al crollo (conservativo)
    err_lineare = prev.t_linear - t_reale
    err_corretto = prev.t_corrected - t_reale

    # Formattazione per la stampa
    def format_td(td):
        """Formatta il timedelta in modo leggibile."""
        tot_minuti = int(td.total_seconds() / 60)
        segno = "+" if tot_minuti >= 0 else "-"
        abs_min = abs(tot_minuti)
        ore = abs_min // 60
        minuti = abs_min % 60
        return f"{segno}{ore}h {minuti}m ({tot_minuti} min)"

    print(f"MOMENTO CROLLO REALE (Fine Dati):  {t_reale.strftime('%d/%m/%Y %H:%M:%S')}")
    print("-" * 65)
    
    print(f"PREVISIONE FUKUZONO (Lineare):")
    print(f"Data stimata:  {prev.t_linear.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"ERRORE (ΔL):   {format_td(err_lineare)}")
    
    print(f"\nPREVISIONE CORRETTA (Qi et al.):")
    print(f"Coefficiente:  {params.coeff_correzione}")
    print(f"Data stimata:  {prev.t_corrected.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"ERRORE (ΔC):   {format_td(err_corretto)}")  
    print("-" * 65)
    
    # Valutazione della calibrazione
    if abs(err_corretto.total_seconds()) < abs(err_lineare.total_seconds()):
        miglioramento = (abs(err_lineare.total_seconds()) - abs(err_corretto.total_seconds())) / 60
        print(f"RISULTATO: Il coefficiente ha ridotto l'errore di {miglioramento:.1f} minuti.")
    else:
        print("ATTENZIONE: Il coefficiente attuale peggiora la stima o è sovra-corretto.")
    
    print("="*65 + "\n")