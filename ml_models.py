# ml_models.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["price_pln"])  # Drop rows without price
    df["price_pln"] = df["price_pln"].astype(float)  # Ensure price is numeric
    df = pd.get_dummies(df, drop_first=True)  # One-hot encoding for categorical variables
    df["mileage_km"] = df["mileage_km"].str.replace(" km", "").str.replace(",", "").astype(float)
    df["engine_capacity"] = df["engine_capacity"].str.replace(" cm3", "").astype(float)
    scaler = MinMaxScaler()
    df[["mileage_km", "engine_capacity"]] = scaler.fit_transform(df[["mileage_km", "engine_capacity"]])
    return df

def train_model(df: pd.DataFrame):
    # Assuming 'price_pln' is the target variable and others are features
    X = df.drop(columns=["price_pln", "link", "full_name", "description"])  # Drop non-feature columns
    y = df["price_pln"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model MSE: {mse}")
    print(f"Model R2: {r2}")

    return model

def predict_price(model, input_data: dict):
    # Make a prediction for a new car entry
    input_df = pd.DataFrame([input_data])
    input_df = preprocess_data(input_df)  # Apply preprocessing steps
    return model.predict(input_df)
