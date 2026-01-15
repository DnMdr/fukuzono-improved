from charset_normalizer import detect

def rileva_encoding(file_path: str) -> str:
    """
    Rileva l'encoding di un file di testo.

    Parameters
    ----------
    file_path : str
        Percorso del file di testo.

    Returns
    -------
    str
        L'encoding rilevato del file.
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = detect(raw_data)
        return result['encoding']