import os
import pandas as pd
import shutil

def remove_duplicates_xlsx(directory):
    summary = []
    files = [f for f in os.listdir(directory) if f.lower().endswith('.xlsx')]
    
    for filename in files:
        file_path = os.path.join(directory, filename)
        
        # Check if file is empty or too small
        if os.path.getsize(file_path) == 0:
            summary.append(f"{filename}: File is empty (0 bytes).")
            continue
            
        try:
            # Use pd.ExcelFile to read all sheets
            excel_file = pd.ExcelFile(file_path, engine='openpyxl')
            sheet_names = excel_file.sheet_names
            
            cleaned_sheets = {}
            total_removed = 0
            
            for sheet_name in sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
                original_count = len(df)
                
                # Keep first occurrence of each unique row
                df_cleaned = df.drop_duplicates(keep='first')
                new_count = len(df_cleaned)
                
                removed_in_sheet = original_count - new_count
                total_removed += removed_in_sheet
                
                cleaned_sheets[sheet_name] = df_cleaned
            
            if total_removed > 0:
                # Save the cleaned data to a temporary file first
                # Use .xlsx extension so pd.ExcelWriter doesn't complain
                temp_file_path = file_path + ".temp.xlsx"
                with pd.ExcelWriter(temp_file_path, engine='openpyxl') as writer:
                    for sheet_name, df_cleaned in cleaned_sheets.items():
                        df_cleaned.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Replace the original file
                if os.path.exists(file_path):
                    os.remove(file_path)
                shutil.move(temp_file_path, file_path)
                summary.append(f"{filename}: Removed {total_removed} rows across {len(sheet_names)} sheets.")
            else:
                summary.append(f"{filename}: No duplicate rows found in any of the {len(sheet_names)} sheets.")
                
        except Exception as e:
            summary.append(f"{filename}: Error processing file: {str(e)}")

    return summary

if __name__ == "__main__":
    directory = r'C:\Users\Esteban Selvaggi\Downloads\Contactos\scrap\bbdd'
    results = remove_duplicates_xlsx(directory)
    for line in results:
        print(line)
