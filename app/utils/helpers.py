import re

def extract_values_from_text(text: str) -> dict:
    """
    Returns a dict of suspected categories to found matches based on common regexes.
    """
    results = {}

    # 15-char GSTIN format (e.g., 27AABCU9603R1ZX)
    gstin_pattern = r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b'
    gstins = re.findall(gstin_pattern, text)
    if gstins:
        results['GSTIN'] = gstins

    # Container No: 4 letters + 7 digits (e.g., MSCU1234567)
    container_pattern = r'\b[A-Z]{4}[0-9]{7}\b'
    containers = re.findall(container_pattern, text)
    if containers:
        results['Container No'] = containers

    # IEC Code: 10 digits
    iec_pattern = r'\b[0-9]{10}\b'
    iecs = re.findall(iec_pattern, text)
    if iecs:
        results['IEC Code'] = iecs

    # Dates: DD/MM/YYYY or DD-MM-YYYY
    date_pattern = r'\b\d{2}[/-]\d{2}[/-]\d{4}\b'
    dates = re.findall(date_pattern, text)
    if dates:
        results['Dates'] = dates

    return results
