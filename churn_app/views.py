from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Profile
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json


      
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')  # 'customer' or 'manager'

    if not username or not password or role not in ['customer', 'manager']:
        return Response({'error': 'username, password, and valid role required'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    # Create user
    user = User.objects.create_user(username=username, password=password)

    # Create profile
    profile = Profile.objects.create(
        user=user,
        role=role,
        age=data.get('age', 0) if role == 'customer' else None,
        marital_status=data.get('marital_status', '') if role == 'customer' else '',
        balance=data.get('balance', 0) if role == 'customer' else 0,
        tenure=data.get('tenure', 0) if role == 'customer' else 0
    )

    return Response({
        'message': f'{role.capitalize()} registered successfully!',
        'user_id': user.id
    }, status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    GET /api/users/
    Only managers can see all users.
    Customers can only see their own profile.
    Optional: ?role=customer or ?role=manager to filter
    """
    # Authenticate the user using JWT
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)

    # Only managers can list other users
    if profile.role != 'manager':
        return Response({'error': 'Permission denied'}, status=403)

    # Optional filtering
    role_filter = request.GET.get('role')
    if role_filter in ['customer', 'manager']:
        profiles = Profile.objects.filter(role=role_filter)
    else:
        profiles = Profile.objects.all()

    users_list = []
    for p in profiles:
        users_list.append({
            'id': p.user.id,
            'username': p.user.username,
            'role': p.role,
            'age': p.age,
            'marital_status': p.marital_status,
            'balance': p.balance,
            'tenure': p.tenure
        })

    return Response(users_list)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request, user_id):
    try:
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    logged_in_profile = Profile.objects.get(user=request.user)

    # Customers can only view their own profile
    if logged_in_profile.role == 'customer' and logged_in_profile.user.id != profile.user.id:
        return Response({'error': 'Permission denied'}, status=403)

    return Response({
        'id': profile.user.id,
        'username': profile.user.username,
        'role': profile.role,
        'age': profile.age,
        'marital_status': profile.marital_status,
        'balance': profile.balance,
        'tenure': profile.tenure
    })
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request, user_id):
    try:
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    logged_in_profile = Profile.objects.get(user=request.user)

    # Customers can only update their own profile
    if logged_in_profile.role == 'customer' and logged_in_profile.user.id != profile.user.id:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    data = request.data  # DRF auto-parses JSON

    if profile.role == 'customer':
        profile.age = data.get('age', profile.age)
        profile.marital_status = data.get('marital_status', profile.marital_status)
        profile.balance = data.get('balance', profile.balance)
        profile.tenure = data.get('tenure', profile.tenure)

    profile.save()

    return JsonResponse({
        'message': 'Profile updated successfully',
        'profile': {
            'id': profile.user.id,
            'username': profile.user.username,
            'role': profile.role,
            'age': profile.age,
            'marital_status': profile.marital_status,
            'balance': profile.balance,
            'tenure': profile.tenure
        }
    })