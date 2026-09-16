
import openpyxl
import os

def find_all_potential_local_competitors(filename, domains_to_exclude):
    """
    Reads an Excel file, excludes known large platforms, and extracts a list of all potential local competitors.
    """
    try:
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook.active
        
        potential_competitors = []
        # Iterate through a much larger set of rows to ensure we capture all possibilities
        for row in sheet.iter_rows(min_row=2, max_row=100, values_only=True):
            if row and len(row) > 0:
                domain = row[0]
                if domain and domain.lower() not in domains_to_exclude:
                    # Find the corresponding URL in the row, ensuring it's a full URL
                    url = next((cell for cell in row[1:] if cell and isinstance(cell, str) and cell.startswith('http')), None)
                    if not url and domain:
                        # If no full URL is found, construct one
                        url = f"https://{domain}"
                    
                    if url:
                        potential_competitors.append({"domain": domain, "url": url})
        
        return potential_competitors

    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    # Expanded list of large, non-local platforms to exclude
    non_local_domains = [
        "facebook.com", "fresha.com", "milanuncios.com", 
        "wallapop.com", "booksy.com", "youtube.com",
        "instagram.com", "linkedin.com", "twitter.com",
        "pinterest.com", "google.com", "doctoralia.es",
        "topdoctors.es", "emagister.com", "indeed.com",
        "glassdoor.com", "jobtoday.com", "amazon.com",
        "ebay.com", "aliexpress.com", "paginasamarillas.es", "trabeja.com", "cronoshare.com", "prontopro.es", "saludterapia.com"
    ]

    # Find the competitor file
    xlsx_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and 'quirojac.es-organic.Competitors' in f]
    if not xlsx_files:
        print("No competitor XLSX file found.")
    else:
        competitors_file = xlsx_files[0]
        competitors_list = find_all_potential_local_competitors(competitors_file, non_local_domains)
        
        if competitors_list:
            print("Lista de posibles competidores locales a investigar:")
            for competitor in competitors_list:
                print(f"Dominio: {competitor['domain']}, URL: {competitor['url']}")
        else:
            print("No se encontraron posibles competidores locales en el archivo.")
