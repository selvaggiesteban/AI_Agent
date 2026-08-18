import os
import pandas as pd
import csv

def remove_duplicates(directory):
    summary = []
    files = [f for f in os.listdir(directory) if f.lower().endswith('.csv')]
    
    for filename in files:
        if filename == 'remove_duplicates.py': # Skip the script itself if it was in the directory
            continue
            
        file_path = os.path.join(directory, filename)
        
        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            summary.append(f"{filename}: File is empty (0 bytes).")
            continue
            
        try:
            # Try to read the CSV
            # Using low_memory=False to avoid DtypeWarning
            # Using encoding='utf-8-sig' to handle BOM
            df = pd.read_csv(file_path, low_memory=False, encoding='utf-8-sig')
            
            original_count = len(df)
            df_cleaned = df.drop_duplicates(keep='first')
            new_count = len(df_cleaned)
            removed_count = original_count - new_count
            
            if removed_count > 0:
                # Save the cleaned data
                df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
                summary.append(f"{filename}: Removed {removed_count} rows. (From {original_count} to {new_count})")
            else:
                summary.append(f"{filename}: No duplicate rows found.")
                
        except Exception as e:
            # If pandas fails, it might be due to encoding or delimiter
            # Let's try to handle common issues
            try:
                # Try with different encoding or engine
                df = pd.read_csv(file_path, low_memory=False, encoding='latin1', on_bad_lines='skip')
                original_count = len(df)
                df_cleaned = df.drop_duplicates(keep='first')
                new_count = len(df_cleaned)
                removed_count = original_count - new_count
                
                if removed_count > 0:
                    df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
                    summary.append(f"{filename}: Removed {removed_count} rows (with latin1 encoding).")
                else:
                    summary.append(f"{filename}: No duplicate rows found (with latin1 encoding).")
            except Exception as e2:
                summary.append(f"{filename}: Error processing file: {str(e)}")

    return summary

if __name__ == "__main__":
    directory = r'C:\Users\Esteban Selvaggi\Downloads\Contactos\scrap\bbdd'
    results = remove_duplicates(directory)
    for line in results:
        print(line)
