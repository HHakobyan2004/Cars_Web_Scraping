import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import datetime
import time

def scrape_cars(query_url):
    cars_base = 'https://www.cars.com/shopping/results/'
    model_url = cars_base + query_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    for attempt in range(3):
        try:
            # Make the request with a longer timeout
            response = requests.get(model_url, headers=headers, timeout=30)
            response.raise_for_status()  # Raise error for bad responses
            break
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}. Retrying...")
            time.sleep(5)  # Delay before retry
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return None

    model_soup = BeautifulSoup(response.text, 'html.parser')
    vehicle_cards = model_soup.find_all("div", class_="vehicle-card")

    if not vehicle_cards:
        print("No vehicle data found. The page might be dynamic or blocked.")
        return None

    vehicles = []
    for vehicle_card in vehicle_cards:
        try:
            title = vehicle_card.find('h2', class_='title').text.strip()
            mileage = int(re.sub(r'\D+', '', vehicle_card.find('div', class_='mileage').text))
            price = int(re.sub(r'\D+', '', vehicle_card.find('span', class_='primary-price').text))
            distance = vehicle_card.find('div', class_='miles-from')
            distance = int(re.sub(r'\D+', '', distance.text)) if distance else np.NaN
            date_accessed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vehicles.append([title, mileage, price, distance, date_accessed])
        except AttributeError:
            continue

    vehicle_dataframe = pd.DataFrame(vehicles, columns=['title', 'mileage', 'price', 'distance', 'date_accessed'])
    print(vehicle_dataframe)
    return vehicle_dataframe


# Test
scrape_cars('results/?list_price_max=30000&makes[]=toyota&models[]=toyota-camry&stock_type=used&zip=90210')

