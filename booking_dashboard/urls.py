from django.contrib import admin
from django.urls import path
from analytics import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('hotels/', views.hotels, name='hotels'),
    path('reviews/', views.reviews, name='reviews'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
]
