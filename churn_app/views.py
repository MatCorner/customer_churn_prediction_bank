from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Client, Staff, DebitCard, CreditCard, Transaction
from decimal import Decimal
from django.db import transaction as db_transaction
from .utils import predict_churn_dummy


# User Register & Login
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

    return Response({"message": "Login successful", "username": username})


# Profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user

    if hasattr(user, "client"):
        client = user.client
        return Response({
            "username": user.username,
            "role": "client",
            "age": client.age,
            "gender": client.gender,
            "marital_status": client.marital_status,
            "income_level": client.income_level,
        })

    if hasattr(user, "staff"):
        staff = user.staff
        return Response({
            "username": user.username,
            "role": "staff",
            "position": staff.position,
        })

    return Response({"error": "User has no role"}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user

    if hasattr(user, "client"):
        client = user.client
        client.age = request.data.get("age", client.age)
        client.gender = request.data.get("gender", client.gender)
        client.marital_status = request.data.get("marital_status", client.marital_status)
        client.income_level = request.data.get("income_level", client.income_level)
        client.save()
        return Response({"message": "Client profile updated"})

    if hasattr(user, "staff"):
        staff = user.staff
        staff.position = request.data.get("position", staff.position)
        staff.save()
        return Response({"message": "Staff profile updated"})

    return Response({"error": "User has no profile role"}, status=400)


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
        acc = DebitCard.objects.create(
            user=user,
            balance=0
        )
        return Response({
            "message": "Debit card created",
            "debit_id": acc.debit_id
        })

    elif account_type == "credit":
        if credit_limit is None:
            return Response({"error": "credit account needs credit_limit"}, status=400)

        acc = CreditCard.objects.create(
            user=user,
            credit_limit=Decimal(str(credit_limit)),
            available_limit=Decimal(str(credit_limit))
        )
        return Response({
            "message": "Credit card created",
            "credit_id": acc.credit_id
        })

    return Response({"error": "Invalid account type"}, status=400)


# Transaction (deposit / withdraw / transfer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    action = request.data.get("action")  # deposit / withdraw / transfer
    amount = Decimal(str(request.data.get("amount")))
    subject_card_no = request.data.get("subject_card_no")
    target_card_no = request.data.get("target_card_no")

    try:
        subject_card = DebitCard.objects.select_for_update().get(card_no=subject_card_no)
    except DebitCard.DoesNotExist:
        return Response({"error": "Subject card not found"}, status=404)

    with db_transaction.atomic():
        # deposit
        if action == "deposit":
            subject_card.balance += amount
            subject_card.save()

        # withdraw
        elif action == "withdraw":
            if subject_card.balance < amount:
                return Response({"error": "Insufficient balance"}, status=400)
            subject_card.balance -= amount
            subject_card.save()

        # transfer
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

        # create transaction record
        Transaction.objects.create(
            subject_card_no=subject_card_no,
            target_card_no=target_card_no if action == "transfer" else None,
            transaction_type=action,
            amount=amount,
            status="success"
        )

    return Response({"message": f"{action} successful"})


# Staff: List users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    data = []

    for u in User.objects.all():
        entry = {"id": u.id, "username": u.username}

        if hasattr(u, "client"):
            entry["role"] = "client"
            churn_score, churn_risk = predict_churn_dummy(u.client)
            entry.update({
                "age": u.client.age,
                "gender": u.client.gender,
                "marital_status": u.client.marital_status,
                "income_level": u.client.income_level,
                "churn_score": churn_score,
                "churn_risk": churn_risk
            })
        elif hasattr(u, "staff"):
            entry["role"] = "staff"
            entry["position"] = u.staff.position
        else:
            entry["role"] = "unknown"

        data.append(entry)

    return Response(data)



# Staff: List all accounts
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_accounts(request):
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    data = []

    for acc in DebitCard.objects.all():
        data.append({
            "type": "debit",
            "card_no": acc.card_no,
            "owner": acc.user.username,
            "balance": str(acc.balance),
        })

    for acc in CreditCard.objects.all():
        data.append({
            "type": "credit",
            "card_no": acc.card_no,
            "owner": acc.user.username,
            "credit_limit": str(acc.credit_limit),
            "available_limit": str(acc.available_limit),
        })

    return Response(data)



# Staff: All transaction history
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    txs = Transaction.objects.all().order_by('-create_time')

    data = []
    for t in txs:
        data.append({
            "transaction_id": t.transaction_id,
            "subject_card_no": t.subject_card_no,
            "target_card_no": t.target_card_no,
            "type": t.transaction_type,
            "amount": str(t.amount),
            "status": t.status,
            "timestamp": t.create_time,
        })

    return Response(data)



# Client: My Transactions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_transactions(request):
    user = request.user

    if not hasattr(user, "client"):
        return Response({"error": "Permission denied"}, status=403)

    card_numbers = list(DebitCard.objects.filter(user=user).values_list("card_no", flat=True))

    txs = Transaction.objects.filter(
        subject_card_no__in=card_numbers
    ) | Transaction.objects.filter(
        target_card_no__in=card_numbers
    )

    txs = txs.order_by('-create_time')

    data = []
    for t in txs:
        data.append({
            "transaction_id": t.transaction_id,
            "subject_card_no": t.subject_card_no,
            "target_card_no": t.target_card_no,
            "type": t.transaction_type,
            "amount": str(t.amount),
            "status": t.status,
            "timestamp": t.create_time,
        })

    return Response(data)
