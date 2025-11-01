from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Profile
from django.views.decorators.http import require_http_methods
import json


      
@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')  # 'customer' or 'manager'

    if not username or not password or role not in ['customer', 'manager']:
        return JsonResponse({'error': 'username, password, and valid role required'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)

    # Create User
    user = User.objects.create_user(username=username, password=password)

    # Create Profile
    profile = Profile.objects.create(
        user=user,
        role=role,
        age=data.get('age', 0) if role=='customer' else None,
        marital_status=data.get('marital_status', '') if role=='customer' else '',
        balance=data.get('balance', 0) if role=='customer' else 0,
        tenure=data.get('tenure', 0) if role=='customer' else 0
    )

    return JsonResponse({
        'message': f'{role.capitalize()} registered successfully!',
        'user_id': user.id
    }, status=201)

@csrf_exempt
@require_http_methods(["GET"])
def list_users(request):
    """
    GET /api/users/?role=customer
    GET /api/users/?role=manager
    If role is not specified, returns all users.
    """
    role = request.GET.get('role')  # Optional: 'customer' or 'manager'

    # Filter profiles by role if specified
    if role in ['customer', 'manager']:
        profiles = Profile.objects.filter(role=role)
    else:
        profiles = Profile.objects.all()

    # Build response data
    users_list = []
    for profile in profiles:
        users_list.append({
            'id': profile.user.id,
            'username': profile.user.username,
            'role': profile.role,
            'age': profile.age,
            'marital_status': profile.marital_status,
            'balance': profile.balance,
            'tenure': profile.tenure
        })

    return JsonResponse(users_list, safe=False, status=200)