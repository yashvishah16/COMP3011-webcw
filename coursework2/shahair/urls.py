from django.urls import path
from . import views

urlpatterns = [
    path('airports/', views.get_list_of_airports),
    path('flights/', views.get_available_flights),
    path('make-booking/', views.make_a_booking),
    path('invoice/<str:booking_id>/', views.create_an_invoice),
    path('confirm/<str:booking_id>/', views.confirm_invoice)
]