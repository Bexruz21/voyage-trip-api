from django.urls import path
from .views import (
    RegisterView, LoginView, MeView, MembershipCardListView, ProfileView,
    RegionListView, RegionDetailView, CountryListView, CountryDetailView,
    CityListView, CityDetailView, CountryCitiesView, RegionCountriesView
)

urlpatterns = [
    # Auth & User
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('cards/', MembershipCardListView.as_view(), name='cards'),
    
    # Regions
    path('regions/', RegionListView.as_view(), name='regions-list'),
    path('regions/<int:pk>/', RegionDetailView.as_view(), name='region-detail'),
    path('regions/<int:region_id>/countries/', RegionCountriesView.as_view(), name='region-countries'),
    
    # Countries
    path('countries/', CountryListView.as_view(), name='countries-list'),
    path('countries/<int:pk>/', CountryDetailView.as_view(), name='country-detail'),
    path('countries/<int:country_id>/cities/', CountryCitiesView.as_view(), name='country-cities'),
    
    # Cities
    path('cities/', CityListView.as_view(), name='cities-list'),
    path('cities/<int:pk>/', CityDetailView.as_view(), name='city-detail'),
]