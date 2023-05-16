from django.db import models

# Models are based on the database table created in cw1 report on page 8
class Airport(models.Model):
    airport_code = models.CharField(max_length=3, primary_key=True)
    airport_name = models.CharField(max_length=100) #the longest airport name in the world has 83 characters

    def __str__(self):
        return f'{self.airport_code}:{self.airport_name}'
    
class Flight(models.Model):
    flight_id = models.CharField(max_length=6, primary_key=True)
    capacity = models.PositiveSmallIntegerField()
    source = models.ForeignKey(Airport, to_field='airport_code', on_delete=models.PROTECT,
                                related_name='departures')
    destination = models.ForeignKey(Airport, to_field='airport_code', on_delete=models.PROTECT,
                                     related_name='arrivals')
    duration = models.PositiveSmallIntegerField()
    time = models.PositiveSmallIntegerField()
    business = models.BooleanField()
    eco_price = models.FloatField()
    bus_price = models.FloatField(blank=True, null=True)
    
    def __str__(self):
      return f'{self.flight_id}: {self.source} - {self.destination}'

class Passenger(models.Model):
    passenger_id = models.CharField(max_length = 6, primary_key=True)
    legal_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200, blank=True, null = True)
    last_name = models.CharField(max_length=200, blank=True, null = True)
    date_of_birth = models.DateField()
    passport_no = models.CharField(max_length=9, unique=True)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=13, blank=True, null = True)
    
    def __str__(self):
        return f'{self.passenger_id}: {self.legal_name}({self.passport_no})'

class Payment_Provider(models.Model):
    pp_id = models.CharField(max_length = 3, primary_key=True)
    url = models.CharField(max_length=300)
    name = models.CharField(max_length=200)

    def __str__(self):
      return self.name

class Booking(models.Model):
    booking_id = models.CharField(max_length = 8, primary_key=True)
    flight_id = models.ForeignKey(Flight, to_field='flight_id', on_delete=models.PROTECT)
    passenger_id = models.ForeignKey(Passenger, to_field='passenger_id', on_delete=models.PROTECT)
    date = models.DateField()
    booking_class = models.CharField(max_length=3, choices = [('eco', 'Economy'),('bus', 'Business')])
    invoice_id = models.IntegerField(null=True)
    payment_provider = models.ForeignKey(Payment_Provider, to_field='pp_id', on_delete=models.PROTECT, null=True)
    payment_received = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.booking_id}: {self.flight_id.flight_id} - {self.passenger_id.legal_name}'
    
