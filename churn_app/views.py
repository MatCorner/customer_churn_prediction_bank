from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
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
from .models import Profile, Transaction
from django.db import transaction as db_transaction
from decimal import Decimal
import json

# 进行交易
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    data = request.data
    action = data.get('action')
    try:
        amount = Decimal(str(data.get('amount')))
    except:
        return Response({"error": "Invalid amount"}, status=400)

    recipient_username = data.get('recipient')

    with db_transaction.atomic():
        sender_profile = Profile.objects.select_for_update().get(user=request.user)

        recipient_profile = None
        if action == "transfer":
            if not recipient_username:
                return Response({"error": "Recipient username required"}, status=400)
            try:
                recipient_user = User.objects.get(username=recipient_username)
                recipient_profile = Profile.objects.select_for_update().get(user=recipient_user)
            except User.DoesNotExist:
                return Response({"error": "Recipient not found"}, status=404)

            if sender_profile.balance < amount:
                return Response({"error": "Insufficient balance"}, status=400)

            sender_profile.balance -= amount
            recipient_profile.balance += amount
            sender_profile.save()
            recipient_profile.save()

        elif action == "deposit":
            sender_profile.balance += amount
            sender_profile.save()

        elif action == "withdraw":
            if sender_profile.balance < amount:
                return Response({"error": "Insufficient balance"}, status=400)
            sender_profile.balance -= amount
            sender_profile.save()

        else:
            return Response({"error": "Invalid action"}, status=400)

        Transaction.objects.create(
            sender=sender_profile.user,
            recipient=recipient_profile.user if recipient_profile else None,
            amount=amount,
            action=action
        )

    return Response({"message": f"{action.capitalize()} successful!"})


# 用户查看自己的交易
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_transactions(request):
    profile = Profile.objects.get(user=request.user)

    transactions = Transaction.objects.filter(
        sender=profile
    ) | Transaction.objects.filter(
        recipient=profile
    )

    data = []
    for t in transactions.order_by('-timestamp'):
        data.append({
            "id": t.id,
            "action": t.action,
            "amount": str(t.amount),
            "sender": t.sender.user.username if t.sender else None,
            "recipient": t.recipient.user.username if t.recipient else None,
            "time": t.timestamp,
        })

    return Response(data)

# 管理员查看所有的交易
# 需要加按id查看的功能
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_transactions(request):
    admin_profile = Profile.objects.get(user=request.user)

    if admin_profile.role != 'manager':
        return Response({"error": "Permission denied"}, status=403)

    transactions = Transaction.objects.all().order_by('-timestamp')

    data = []
    for t in transactions:
        data.append({
            "id": t.id,
            "action": t.action,
            "amount": str(t.amount),
            "sender": t.sender.username if t.sender else None,
            "recipient": t.recipient.username if t.recipient else None,
            "time": t.created_at
        })

    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, transaction_id):
    try:
        t = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found"}, status=404)

    profile = Profile.objects.get(user=request.user)

    # 客户只能查看自己的交易
    if profile.role == 'customer' and t.sender != request.user and t.recipient != request.user:
        return Response({"error": "Permission denied"}, status=403)

    data = {
        "id": t.id,
        "action": t.action,
        "amount": str(t.amount),
        "sender": t.sender.username if t.sender else None,
        "recipient": t.recipient.username if t.recipient else None,
        "time": t.created_at
    }
    return Response(data)


# 注册    
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

# 管理员查看所有的用户
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

# 登录
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
 
# 用户查看自己的档案   
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

# 用户查看自己的余额 功能是否和my_profile有一定重复？
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_balance(request):
    profile = Profile.objects.get(user=request.user)
    return Response({
        "username": profile.user.username,
        "balance": profile.balance
    })

# 管理员查看特定用户的余额 
# 该功能仅作测试用
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_balance(request, user_id):
    admin_profile = Profile.objects.get(user=request.user)
    if admin_profile.role != 'manager':
        return Response({"error": "Permission denied"}, status=403)

    try:
        profile = Profile.objects.get(user__id=user_id)
    except Profile.DoesNotExist:
        return Response({"error": "User not found"}, 404)

    return Response({
        "username": profile.user.username,
        "balance": profile.balance
    })

# 用户更新档案
# 管理员是否能直接更新档案    
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
    
# 流失预测模型示例
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def churn_prediction(request):
#     profile = Profile.objects.get(user=request.user)

#     # 特征工程（示例）
#     num_transactions = Transaction.objects.filter(sender=profile).count()

#     features = {
#         "age": profile.age,
#         "balance": float(profile.balance),
#         "tenure": profile.tenure,
#         "num_transactions": num_transactions,
#     }

#     from .ml.churn_predictor import predict_churn
#     prob = predict_churn(features)

#     return Response({
#         "username": profile.user.username,
#         "churn_probability": prob
#     })
