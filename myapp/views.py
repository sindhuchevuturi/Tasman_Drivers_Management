#hello
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from twilio.rest import Client
from myapp.models import Roster  # Assuming you have a Roster model
import json
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q

from django.conf import settings

account_sid = settings.ACCOUNT_SID
auth_token = settings.AUTH_TOKEN
twilio_phone_number=settings.YOUR_TWILIO_PHONE_NUMBER

def trailers_list(request):
    """Render the trailers list view"""
    trailers = Trailer.objects.all()
    return render(request, 'trailers.html', {'trailers': trailers})
def add_trailer(request):
    """Handle AJAX requests to add a new trailer"""
    if request.method == 'POST':
        rego_number = request.POST.get('rego_number', '').strip()
        if rego_number:
            # Check if the trailer already exists
            if Trailer.objects.filter(rego_number=rego_number).exists():
                return JsonResponse({'status': 'exists', 'message': 'Trailer already exists.'})
            else:
                trailer = Trailer.objects.create(rego_number=rego_number)
                return JsonResponse({
                    'status': 'success',
                    'rego_number': trailer.rego_number,
                    'trailer_id': trailer.id
                })
        return JsonResponse({'status': 'error', 'message': 'Invalid trailer registration number.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# views.py

def vehicle_list(request):
    """Render the vehicles list view"""
    vehicles = Vehicle.objects.all()  # Changed from 'vehicle' to 'vehicles' for clarity
    return render(request, 'vehicles.html', {'vehicle': vehicles})  # Keep the context variable the same
def add_vehicle(request):
    """Handle AJAX requests to add a new vehicle"""
    if request.method == 'POST':
        rego_number = request.POST.get('rego_number', '').strip()
        if rego_number:
            if Vehicle.objects.filter(rego_number=rego_number).exists():
                return JsonResponse({'status': 'exists', 'message': 'Vehicle already exists.'})
            else:
                vehicle = Vehicle(rego_number=rego_number)
                vehicle.save()
                return JsonResponse({
                    'status': 'success',
                    'rego_number': vehicle.rego_number,
                    'vehicle_id': vehicle.id
                })
        return JsonResponse({'status': 'error', 'message': 'Invalid vehicle registration number.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def drivers_list(request):
    """Render the drivers list view."""
    drivers = Driver.objects.all()
    return render(request, 'drivers.html', {'drivers': drivers})

def add_driver(request):
    """Handle AJAX requests to add a new driver."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        on_leave = request.POST.get('on_leave') == 'true'
        has_msic = request.POST.get('has_msic') == 'true'
        has_white_card = request.POST.get('has_white_card') == 'true'

        if name and phone_number:
            # Check if a driver with the same name and phone number already exists
            if not Driver.objects.filter(name=name, phone_number=phone_number).exists():
                driver = Driver.objects.create(
                    name=name,
                    phone_number=phone_number,
                    on_leave=on_leave,
                    has_msic=has_msic,
                    has_white_card=has_white_card
                )
                return JsonResponse({
                    'status': 'success',
                    'name': driver.name,
                    'phone_number': driver.phone_number,
                    'on_leave': driver.on_leave,
                    'has_msic': driver.has_msic,
                    'has_white_card': driver.has_white_card
                })
            else:
                return JsonResponse({'status': 'exists', 'message': 'Driver with this name and phone number already exists.'})
        return JsonResponse({'status': 'error', 'message': 'Please Enter the Phone number and Name.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})



def delete_driver(request, id):
    if request.method == 'DELETE':
        try:
            driver = Driver.objects.get(id=id)
            driver.delete()
            return JsonResponse({'status': 'success'})
        except Driver.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Driver not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
from django.views.decorators.http import require_http_methods

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def edit_driver(request, id):
    try:
        driver = Driver.objects.get(id=id)
        driver.name = request.POST.get('name')
        driver.phone_number = request.POST.get('phone_number')
        driver.on_leave = request.POST.get('on_leave') == 'true'
        driver.has_msic = request.POST.get('has_msic') == 'true'
        driver.has_white_card = request.POST.get('has_white_card') == 'true'

        # Check if another driver (not this one) exists with the same name and phone number
        if Driver.objects.filter(name=driver.name, phone_number=driver.phone_number).exclude(id=driver.id).exists():
            return JsonResponse({'status': 'exists', 'message': 'Driver with this name and phone number already exists.'})
        else:
            driver.save()
            return JsonResponse({'status': 'success'})
    except Driver.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Driver not found'}, status=404)


def jobs_list(request):
    """Render the jobs list view."""
    jobs = Job.objects.all()  # Use plural to match the template
    for job in jobs:
        print(job.job_date)
    print(jobs)
    vehicles = Vehicle.objects.all()
    trailers = Trailer.objects.all()
    drivers = Driver.objects.all()
    drivers_list = [{'id': driver.id, 'name': driver.name, 'has_msic': driver.has_msic, 'has_whitecard': driver.has_white_card} for driver in drivers]


    rosters = Roster.objects.all()

    return render(request, 'job.html', {'jobs': jobs,'vehicles':vehicles,'trailers':trailers,'drivers':drivers_list,'rosters':rosters})  # Change 'job' to 'jobs'

def add_job(request):
    """Handle AJAX requests to add a new job."""
    if request.method == 'POST':
        job_name = request.POST.get('job_name', '').strip()
        job_count = request.POST.get('job_count', '').strip()
        print("date",request.POST.get('job_date', ''))
        job_date = request.POST.get('job_date', '')
        trailer_type = request.POST.get('trailer_type', '')

        if job_name and job_count and job_date and trailer_type:
            try:
                # Convert job_daate string to a datetime object
                # job_date = datetime.strptime(job_date, '%Y-%m-%d')  # Adjust format as necessary
                print("after date",job_date)
                job = Job.objects.create(
                    job_name=job_name,
                    job_count=job_count,
                    job_date=job_date,
                    trailer_type=trailer_type
                )
                return JsonResponse({'status': 'success', 'job': {
                    'id': job.id,
                    'job_name': job.job_name,
                    'job_count': job.job_count,
                    'job_date': job.job_date,
                    'trailer_type': job.trailer_type
                }})
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid date format. Please use YYYY-MM-DD.'})
        
        return JsonResponse({'status': 'error', 'message': 'Please fill in all fields.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def delete_job(request, id):
    """Handle AJAX requests to delete a job."""
    if request.method == 'DELETE':
        try:
            job = Job.objects.get(id=id)
            job.delete()
            return JsonResponse({'status': 'success'})
        except Job.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def edit_job(request, id):
    if request.method == 'POST':
        job = get_object_or_404(Job, id=id)

        job_name = request.POST.get('job_name')
        job_count = request.POST.get('job_count')
        job_date = request.POST.get('job_date')
        trailer_type = request.POST.get('trailer_type')

        # Validate input values
        if not job_name or not job_count or not trailer_type:
            return JsonResponse({'status': 'error', 'message': 'Please provide all fields.'}, status=400)

        # Validate job_date
        try:
            job_date = datetime.strptime(job_date, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

        # Update job fields
        job.job_name = job_name
        job.job_count = job_count
        job.job_date = job_date
        job.trailer_type = trailer_type

        # Save the job
        job.save()
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@csrf_exempt  # Use cautiously, consider proper CSRF protection
def add_roster(request):


        if request.method == 'POST':
            data = json.loads(request.body)
            print("Received Data:", data)

            try:
                # Parse the date from the incoming data
                job_date = datetime.strptime(data['date'], '%b. %d, %Y').date()
                print("Parsed job_date:", job_date)

                # Validate and parse start_time
                start_time_str = data.get('startTime')
                finish_time_str = data.get('finishTime')

                if not start_time_str:
                    return JsonResponse({'status': 'error', 'message': 'startTime cannot be empty.'})

                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                finish_time = None  # Default to None if not provided

                if finish_time_str:
                    try:
                        finish_time = datetime.strptime(finish_time_str, '%H:%M').time()
                    except ValueError:
                        return JsonResponse({'status': 'error', 'message': 'Invalid format for finishTime. Use HH:MM.'})

                # Retrieve related objects
                vehicles = Vehicle.objects.get(id=data['vehicleRegos'])
                trailer1 = Trailer.objects.get(id=data['trailerRegos'][0]) if data['trailerRegos'][0] else None
                trailer2 = Trailer.objects.get(id=data['trailerRegos'][1]) if len(data['trailerRegos']) > 1 and data['trailerRegos'][1] else None
                trailer3 = Trailer.objects.get(id=data['trailerRegos'][2]) if len(data['trailerRegos']) > 2 and data['trailerRegos'][2] else None
                driver = Driver.objects.get(id=data['driverName'])

                print("Vehicle:", vehicles.rego_number)
                print("Trailer1:", trailer1.rego_number if trailer1 else "None")
                print("Trailer2:", trailer2.rego_number if trailer2 else "None")
                print("Trailer3:", trailer3.rego_number if trailer3 else "None")
                print("Driver:", driver.name)

                # Create a new Roster instance
                roster = Roster.objects.create(
                    in_service=data['in_service'],
                    job_date=job_date,
                    vehicle=vehicles,
                    trailer1=trailer1,
                    trailer2=trailer2,
                    trailer3=trailer3,
                    trailer_type=data['trailerType'],
                    start_time=start_time,
                    end_time=finish_time,
                    client_name=data['clientName'],
                    wharf_status=data['wharfStatus'],
                    construction_site=data['constructionSite'],
                    driver=driver,
                    notes=data['notes']
                )
                roster.save()

                # Send SMS notification
                client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
                print("Twilio Config:", settings.YOUR_TWILIO_PHONE_NUMBER)

                # Prepare the SMS body
                message_body = (
                    f"Roster added!\n"
                    f"Date: {job_date}\n"
                    f"Vehicle Regos: {vehicles.rego_number}\n"
                    f"Trailer 1: {trailer1.rego_number if trailer1 else 'None'}\n"
                    f"Trailer 2: {trailer2.rego_number if trailer2 else 'None'}\n"
                    f"Trailer 3: {trailer3.rego_number if trailer3 else 'None'}\n"
                    f"Trailer Type: {data['trailerType']}\n"
                    f"Start Time: {start_time}\n"
                    f"End Time: {finish_time if finish_time else 'N/A'}\n"
                    f"Wharf Status: {data['wharfStatus']}\n"
                    f"Construction Site: {data['constructionSite']}\n"
                    f"Client: {data['clientName']}\n"
                    f"Driver: {driver.name}\n"
                    f"Notes: {data['notes']}\n"
                )

                print("Driver Phone Number:", driver.phone_number)
                message = client.messages.create(
                    body=message_body,
                    from_=twilio_phone_number,
                    to=driver.phone_number
                )
                # print("Message Sent:", message.sid)
                print("Message Sent")

                return JsonResponse({
                    'status': 'success',
                    'message': f"Roster created successfully. ID: {roster.id}",
                    'data': {
                        'id': roster.id,
                    }
                })
            except Vehicle.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Vehicle not found.'})
            except Trailer.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'One of the trailers was not found.'})
            except Driver.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Driver not found.'})
            except Exception as e:
                print("Error:", e)
                return JsonResponse({'status': 'error', 'message': str(e)})

        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# views.py
from django.http import JsonResponse
from .models import Driver

from django.http import JsonResponse
from .models import Driver  # Make sure to import your Driver model


# Twilio credentials

# def add_roster_and_notify(request):
#     if request.method == 'POST':
#         # Parse the incoming JSON data
#         data = json.loads(request.body)
        
#         # Save data in the database
#         roster = Roster(
#             date=data.get('date'),
#             vehicle_regos=data.get('vehicleRegos'),
#             trailer_regos=data.get('trailerRegos'),
#             trailer_type=data.get('trailerType'),
#             start_time=data.get('startTime'),
#             finish_time=data.get('finishTime'),
#             client_name=data.get('clientName'),
#             wharf_status=data.get('wharfStatus'),
#             construction_site=data.get('constructionSite'),
#             driver_name=data.get('driverName'),
#             notes=data.get('notes')
#         )
#         roster.save()

#         # Create a Twilio client
#         client = Client(account_sid, auth_token)

#         # Prepare the SMS body with relevant details
#         message_body = (
#             f"Roster added!\n"
#             f"Date: {data.get('date')}\n"
#             f"Vehicle Regos: {data.get('vehicleRegos')}\n"
#             f"Trailer Type: {data.get('trailerType')}\n"
#             f"Client: {data.get('clientName')}\n"
#             f"Driver: {data.get('driverName')}\n"
#             f"Notes: {data.get('notes')}\n"
#         )

#         # Send the SMS
#         message = client.messages.create(
#             body=message_body,
#             from_=twilio_phone_number,
#             to=recipient_phone_number
#         )

#         # Response back to the client
#         return JsonResponse({'status': 'success', 'sms_sid': message.sid})
#     else:
#         return JsonResponse({'error': 'Invalid request'}, status=400)

    

def get_filtered_drivers(request):
    if request.method == "GET":
        # Retrieve query parameters
        wharfStatus = request.GET.get('wharfStatus')
        constructionSite = request.GET.get('constructionSite')

        # Convert query parameters to Boolean values
        wharfStatus = wharfStatus.lower() == 'true' if wharfStatus is not None else False
        constructionSite = constructionSite.lower() == 'true' if constructionSite is not None else False

        # Debugging print statements
        print(f"Wharf Status: {wharfStatus}, Construction Site: {constructionSite}")

        if wharfStatus and constructionSite:
            # Both are True, fetch drivers with both `has_msic=True` and `has_white_card=True`
            print("Condition: YES YES")
            filtered_drivers = Driver.objects.filter(has_msic=True, has_white_card=True)
        elif wharfStatus or constructionSite:
            # Either one is True, fetch drivers matching either condition
            # Exclude drivers with both `has_msic=False` and `has_white_card=False` (like Nitin)
            print("Condition: YES NO or NO YES")
            filtered_drivers = Driver.objects.filter(
                Q(has_msic=wharfStatus) | Q(has_white_card=constructionSite)
            ).exclude(has_msic=False, has_white_card=False)
        else:
            # Both are False, fetch all drivers
            print("Condition: NO NO")
            filtered_drivers = Driver.objects.all()

        # Exclude drivers who are on leave in all cases
        filtered_drivers = filtered_drivers.exclude(on_leave=True)

        # Debugging print statement
        print("Filtered Drivers QuerySet:", filtered_drivers)

        # Prepare driver data for the response
        driver_data = [{'id': driver.id, 'name': driver.name} for driver in filtered_drivers]

        # Return the response
        return JsonResponse(driver_data, safe=False)

import csv
from django.http import HttpResponse
from .models import Roster

def export_roster_csv(request):
    # Create the HTTP response object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rosters.csv"'

    # Create a CSV writer
    writer = csv.writer(response)

    # Write the header row
    writer.writerow([
       'Runsheet Received', 'Job Date', 'Vehicle Rego Number', 'Driver Name', 
        'Trailer1 Rego Number', 'Trailer2 Rego Number', 'Trailer3 Rego Number', 
        'Trailer Type', 'Start Time', 'End Time', 
        'Client Name', 'Wharf Status', 'Construction Site', 'Notes'
    ])

    # Fetch all Roster objects and write to the CSV
    rosters = Roster.objects.all()
    for roster in rosters:
        writer.writerow([
            "Received" if roster.in_service else "Not Received",  
            roster.job_date.strftime('%Y-%m-%d') if roster.job_date else '',
            roster.vehicle.rego_number if roster.vehicle else '',
            roster.driver.name if roster.driver else '',
            roster.trailer1.rego_number if roster.trailer1 else '',
            roster.trailer2.rego_number if roster.trailer2 else '',
            roster.trailer3.rego_number if roster.trailer3 else '',
            roster.trailer_type,
            roster.start_time.strftime('%H:%M') if roster.start_time else '',
            roster.end_time.strftime('%H:%M') if roster.end_time else '',
            roster.client_name,
            roster.wharf_status,
            roster.construction_site,
            roster.notes,
        ])

    return response

def update_trailer_in_service(request):
    if request.method == 'POST':
        trailer_id = request.POST.get('trailer_id')
        in_service = request.POST.get('in_service') == 'true'
        try:
            trailer = Trailer.objects.get(id=trailer_id)
            trailer.in_service = in_service
            trailer.save()
            return JsonResponse({'status': 'success'})
        except Trailer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Trailer not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
def update_vehicle_in_service(request):
    vehicle_id = request.POST.get('vehicle_id')
    in_service = request.POST.get('in_service') == 'true'

    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        vehicle.in_service = in_service
        vehicle.save()
        return JsonResponse({'status': 'success'})
    except Vehicle.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Vehicle not found'}, status=404)
    
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_roster_service(request):
    if request.method == 'POST':
        # data = json.loads(request.body)
        roster_id = request.POST.get('roster_id')
        is_service =request.POST.get('is_service')== 'true'
        print("roster_id",roster_id,"is_service",is_service)
        # Fetch and update the roster record
        try:
            # print()
            roster = Roster.objects.get(id=roster_id)
            roster.in_service = is_service

            print("roster",roster)

            roster.save()
            print("roster after save ",roster)
            print("roster after save ",roster.in_service)

            return JsonResponse({'status': 'success'})
        except Roster.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Roster not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
