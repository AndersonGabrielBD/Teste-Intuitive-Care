import tabula
import pandas as pd
import zipfile
import os
import pdfplumber
from warnings import filterwarnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

filterwarnings('ignore')

#
EXPECTED_COLUMNS = [
    'Procedimento', 'RN (alteração)', 'VIGÊNCIA', "OD", "AMB", 
    "HCO", "HSO", "REF", "PAC", 'DUT', 'SUBGRUPO', 'GRUPO', 'CAPITULO'
]

REPLACEMENTS = {
    '\u2013': '-',  
    '\u2014': '-', 
    '\u2018': "'",  
    '\u2019': "'",  
    '\u201c': '"',  
    '\u201d': '"', 
    '\u00a0': ' ',
    "OD": " Seg. Odontológica",
    "AMB": " Seg. Ambulatorial"
}

def clean_text(text):
    if pd.isna(text):
        return text
    if isinstance(text, (str, bytes)):
        text = str(text)
        for k, v in REPLACEMENTS.items():
            text = text.replace(k, v)
    return text

def extract_with_tabula(pdf_path, attempts=2):
    encodings = ['utf-8', 'latin1']
    methods = [
        {'lattice': True, 'stream': False, 'guess': False},
        {'lattice': False, 'stream': True, 'guess': False},
        {'lattice': False, 'stream': False, 'guess': True}
    ]
    
    for attempt in range(attempts):
        encoding = encodings[attempt % len(encodings)]
        for method in methods:
            try:
                dfs = tabula.read_pdf(
                    pdf_path,
                    pages='all',
                    encoding=encoding,
                    pandas_options={'header': None},
                    multiple_tables=True,
                    **method
                )
                if dfs and len(dfs) > 0:
                    return dfs
            except Exception:
                continue
    return None

def process_page_with_pdfplumber(page):
    try:
        table = page.extract_table()
        return table if table else None
    except Exception:
        return None

def extract_with_pdfplumber(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with ThreadPoolExecutor() as executor:
                tables = list(executor.map(process_page_with_pdfplumber, pdf.pages))
            return [row for table in tables if table for row in table]
    except Exception:
        return None

def process_dataframe(df):
    if df is None or df.empty:
        return None
    
    df = df.applymap(clean_text)
    
    if len(df.columns) > len(EXPECTED_COLUMNS):
        df = df.iloc[:, :len(EXPECTED_COLUMNS)]
    elif len(df.columns) < len(EXPECTED_COLUMNS):
        for i in range(len(df.columns), len(EXPECTED_COLUMNS)):
            df[f'Coluna_{i}'] = None
    
    df.columns = EXPECTED_COLUMNS[:len(df.columns)]
    df.dropna(how='all', inplace=True)
    return df

def save_to_output(df, csv_filename, zip_filename):
    try:
        try:
            df.to_csv(csv_filename, index=False, sep=';', encoding='utf-8-sig')
        except UnicodeEncodeError:
            df.to_csv(csv_filename, index=False, sep=';', encoding='latin1', errors='replace')
        
        with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(csv_filename, os.path.basename(csv_filename))
        
        os.remove(csv_filename)
        return True
    except Exception as e:
        print(f"Erro ao salvar resultado: {str(e)}")
        return False

def main():
    current_dir = Path(__file__).parent
    pdf_path = current_dir.parent / "Web-Scraping" / "output" / "ans_pdfs" / "Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"
    
    csv_filename = "Teste_Anderson.csv"
    zip_filename = current_dir.parent / "Transformacao-Dados" / "output" / "Teste_AndersonGabriel.zip"
    
    dfs = extract_with_tabula(str(pdf_path))  
    df = pd.concat(dfs, ignore_index=True) if dfs and len(dfs) > 1 else (dfs[0] if dfs else None)
    

    if df is None or df.empty:
        print("Tabula falhou, tentando pdfplumber...")
        table_data = extract_with_pdfplumber(str(pdf_path))
        df = pd.DataFrame(table_data) if table_data else None
    
    if df is not None:
        processed_df = process_dataframe(df)
        if processed_df is not None and not processed_df.empty:
            if save_to_output(processed_df, csv_filename, zip_filename):
                print(f"Arquivo {zip_filename} criado com sucesso!")
                print(f"Localização: {Path(zip_filename).absolute()}")
                return
    
    print("Falha ao extrair tabelas do PDF.")

if __name__ == "__main__":
    main()