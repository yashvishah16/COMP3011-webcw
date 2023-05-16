from django.contrib import admin
from .models import Airport, Flight, Passenger, Booking, Payment_Provider

# Registering models for this project.
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Passenger)
admin.site.register(Booking)
admin.site.register(Payment_Provider)