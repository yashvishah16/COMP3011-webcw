from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .models import Airport, Flight, Passenger, Booking, Payment_Provider
import json, requests, random, string
from django.http import JsonResponse

# API Endpoint for URL: /airports
# Function only includes GET Request
# Sends a list of all the airport codes and names including status code
@csrf_exempt
def get_list_of_airports(request):
    #returns appropriate error if anything apart from a GET request is sent
    if request.method != 'GET':
        return JsonResponse({'error': 'This URL only supports GET requests'}, status=400)
    airports_list = []
    airport_objects = Airport.objects.all()
    # Iterate over each airport and add all the airports details as dictionaries to the list
    index = 0
    while index < len(airport_objects):
        airport = airport_objects[index]
        airports_list.append({'airport_code': airport.airport_code, 'airport_name': airport.airport_name})
        index += 1
    response_dictionary = {'status_code': '200', 'list_of_airports': airports_list}
    #this creates a Json object
    return JsonResponse(response_dictionary)
    
# API Endpoint for URL: /flights
# Function only includes GET Request
# Receives required parmaters from search bar and displays flight information accordingly
@csrf_exempt
def get_available_flights(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'This URL only supports GET requests'}, status=400)
    
    # Store parameters entered in search bars into variables
    date = request.GET.get('date') #date of departure
    source = request.GET.get('source') #source airport code
    destination = request.GET.get('destination') #destination airport code

    # Error responses if required paramets have not been supplied
    if not date:
        return JsonResponse({'error': 'Missing required date of departure'})
    if not source:
        return JsonResponse({'error': 'Missing source airport code'})
    if not destination:
        return JsonResponse({'error': 'Missing destination airport code'})
    
    # Error if source and destination airport codes provided are invalid
    airports_list = []
    airport_objects = Airport.objects.all()
    index = 0
    while index < len(airport_objects):
        airport = airport_objects[index]
        airports_list.append(airport.airport_code)
        index += 1
    if source not in airports_list:
        return JsonResponse({'error': 'Source airport code is invalid'}, status=401)
    if destination not in airports_list:
        return JsonResponse({'error': 'Destination airport code is invalid'}, status=401)
    
    flights_list = []
    for flight in Flight.objects.filter(source=source, destination=destination):
        past_bookings = Booking.objects.filter(date=date,
                                             flight_id = flight.flight_id)
        # total flight capactiy - total number of bookings that have been made for that flight = remaining capacity
        remaining_capactiy = flight.capacity - past_bookings.count()
        flights_list.append({'flight_code': flight.flight_id, 'duration': flight.duration, 'flight_time': flight.time,
                             'business_status': flight.business, 'eco_price': flight.eco_price, 'bus_price': flight.bus_price})
    response_dictionary = {'status_code': '200', 'flight_list': flights_list}
    #this creates a json object
    return JsonResponse(response_dictionary)

# API Endpoint for URL: /make-booking
# Function only includes POST Request
# Function checks the retrieved information containing passenger details for validity
# If everything is okay, add a record to the database and respond with booking id and a list of trusted payment providers.
@csrf_exempt
def make_a_booking(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'This URL only supports POST requests'}, status=400)
    
    # Store parameters into variables
    booking_legal_name             = request.POST.get('legal_name')
    booking_first_name             = request.POST.get('first_name')
    booking_last_name              = request.POST.get('last_name')
    booking_date_of_birth          = request.POST.get('date_of_birth')
    booking_passport_number        = request.POST.get('passport_no')
    booking_email                  = request.POST.get('email')
    booking_contact_number         = request.POST.get('contact_no')
    booking_flight_code            = request.POST.get('flight_code')
    booking_class                  = request.POST.get('class')
    booking_date_of_departure      = request.POST.get('date_of_departure')

    # Error responses if required parameters have not been supplied
    if not booking_legal_name:
        return JsonResponse({'error': 'Missing required legal name'})
    if not booking_date_of_birth:
        return JsonResponse({'error': 'Missing required date of birth'})
    if not booking_passport_number:
        return JsonResponse({'error': 'Missing required passport number'})
    if not booking_email:
        return JsonResponse({'error': 'Missing required email address'})
    if not booking_flight_code:
        return JsonResponse({'error': 'Missing required flight code'})
    if not booking_class:
        return JsonResponse({'error': 'Missing required booking class'})
    if not booking_date_of_departure:
        return JsonResponse({'error': 'Missing required departure date'})
    
    # Error if required parameters provided are invalid
    if booking_legal_name == 'null' or booking_legal_name == '':
        return JsonResponse({'error': 'Enter your legal name!'})
    date_of_birth = datetime.strptime(booking_date_of_birth, '%Y-%m-%d').date()
    if date_of_birth.year < 1963 or date_of_birth.year > 2023:
       return JsonResponse({'error': 'Date of birth is supposed to be between 1963-2023'}, status=401)
    if len(booking_passport_number)>9:
        return JsonResponse({'error': 'Length of passport number should be 9 characters or less'}, status=401)
    if '@' not in booking_email:
        return JsonResponse({'error': 'Invalid email address. Should contain "@"!'}, status=401)
    if not Flight.objects.filter(flight_id = booking_flight_code).exists():
        return JsonResponse({'error': 'Entered flight code does not exist. Enter a valid flight code!'}, status=401)
    if not (booking_class == 'eco' or booking_class == 'bus'):
        return JsonResponse({'error': 'Enter a valid booking class(eco or bus)!'}, status=401)
    departure_date = datetime.strptime(booking_date_of_departure, '%Y-%m-%d').date()
    if departure_date.year < 2023 or departure_date.year > 2025:
        return JsonResponse({'error': 'You can only book 2 years in advance. Enter departure date between 2023-2025'}, status=401)
    
    # Check if the passenger is new or they already have previous record
    if not Passenger.objects.filter(passport_no=booking_passport_number).exists():
        if booking_email and Passenger.objects.filter(email=booking_email).exists():
            return JsonResponse({'This Email ID already has a passenger. Please use a different email address!'})
        
        new_passenger = Passenger(
          passenger_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
          legal_name = booking_legal_name,
          first_name = booking_first_name if booking_first_name is not None else '',
          last_name = booking_last_name if booking_last_name is not None else '',
          date_of_birth = booking_date_of_birth,
          passport_no = booking_passport_number,
          email = booking_email,
          contact_no = booking_contact_number if booking_contact_number is not None else '')
        new_passenger.save()

    # Retrieve passenger ID for current passenger
    # If a passenger is trying to make a new booking for a flight booked previously
    # for the same date and the same passenger, deny and respond with previous booking id
    current_passenger_id = Passenger.objects.filter(passport_no = booking_passport_number)[0].passenger_id
    existing_booking_check = Booking.objects.filter(flight_id = booking_flight_code,
                             passenger_id = current_passenger_id,
                             date = booking_date_of_departure)
    if existing_booking_check.exists():
        check_booking_id = existing_booking_check[0].booking_id
        return JsonResponse({'The requested booking has been previously made with this booking id': check_booking_id})
    
    # Make a new booking
    else:
        new_booking = Booking(
          booking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
          flight_id = Flight.objects.get(flight_id = booking_flight_code),
          passenger_id = Passenger.objects.get(passenger_id = current_passenger_id),
          date = booking_date_of_departure,
          booking_class = booking_class,
          invoice_id = None,
          payment_received = False
        )
        new_booking.save()
        payment_providers = []
        for payment in Payment_Provider.objects.all():
            payment_providers.append({'pp_code': payment.pp_id, 'pp_name': payment.name})
        response_dictionary = {'status_code': '200', 'booking_id': new_booking.booking_id, 'pp_list': payment_providers}
        return JsonResponse(response_dictionary)
    
# API Endpoint for URL: /invoice/{booking-id}
# Function only includes POST Request
# For the given booking id, the invoice is generated by calling the api endpoint of the payment provider retrieved as the parameters
# Once an invoice id is received, it is stored in the database and forwarded to the caller.
@csrf_exempt
def create_an_invoice(request, booking_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'This URL only supports POST requests'}, status=400)
    
    # Store parameter into variable
    preferred_vendor = request.POST.get('preferred_vendor')

    # Error responses if required parameter has not been supplied
    if not preferred_vendor:
        return JsonResponse({'error': 'Missing required preferred vendor'}, status=400)
    
    # Error if required parameters provided are invalid
    vendors_list = []
    for vendor in Payment_Provider.objects.all():
        vendors_list.append(vendor.pp_id)
    if preferred_vendor not in vendors_list:
        return JsonResponse({'Preferred vendor is invalid!'}, status=401)
    all_bookings = []
    for booking in Booking.objects.all():
        all_bookings.append(booking.booking_id)
    if booking_id not in all_bookings:
        return JsonResponse({'Booking id is invalid!'}, status=401)
    if Booking.objects.get(booking_id = booking_id).invoice_id is not None:
        return JsonResponse({'error': 'Given booking id already has an invoice, please enter new details!'})
    Booking.objects.get(booking_id = booking_id).payment_provider = Payment_Provider.objects.get(pp_id = preferred_vendor)

    #appending /invoice to current payment provider's url to get the required path
    updated_url = Payment_Provider.objects.get(pp_id = preferred_vendor).url+'invoice/'

    # Retrieve appropriate cost of the ticket based on booking class
    current_booking = Booking.objects.get(booking_id = booking_id)
    if current_booking.booking_class == 'eco':
        cost = Flight.objects.get(flight_id=booking.flight_id.flight_id).eco_price
    elif current_booking.booking_class == 'bus':
        cost = Flight.objects.get(flight_id=booking.flight_id.flight_id).bus_price
    else:
        return JsonResponse({'Invalid booking class'}, status=401)
    
    if cost is None:
        return JsonResponse({'Failed to retrieve flight price!'})
    cost = int(cost * 100)
    input_data = {
        "api_key": '2002',
        "amount": cost,
        "metadata": []
    }

    # Send the POST request to payment provider's API endpoint
    actual_response = requests.post(updated_url, json=input_data, headers={'Content-Type': 'application/json'})
    if actual_response.status_code == 200:
        response = actual_response.json()
        invoice_id = response['invoice_id'] 
        current_booking.invoice_id = invoice_id
        current_booking.save()

        # Return the invoice_id to the aggregator
        response_dictionary = {'status_code': '200', 'invoice_id': invoice_id}
        return JsonResponse(response_dictionary, safe=False)

    else:
        # Handle the error status code appropriately as decided by the group
        if actual_response.status_code == 400: # Bad Request
            return JsonResponse({'error': 'Error: Bad Request'})
        elif actual_response.status_code == 401:   # Unauthorized
            return JsonResponse({'error': 'Error: Unauthorized'})
        elif actual_response.status_code == 403:   # Forbidden
            return JsonResponse({'error': 'Error: Forbidden'})
        elif actual_response.status_code == 404:   # Not Found
            return JsonResponse({'error': 'Error: Not Found'})
        elif actual_response.status_code == 500:   # Internal Server Error
            return JsonResponse({'error': 'Error: Internal Server Error'})
        
# API Endpoint for URL: /confirm/{invoice-id}
# Function only includes POST Request
# For the given invoice id, function checks if it has been confirmed by calling the appropriate api endpoint.
# If yes, it updates the database and inform the flight aggregator
@csrf_exempt
def confirm_invoice(request, booking_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'This URL only supports POST requests'}, status=400)
    # Get the booking that matches both invoice id as well as payment provider
    current_booking = Booking.objects.filter(booking_id = booking_id)
    if not current_booking.exists():
        return JsonResponse({'This booking id is invalid'})
    elif current_booking.count() > 1:
        return JsonResponse({'error': 'More than one booking found for the given booking id!'})
    else:
        payment_provider = Payment_Provider.objects.get(pp_id = current_booking[0].payment_provider.pp_id)
        updated_url = payment_provider.url + f'invoice/{current_booking[0].invoice_id}/'
        input_data = {'api_key': '2002'}
        actual_response = requests.get(updated_url, json=input_data, headers={'Content-Type': 'application/json'})
        if actual_response.status_code == 200:
            response = actual_response.json()
            payment_status = response['paid']
            # Update the booking with the new invoice status
            current_booking[0].status = payment_status
            current_booking[0].save()
            # Return the invoice_status to the aggregator
            response_dictonary = {'status_code': '200', 'payment_status': payment_status}
            return JsonResponse(response_dictonary)
        else:
            # Handle the error status code appropriately as decided by the group
            if actual_response.status_code == 400: # Bad Request
                return JsonResponse({'error': 'Error: Bad Request'})
            elif actual_response.status_code == 401:   # Unauthorized
                return JsonResponse({'error': 'Error: Unauthorized'})
            elif actual_response.status_code == 403:   # Forbidden
                return JsonResponse({'error': 'Error: Forbidden'})
            elif actual_response.status_code == 404:   # Not Found
                return JsonResponse({'error': 'Error: Not Found'})
            elif actual_response.status_code == 500:   # Internal Server Error
                return JsonResponse({'error': 'Error: Internal Server Error'})