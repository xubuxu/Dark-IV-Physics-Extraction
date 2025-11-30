import pandas as pd

def generate_excel_report(results_list, output_path):
    """Generates an Excel summary report from a list of results dictionaries."""
    df = pd.DataFrame(results_list)
    # Reorder columns if possible to put filename first
    cols = ['filename'] + [c for c in df.columns if c != 'filename']
    # Filter only existing columns
    cols = [c for c in cols if c in df.columns]
    df = df[cols]
    
    df.to_excel(output_path, index=False)
