import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import math

def mobile_de_scraping(url, lang="en"):
    # Send initial request to parse total items and pages
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the number of results on the first page
    results_text = soup.select_one(".rbt-result-list-headline")
    if not results_text:
        raise ValueError("Could not find results headline. Check if the URL is correct.")
    
    # Extract number of items from text
    number_of_items = int(re.sub(r'[^\d]', '', results_text.text))
    number_of_pages = math.ceil(number_of_items / 20)  # Each page has ~20 results
    number_of_pages = min(number_of_pages, 50)  # Limit to max 50 pages

    # Prepare data storage
    all_data = []

    for page in range(1, number_of_pages + 1):
        # Modify URL to include page number
        if "pageNumber=" in url:
            page_url = re.sub(r'pageNumber=\d+', f'pageNumber={page}', url)
        else:
            page_url = f"{url}&pageNumber={page}"

        # Fetch the page
        page_response = requests.get(page_url)
        page_soup = BeautifulSoup(page_response.text, 'html.parser')

        # Scrape data fields
        models = [item.text.strip() for item in page_soup.select(".u-text-break-word")]
        prices = [re.sub(r'[^\d]', '', item.text) for item in page_soup.select(".h3.u-block")]
        kms_years = [item.text.strip() for item in page_soup.select(".rbt-regMilPow")]
        valuations = [item.text.strip() for item in page_soup.select(".mde-price-rating__badge")]

        # Parse `kms_years` for mileage, year, and power
        years, kms, powers = [], [], []
        for item in kms_years:
            parts = item.split()
            if "Neuwagen" in parts:
                years.append("New")
                kms.append("0")
            elif len(parts) > 3:
                years.append(parts[1])
                kms.append(re.sub(r'[^\d]', '', parts[3]))
            else:
                years.append(None)
                kms.append(None)
            # Extract power (Kw) if available
            kw_match = re.search(r'(\d+)\s?kW', item)
            powers.append(kw_match.group(1) if kw_match else None)

        # Combine data into a structured format
        for i in range(len(models)):
            all_data.append({
                "Model": models[i],
                "Year": years[i] if i < len(years) else None,
                "Km": kms[i] if i < len(kms) else None,
                "Power (Kw)": powers[i] if i < len(powers) else None,
                "Price (€)": prices[i] if i < len(prices) else None,
                "Valuation": valuations[i] if i < len(valuations) else None
            })

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    return df

# Example usage
if __name__ == "__main__":
    search_url = "https://suchen.mobile.de/fahrzeuge/search.html?damageUnrepaired=NO_DAMAGE_UNREPAIRED&isSearchRequest=true&makeModelVariant1.makeId=25200&maxMileage=150000&maxPowerAsArray=KW&maxPrice=11000&minMileage=125000&minPowerAsArray=KW&minPrice=10000&scopeId=C&sfmr=false"
    scraped_data = mobile_de_scraping(search_url, lang="en")
    print(scraped_data.head())
