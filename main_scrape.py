from scrapers.scrape_cars_otomoto import scrape_otomoto
from scrapers.test import scrape_multiple_makes
from ml_models import preprocess_data, train_model, predict_price

scrape_otomoto('bmw', 3)


def main():
    # Step 1: Scrape Data
    car_types = ['bmw', 'audi', 'mercedes', 'volkswagen', 'toyota']  # List of car makes
    pages_to_scrape = 10
    cars_df = scrape_multiple_makes(car_types, pages_to_scrape)
    
    # Step 2: Data Preprocessing
    cars_df = preprocess_data(cars_df)
    
    # Step 3: Train the Model
    model = train_model(cars_df)
    
    # Step 4: Example Prediction (optional)
    example_car = {
        "mileage_km": 35000,
        "engine_capacity": 2000,
        "fuel_type_diesel": 1,  # Example for one-hot encoding
        "fuel_type_petrol": 0
    }
    predicted_price = predict_price(model, example_car)
    print(f"Predicted price for the car: {predicted_price[0]} PLN")

if __name__ == "__main__":
    main()