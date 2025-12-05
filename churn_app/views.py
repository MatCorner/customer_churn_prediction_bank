from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Client, Staff, DebitCard, CreditCard, Transaction
from decimal import Decimal
from django.db import transaction as db_transaction
from rest_framework.authtoken.models import Token
# Import the actual prediction function (make sure utils.py is updated)
from .utils import predict_churn_dummy


# =========================================================
# 1. FRONTEND PAGE RENDERING
# =========================================================

def page_login(request):
    """Render the Login HTML Page"""
    return render(request, 'login.html')


def page_dashboard(request):
    """Render the Dashboard HTML Page"""
    return render(request, 'dashboard.html')


# =========================================================
# 2. AUTHENTICATION
# =========================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    role = request.data.get("role")  # client / staff

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    if role not in ["client", "staff"]:
        return Response({"error": "Invalid role"}, status=400)

    user = User.objects.create_user(username=username, password=password)

    if role == "client":
        Client.objects.create(user=user)
    else:
        Staff.objects.create(user=user)

    return Response({"message": "User created successfully", "role": role})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    # get or create token
    token, created = Token.objects.get_or_create(user=user)

    return Response({
        "message": "Login successful",
        "username": username,
        "token": token.key
    })


# =========================================================
# 3. PROFILE & AI PREDICTION
# =========================================================
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_me(request):
    user = request.user

    if not hasattr(user, "client"):
        return Response({"error": "User is not a client"}, status=400)

    client = user.client

    if request.method == 'GET':
        return Response({
            "username": user.username,
            "role": "client",
            "age": client.age,
            "gender": client.gender,
            "marital_status": getattr(client, 'marital_status', 'Single'),
            "income_level": client.income_level,
            "education_level": client.education_level,
        })

    elif request.method == 'PUT':
        client.age = request.data.get("age", client.age)
        client.gender = request.data.get("gender", client.gender)
        client.education_level = request.data.get("education_level", client.education_level)
        client.income_level = request.data.get("income_level", client.income_level)
        client.save()

        churn_prob, risk_level = predict_churn_dummy(client)

        client.warning = 1 if risk_level == 'high' else 0
        client.save()

        return Response({
            "message": "Profile updated successfully",
            "prediction_result": {
                "score": churn_prob,
                "risk": risk_level
            }
        })


# Helper to reuse logic
def _get_profile_response(user):
    if hasattr(user, "client"):
        client = user.client
        return Response({
            "username": user.username,
            "role": "client",
            "age": client.age,
            "gender": client.gender,
            "marital_status": getattr(client, 'marital_status', 'Single'),
            "income_level": client.income_level,
            "education_level": client.education_level,
        })
    return Response({"error": "Not a client"}, status=400)


# =========================================================
# 4. DASHBOARD HELPER APIS (For VIP & Wallet)
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_accounts(request):
    """
    Simplified API for the Dashboard to get Balance (Gold VIP logic).
    Automatically finds the user's Debit Card.
    """
    user = request.user
    card = DebitCard.objects.filter(user=user).first()

    if not card:
        return Response({"balance": 0.00, "card_no": "No Card"})

    return Response({
        "balance": card.balance,
        "card_no": card.card_no,
        "type": "debit"
    })


# Simplified Wrappers for Dashboard Actions (Deposit/Withdraw)
# These call the core logic but don't require typing a card number manually

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    amount = Decimal(str(request.data.get("amount", 0)))
    card = DebitCard.objects.filter(user=request.user).first()
    if not card: return Response({"error": "No card found"}, status=400)

    card.balance += amount
    card.save()

    # Create Record
    Transaction.objects.create(
        subject_card_no=card.card_no,
        transaction_type='deposit',
        amount=amount,
        status="success"
    )
    return Response({"message": "Deposit successful"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    amount = Decimal(str(request.data.get("amount", 0)))
    card = DebitCard.objects.filter(user=request.user).first()
    if not card: return Response({"error": "No card found"}, status=400)

    if card.balance < amount:
        return Response({"error": "Insufficient funds"}, status=400)

    card.balance -= amount
    card.save()

    Transaction.objects.create(
        subject_card_no=card.card_no,
        transaction_type='withdraw',
        amount=amount,
        status="success"
    )
    return Response({"message": "Payment successful"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    # Simplified transfer for demo
    amount = Decimal(str(request.data.get("amount", 0)))
    card = DebitCard.objects.filter(user=request.user).first()
    if not card or card.balance < amount:
        return Response({"error": "Insufficient funds"}, status=400)

    card.balance -= amount
    card.save()

    Transaction.objects.create(
        subject_card_no=card.card_no,
        transaction_type='transfer',
        amount=amount,
        status="success"
    )
    return Response({"message": "Transfer successful"})


# =========================================================
# 5. STAFF & ADMIN APIS
# =========================================================

# Staff: List users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    # Kept original logic
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)
    data = []
    for u in User.objects.all():
        entry = {"id": u.id, "username": u.username}
        if hasattr(u, "client"):
            entry["role"] = "client"
            # Optional: Add churn score here for Manager view
            churn_score, churn_risk = predict_churn_dummy(u.client)
            entry.update({
                "age": u.client.age,
                "churn_score": churn_score,
                "churn_risk": churn_risk
            })
        elif hasattr(u, "staff"):
            entry["role"] = "staff"
        data.append(entry)
    return Response(data)


# Create Debit / Credit Card
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account(request):
    user = request.user
    if not hasattr(user, "client"):
        return Response({"error": "Only clients can create accounts"}, status=403)

    account_type = request.data.get("account_type")
    credit_limit = request.data.get("credit_limit")

    if account_type == "debit":
        acc = DebitCard.objects.create(user=user, balance=0)
        return Response({"message": "Debit card created", "debit_id": acc.debit_id})

    elif account_type == "credit":
        acc = CreditCard.objects.create(
            user=user,
            credit_limit=Decimal(str(credit_limit or 10000)),
            available_limit=Decimal(str(credit_limit or 10000))
        )
        return Response({"message": "Credit card created", "credit_id": acc.credit_id})

    return Response({"error": "Invalid account type"}, status=400)


# The Original Generic Transaction Logic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    action = request.data.get("action")
    amount = Decimal(str(request.data.get("amount")))
    subject_card_no = request.data.get("subject_card_no")
    target_card_no = request.data.get("target_card_no")

    try:
        subject_card = DebitCard.objects.select_for_update().get(card_no=subject_card_no)
    except DebitCard.DoesNotExist:
        return Response({"error": "Subject card not found"}, status=404)

    with db_transaction.atomic():
        if action == "deposit":
            subject_card.balance += amount
            subject_card.save()
        elif action == "withdraw":
            if subject_card.balance < amount:
                return Response({"error": "Insufficient balance"}, status=400)
            subject_card.balance -= amount
            subject_card.save()
        elif action == "transfer":
            if subject_card.balance < amount:
                return Response({"error": "Insufficient balance"}, status=400)
            try:
                target_card = DebitCard.objects.select_for_update().get(card_no=target_card_no)
            except DebitCard.DoesNotExist:
                return Response({"error": "Target card not found"}, status=404)
            subject_card.balance -= amount
            target_card.balance += amount
            subject_card.save()
            target_card.save()
        else:
            return Response({"error": "Invalid transaction type"}, status=400)

        Transaction.objects.create(
            subject_card_no=subject_card_no,
            target_card_no=target_card_no if action == "transfer" else None,
            transaction_type=action,
            amount=amount,
            status="success"
        )

    return Response({"message": f"{action} successful"})