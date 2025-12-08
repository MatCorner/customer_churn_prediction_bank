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
from .utils import predict_churn_dummy
from django.utils.timesince import timesince


# =========================================================
# 1. PAGE RENDERING (HTML)
# =========================================================

def page_login(request):
    """Render Login Page"""
    return render(request, 'login.html')


def page_dashboard(request):
    """Render Client Dashboard"""
    return render(request, 'dashboard.html')


def page_manager_dashboard(request):
    """Render Manager Dashboard (New)"""
    return render(request, 'manager_dashboard.html')


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

    user = User.objects.create_user(username=username, password=password)

    if role == "client":
        Client.objects.create(user=user)
    else:
        # Create Staff profile
        Staff.objects.create(user=user, position="Manager")

    return Response({"message": "User created", "role": role})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    token, _ = Token.objects.get_or_create(user=user)

    # Check role to help frontend redirect
    role = "unknown"
    if hasattr(user, "client"):
        role = "client"
    elif hasattr(user, "staff"):
        role = "staff"

    return Response({
        "message": "Login successful",
        "token": token.key,
        "role": role  # Return role for redirection
    })


# =========================================================
# 3. MANAGER APIs
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    Returns list of all clients with REAL-TIME churn scores.
    Sorted by Churn Risk (High -> Low).
    """
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    data = []
    # Only list Clients
    for u in User.objects.filter(client__isnull=False):
        client = u.client

        # Auto-calculate risk
        score, risk = predict_churn_dummy(client)

        # Save warning status
        client.warning = 1 if risk == 'high' else 0
        client.save()

        entry = {
            "id": u.id,
            "username": u.username,
            "age": client.age,
            "gender": client.gender,
            "income": client.income_level,
            "churn_score": score,  # 0.00 - 1.00
            "churn_risk": risk  # low/medium/high
        }
        data.append(entry)

    # --- SORTING LOGIC ---
    # Sort by Churn Score Descending (Highest Risk First)
    data.sort(key=lambda x: x['churn_score'], reverse=True)

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_user_churn(request, user_id):
    """
    Manual re-analysis trigger (if needed).
    """
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    try:
        target_user = User.objects.get(id=user_id)
        if not hasattr(target_user, "client"):
            return Response({"error": "User is not a client"}, status=400)

        client = target_user.client
        score, risk = predict_churn_dummy(client)

        client.warning = 1 if risk == 'high' else 0
        client.save()

        return Response({
            "message": "Analysis complete",
            "prediction_result": {"score": score, "risk": risk}
        })
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


# =========================================================
# 4. CLIENT APIs (Profile, Wallet, Transactions)
# =========================================================

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_me(request):
    user = request.user
    if not hasattr(user, "client"):
        return Response({"error": "Not a client"}, status=400)
    client = user.client

    if request.method == 'GET':
        return Response({
            "username": user.username,
            "age": client.age,
            "gender": client.gender,
            "education_level": client.education_level,
            "income_level": client.income_level,
        })
    elif request.method == 'PUT':
        client.age = request.data.get("age", client.age)
        client.gender = request.data.get("gender", client.gender)
        client.education_level = request.data.get("education_level", client.education_level)
        client.income_level = request.data.get("income_level", client.income_level)
        client.save()

        # Calculate risk for client view (optional)
        score, risk = predict_churn_dummy(client)

        return Response({
            "message": "Profile updated",
            "prediction_result": {"score": score, "risk": risk}
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_accounts(request):
    card = DebitCard.objects.filter(user=request.user).first()
    if not card: return Response({"balance": 0.00})
    return Response({"balance": card.balance, "card_no": card.card_no})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    amount = Decimal(str(request.data.get("amount", 0)))
    card = DebitCard.objects.filter(user=request.user).first()
    if not card: return Response({"error": "No card"}, status=400)

    card.balance += amount
    card.save()

    Transaction.objects.create(
        subject_card_no=card.card_no, transaction_type='deposit', amount=amount, status="success"
    )
    return Response({"message": "Deposit success"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    amount = Decimal(str(request.data.get("amount", 0)))
    card = DebitCard.objects.filter(user=request.user).first()
    if not card or card.balance < amount: return Response({"error": "Insufficient funds"}, status=400)

    card.balance -= amount
    card.save()
    Transaction.objects.create(
        subject_card_no=card.card_no, transaction_type='withdraw', amount=amount, status="success"
    )
    return Response({"message": "Payment success"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    amount = Decimal(str(request.data.get("amount", 0)))
    card = DebitCard.objects.filter(user=request.user).first()
    if not card or card.balance < amount: return Response({"error": "Insufficient funds"}, status=400)

    card.balance -= amount
    card.save()
    Transaction.objects.create(
        subject_card_no=card.card_no, transaction_type='transfer', amount=amount, status="success"
    )
    return Response({"message": "Transfer success"})


# Generic transaction endpoint (Legacy support)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    return Response({"message": "Generic transaction created"})


# =========================================================
# MANAGER: INTELLIGENT ALERTS (VIP & TRANSACTIONS ONLY)
# =========================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_alerts(request):
    """
    Smart Intelligence: Only returns 'Events' (Transactions / VIP).
    Risk warnings are excluded (handled in Client List sorting).
    """
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    alerts = []

    # Threshold for "Important" news
    threshold = 3000

    # Fetch recent large transactions
    big_txs = Transaction.objects.filter(amount__gte=threshold).order_by('-create_time')[:10]

    for tx in big_txs:
        card = DebitCard.objects.filter(card_no=tx.subject_card_no).first()
        if not card: continue
        username = card.user.username

        # Logic A: Capital Outflow (Money Leaving)
        if tx.transaction_type == 'withdraw' or tx.transaction_type == 'transfer':
            alerts.append({
                "type": "danger",  # Red Icon
                "icon": "💸",
                "message": f"Large Outflow: [{username}] moved ${tx.amount} out.",
                "time": timesince(tx.create_time).split(',')[0] + " ago",
                "sort_key": tx.create_time.timestamp()
            })

        # Logic B: Capital Inflow & VIP Events
        elif tx.transaction_type == 'deposit':
            # Check if this deposit made them a VIP (>50k)
            is_vip = card.balance > 50000

            # Message formatting
            msg = f"Big Deposit: [{username}] added ${tx.amount}."
            icon = "💰"
            type_color = "success"  # Green

            if is_vip:
                msg = f"🌟 VIP PROMOTION: [{username}] reached Gold status with ${tx.amount} deposit!"
                icon = "🏆"  # Trophy icon for VIP

            alerts.append({
                "type": type_color,
                "icon": icon,
                "message": msg,
                "time": timesince(tx.create_time).split(',')[0] + " ago",
                "sort_key": tx.create_time.timestamp()
            })

    # Sort by time (Newest first)
    alerts.sort(key=lambda x: x['sort_key'], reverse=True)

    return Response(alerts)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def client_alerts(request):
    card = DebitCard.objects.filter(user=request.user).first()
    if not card: return Response([])

    alerts = []

    # 1. VIP
    if card.balance > 50000:
        alerts.append({
            "is_vip_notice": True,
            "icon": "👑",
            "title": "Gold VIP Status Active",
            "desc": "You are enjoying exclusive low interest rates and premium support.",
            "amount": "",
            "time": "Now"
        })

    # 2. deal
    txs = Transaction.objects.filter(subject_card_no=card.card_no).order_by('-create_time')[:5]

    for tx in txs:
        icon = "📝"
        title = "Transaction"
        sign = ""
        color_class = "text-dark"

        if tx.transaction_type == 'deposit':
            icon = "💰"
            title = "Deposit Received"
            sign = "+"
            color_class = "text-success"
        elif tx.transaction_type == 'withdraw':
            icon = "🧾"
            title = "Bill Payment / Withdrawal"
            sign = "-"
            color_class = "text-danger"
        elif tx.transaction_type == 'transfer':
            icon = "💸"
            title = f"Transfer to Acc #{tx.target_card_no}"
            sign = "-"
            color_class = "text-danger"

        alerts.append({
            "is_vip_notice": False,
            "icon": icon,
            "title": title,
            "desc": timesince(tx.create_time).split(',')[0] + " ago",
            "amount": f"{sign}${tx.amount}",
            "color_class": color_class,
            "time": tx.create_time
        })

    return Response(alerts)