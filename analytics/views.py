import json
import pandas as pd
from django.shortcuts import render

def dashboard(request):
    # Load the cleaned dataset from project folder
    # Use on_bad_lines='skip' to skip rows with inconsistent number of fields
    df = pd.read_csv("data/clean_booking_reviews.csv", on_bad_lines='skip')

    # Example KPIs - using correct column names from CSV
    # Convert rating column to numeric (it contains string values)
    df['reviews.rating'] = pd.to_numeric(df['reviews.rating'], errors='coerce')
    avg_rating = df['reviews.rating'].mean()
    total_reviews = len(df)
    negative_percent = len(df[df['reviews.rating'] <= 5]) / total_reviews * 100

    # Example charts - using correct column names from CSV
    top_hotels = df.groupby('name')['reviews.rating'].mean().sort_values(ascending=False).head(5)
    top_countries = df.groupby('reviews.userProvince')['reviews.rating'].mean().sort_values(ascending=False).head(5)

    context = {
        'avg_rating': round(avg_rating, 2),
        'total_reviews': total_reviews,
        'negative_percent': round(negative_percent, 2),
        'top_hotels_json': json.dumps(top_hotels.index.tolist()),
        'top_hotels_data': json.dumps(top_hotels.values.tolist()),
        'top_countries_json': json.dumps(top_countries.index.tolist()),
        'top_countries_data': json.dumps(top_countries.values.tolist()),
    }

    return render(request, "dashboard.html", context)
