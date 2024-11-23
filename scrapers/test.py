import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List
import csv
import pandas as pd

@dataclass
class Car:
    link: str
    full_name: str
    description: str
    year: str
    mileage_km: str
    engine_capacity: str
    fuel_type: str
    price_pln: str

class OtomotoScraper:
    def __init__(self, car_make: str) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                          "AppleWebKit/537.11 (KHTML, like Gecko) "
                          "Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }
        self.car_make = car_make
        self.website = "https://www.otomoto.pl/osobowe"

    def scrape_pages(self, number_of_pages: int) -> List[Car]:
        cars = []
        for i in range(1, number_of_pages + 1):
            current_website = f"{self.website}/{self.car_make}/?page={i}"
            print(f"Scraping page {i}: {current_website}")
            new_cars = self.scrape_cars_from_current_page(current_website)
            if new_cars:
                cars.extend(new_cars)
        return cars

    def scrape_cars_from_current_page(self, current_website: str) -> List[Car]:
        try:
            response = requests.get(current_website, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            cars = self.extract_cars_from_page(soup)
            return cars
        except Exception as e:
            print(f"Error scraping {current_website}: {e}")
            return []

    def extract_cars_from_page(self, soup: BeautifulSoup) -> List[Car]:
        cars = []
        car_elements = soup.find_all("div", class_="ooa-1qo9a0p epwfahw6")

        for element in car_elements:
            try:
                # Extract link and title
                title_tag = element.find("h1", class_="epwfahw9 ooa-1ed90th er34gjf0")
                link = title_tag.find("a", href=True).get("href")
                full_name = title_tag.find("a").text.strip()

                # Extract description
                description_tag = element.find("p", class_="epwfahw10 ooa-1tku07r er34gjf0")
                description = description_tag.text.strip() if description_tag else ""

                # Create Car object
                car = Car(
                    link=link,
                    full_name=full_name,
                    description=description,
                    year=None,  # Year is not in the snippet; update if found elsewhere
                    mileage_km=None,  # Mileage not in snippet
                    engine_capacity=None,  # Extract from `description` if needed
                    fuel_type=None,  # Fuel type not in snippet
                    price_pln=None,  # Price not in snippet
                )
                cars.append(car)
            except Exception as e:
                print(f"Error processing car element: {e}")

        return cars

def write_to_csv(cars: List[Car], filename="multi_cars.csv") -> None:
    if not cars:
        print("No cars to save!")
        return
    with open(filename, mode="w", newline='', encoding="utf-8") as f:
        fieldnames = [
            "link", "full_name", "description", 
            "year", "mileage_km", "engine_capacity", 
            "fuel_type", "price_pln"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for car in cars:
            writer.writerow(asdict(car))
    print(f"Data successfully written to {filename}")

def scrape_multiple_makes(car_types: List[str], pages: int) -> None:
    all_cars = []
    for car_make in car_types:
        print(f"Scraping data for: {car_make}")
        scraper = OtomotoScraper(car_make)
        cars = scraper.scrape_pages(pages)
        all_cars.extend(cars)
    # Write aggregated data to CSV
    write_to_csv(all_cars, filename="multi_cars.csv")
    cars_df = pd.DataFrame([asdict(car) for car in all_cars])
    print(cars_df.head())
    print("Data scraping and saving complete.")
    return cars_df

if __name__ == "__main__":
    car_types = ['bmw', 'audi', 'mercedes', 'volkswagen', 'toyota']  # List of car makes
    pages_to_scrape = 10
    scrape_multiple_makes(car_types, pages_to_scrape)

