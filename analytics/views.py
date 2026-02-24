import json
import pandas as pd
from django.shortcuts import render

def dashboard(request):
    df = pd.read_csv("data/clean_booking_reviews.csv", on_bad_lines='skip')
    df['reviews.rating'] = pd.to_numeric(df['reviews.rating'], errors='coerce')
    avg_rating = df['reviews.rating'].mean()
    total_reviews = len(df)
    negative_percent = len(df[df['reviews.rating'] <= 5]) / total_reviews * 100

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

def hotels(request):
    df = pd.read_csv("data/clean_booking_reviews.csv", on_bad_lines='skip')
    df['reviews.rating'] = pd.to_numeric(df['reviews.rating'], errors='coerce')
    
    hotel_stats = df.groupby('name').agg({
        'reviews.rating': 'mean',
        'reviews.text': 'count'
    }).rename(columns={'reviews.text': 'review_count'})
    
    hotel_stats = hotel_stats.sort_values('reviews.rating', ascending=False)
    top_hotels_list = [
        {'name': name, 'rating': round(row['reviews.rating'], 2), 'review_count': row['review_count']}
        for name, row in hotel_stats.head(20).iterrows()
    ]
    
    context = {
        'top_hotels_json': json.dumps([h['name'] for h in top_hotels_list]),
        'top_hotels_data': json.dumps([h['rating'] for h in top_hotels_list]),
        'top_hotels_list': top_hotels_list,
        'total_hotels': len(hotel_stats)
    }
    
    return render(request, "hotels.html", context)

def reviews(request):
    df = pd.read_csv("data/clean_booking_reviews.csv", on_bad_lines='skip')
    df['reviews.rating'] = pd.to_numeric(df['reviews.rating'], errors='coerce')
    
    total_reviews = len(df)
    positive_count = len(df[df['reviews.rating'] > 7])
    neutral_count = len(df[(df['reviews.rating'] >= 5) & (df['reviews.rating'] <= 7)])
    negative_count = len(df[df['reviews.rating'] < 5])
    
    recent_reviews = df.dropna(subset=['reviews.text']).head(20).to_dict('records')
    
    context = {
        'total_reviews': total_reviews,
        'positive_count': positive_count,
        'neutral_count': neutral_count,
        'negative_count': negative_count,
        'recent_reviews': recent_reviews
    }
    
    return render(request, "reviews.html", context)

def reports(request):
    df = pd.read_csv("data/clean_booking_reviews.csv", on_bad_lines='skip')
    df['reviews.rating'] = pd.to_numeric(df['reviews.rating'], errors='coerce')
    
    avg_rating = df['reviews.rating'].mean()
    median_rating = df['reviews.rating'].median()
    std_rating = df['reviews.rating'].std()
    
    top_hotels = df.groupby('name')['reviews.rating'].mean().sort_values(ascending=False).head(10)
    province_counts = df.groupby('reviews.userProvince').size().sort_values(ascending=False).head(10)
    
    context = {
        'avg_rating': round(avg_rating, 2),
        'median_rating': round(median_rating, 2),
        'std_rating': round(std_rating, 2),
        'top_hotels_json': json.dumps(top_hotels.index.tolist()),
        'top_hotels_data': json.dumps(top_hotels.values.tolist()),
        'province_counts': province_counts.to_dict()
    }
    
    return render(request, "reports.html", context)

def settings(request):
    return render(request, "settings.html")
