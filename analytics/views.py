import json
import pandas as pd
from django.shortcuts import render

def dashboard(request):
    df = pd.read_csv("data/clean_booking_reviews.csv", on_bad_lines='skip')
    df['reviews.rating'] = pd.to_numeric(df['reviews.rating'], errors='coerce')
    
    # Get filter parameters
    rating_filter = request.GET.get('rating', 'all')
    province_filter = request.GET.get('province', 'all')
    
    # Apply filters
    filtered_df = df.copy()
    
    if rating_filter != 'all':
        if rating_filter == 'high':
            filtered_df = filtered_df[filtered_df['reviews.rating'] > 7]
        elif rating_filter == 'medium':
            filtered_df = filtered_df[(filtered_df['reviews.rating'] >= 5) & (filtered_df['reviews.rating'] <= 7)]
        elif rating_filter == 'low':
            filtered_df = filtered_df[filtered_df['reviews.rating'] < 5]
    
    if province_filter != 'all':
        filtered_df = filtered_df[filtered_df['reviews.userProvince'] == province_filter]
    
    # Only filter original df for province dropdown (show all options)
    provinces = df['reviews.userProvince'].dropna().unique().tolist()
    provinces = sorted([p for p in provinces if p])
    
    avg_rating = filtered_df['reviews.rating'].mean()
    total_reviews = len(filtered_df)
    negative_percent = len(filtered_df[filtered_df['reviews.rating'] <= 5]) / total_reviews * 100 if total_reviews > 0 else 0
    
    # Chart 1: Top 5 Hotels by Rating
    top_hotels = filtered_df.groupby('name')['reviews.rating'].mean().sort_values(ascending=False).head(5)
    
    # Chart 2: Top 5 Countries/Provinces by Rating
    top_countries = filtered_df.groupby('reviews.userProvince')['reviews.rating'].mean().sort_values(ascending=False).head(5)
    
    # Chart 3: Rating Distribution (Pie/Doughnut)
    rating_bins = [0, 2, 4, 6, 8, 10]
    rating_labels = ['0-2', '2-4', '4-6', '6-8', '8-10']
    rating_values = []
    for i in range(len(rating_bins) - 1):
        count = len(filtered_df[(filtered_df['reviews.rating'] > rating_bins[i]) & (filtered_df['reviews.rating'] <= rating_bins[i+1])])
        rating_values.append(count)
    
    # Chart 4: Sentiment Breakdown (Doughnut)
    positive_count = len(filtered_df[filtered_df['reviews.rating'] > 7])
    neutral_count = len(filtered_df[(filtered_df['reviews.rating'] >= 5) & (filtered_df['reviews.rating'] <= 7)])
    negative_count = len(filtered_df[filtered_df['reviews.rating'] < 5])
    
    # Chart 5: Reviews by Province (Horizontal Bar) - Top 10
    province_counts = filtered_df.groupby('reviews.userProvince').size().sort_values(ascending=False).head(10)
    
    # Chart 6: Rating Range Stats
    rating_stats = {
        'min': filtered_df['reviews.rating'].min(),
        'max': filtered_df['reviews.rating'].max(),
        'avg': filtered_df['reviews.rating'].mean()
    }

    context = {
        'avg_rating': round(avg_rating, 2) if pd.notna(avg_rating) else 0,
        'total_reviews': total_reviews,
        'negative_percent': round(negative_percent, 2),
        'top_hotels_json': json.dumps(top_hotels.index.tolist()),
        'top_hotels_data': json.dumps(top_hotels.values.tolist() if len(top_hotels) > 0 else []),
        'top_countries_json': json.dumps(top_countries.index.tolist()),
        'top_countries_data': json.dumps(top_countries.values.tolist() if len(top_countries) > 0 else []),
        # Chart 3: Rating Distribution
        'rating_dist_labels': json.dumps(rating_labels),
        'rating_dist_data': json.dumps(rating_values),
        # Chart 4: Sentiment
        'sentiment_data': json.dumps([positive_count, neutral_count, negative_count]),
        # Chart 5: Province counts
        'province_labels': json.dumps(province_counts.index.tolist()),
        'province_counts': json.dumps(province_counts.values.tolist()),
        # Chart 6: Rating range
        'rating_min': round(rating_stats['min'], 1) if pd.notna(rating_stats['min']) else 0,
        'rating_max': round(rating_stats['max'], 1) if pd.notna(rating_stats['max']) else 0,
        'rating_avg': round(rating_stats['avg'], 1) if pd.notna(rating_stats['avg']) else 0,
        # Filter options
        'provinces': provinces,
        'selected_rating': rating_filter,
        'selected_province': province_filter,
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
    
    avg_rating_all = df['reviews.rating'].mean()
    
    context = {
        'top_hotels_json': json.dumps([h['name'] for h in top_hotels_list]),
        'top_hotels_data': json.dumps([h['rating'] for h in top_hotels_list]),
        'top_hotels_list': top_hotels_list,
        'total_hotels': len(hotel_stats),
        'avg_rating_all': round(avg_rating_all, 2) if pd.notna(avg_rating_all) else 0
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
