from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Customer
import json

@csrf_exempt
def customer_list_create(request):
    if request.method == 'GET':
        # Return all customers
        customers = list(Customer.objects.values(
            'id', 'user__username', 'age', 'marital_status', 'balance', 'tenure'
        ))
        return JsonResponse(customers, safe=False)

    elif request.method == 'POST':
        # Add a new customer
        data = json.loads(request.body)

        # Create a User first
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)

        # Create Customer linked to this User
        customer = Customer.objects.create(
            user=user,
            age=data.get('age', 0),
            marital_status=data.get('marital_status', ''),
            balance=data.get('balance', 0),
            tenure=data.get('tenure', 0)
        )

        return JsonResponse({
            'message': 'Customer created successfully',
            'customer_id': customer.id
        }, status=201)
