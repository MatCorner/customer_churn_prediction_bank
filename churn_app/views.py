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
      
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    role = request.data.get("role")  # "client" / "staff"

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    if role not in ["client", "staff"]:
        return Response({"error": "Invalid role"}, status=400)

    user = User.objects.create_user(username=username, password=password)

    if role == "client":
        Client.objects.create(user=user)

    if role == "staff":
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user

    # 判断客户或管理员
    if hasattr(user, "client"):
        client = user.client
        return Response({
            "username": user.username,
            "role": "client",
            "age": client.age,
            "gender": client.gender,
            "income_category": client.income_category,
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
        client.income_category = request.data.get("income_category", client.income_category)
        client.save()
        return Response({"message": "Client profile updated"})

    if hasattr(user, "staff"):
        staff = user.staff
        staff.position = request.data.get("position", staff.position)
        staff.save()
        return Response({"message": "Staff profile updated"})

    return Response({"error": "User has no profile role"}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account(request):
    user = request.user

    if not hasattr(user, "client"):
        return Response({"error": "Only clients can create accounts"}, status=403)

    account_type = request.data.get("account_type")  # debit / credit
    credit_limit = request.data.get("credit_limit")

    if account_type not in ["debit", "credit"]:
        return Response({"error": "Invalid account type"}, status=400)

    if account_type == "debit":
        acc = DebitCard.objects.create(user=user, balance=0)
    else:
        if credit_limit is None:
            return Response({"error": "Credit account requires credit_limit"}, status=400)
        acc = CreditCard.objects.create(user=user, credit_limit=credit_limit)

    return Response({
        "message": "Account created",
        "type": account_type,
        "account_id": acc.id
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    action = request.data.get("action")  # deposit / withdraw / transfer
    amount = Decimal(str(request.data.get("amount")))
    sender_account_id = request.data.get("sender_account")
    recipient_account_id = request.data.get("recipient_account")

    try:
        sender = DebitCard.objects.select_for_update().get(id=sender_account_id)
    except DebitCard.DoesNotExist:
        return Response({"error": "Sender account not found"}, status=404)

    with db_transaction.atomic():
        if action == "deposit":
            sender.balance += amount
            sender.save()

        elif action == "withdraw":
            if sender.balance < amount:
                return Response({"error": "Insufficient balance"}, status=400)
            sender.balance -= amount
            sender.save()

        elif action == "transfer":
            try:
                recipient = DebitCard.objects.select_for_update().get(id=recipient_account_id)
            except DebitCard.DoesNotExist:
                return Response({"error": "Recipient account not found"}, status=404)

            if sender.balance < amount:
                return Response({"error": "Insufficient balance"}, status=400)

            sender.balance -= amount
            recipient.balance += amount
            sender.save()
            recipient.save()

        else:
            return Response({"error": "Invalid action"}, status=400)

        Transaction.objects.create(
            sender=sender,
            recipient=None if action != "transfer" else recipient,
            amount=amount,
            action=action
        )

    return Response({"message": f"{action.capitalize()} successful"})

# staff
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    # 必须是 staff
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    users = User.objects.all().order_by("id")
    results = []

    for u in users:
        item = {
            "username": u.username,
            "id": u.id,
        }

        # 客户 (client)
        if hasattr(u, "client"):
            item["role"] = "client"

            
            #调用 Churn 预测模型
            churn_score, churn_risk = predict_churn_dummy(u.client)
            item["churn_score"] = churn_score
            item["churn_risk"] = churn_risk

            # 客户基础信息
            item["client_info"] = {
                "age": u.client.age,
                "gender": u.client.gender,
                "marital_status": u.client.marital_status,
                "income_category": u.client.income_category,
            }

        # 管理员（staff）
        elif hasattr(u, "staff"):
            item["role"] = "staff"
            item["staff_info"] = {
                "position": u.staff.position
            }

        else:
            item["role"] = "unknown"

        results.append(item)

    return Response(results)

# staff views all accounts
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_accounts(request):
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    data = []

    # 借记卡
    for acc in DebitCard.objects.all():
        data.append({
            "type": "debit",
            "account_id": acc.id,
            "owner": acc.user.username,
            "balance": str(acc.balance),
            "created_at": acc.created_at,
        })

    # 信用卡
    for acc in CreditCard.objects.all():
        data.append({
            "type": "credit",
            "account_id": acc.id,
            "owner": acc.user.username,
            "credit_limit": str(acc.credit_limit),
            "created_at": acc.created_at,
        })

    return Response(data)

# staff views transaction
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    if not hasattr(request.user, "staff"):
        return Response({"error": "Permission denied"}, status=403)

    txs = Transaction.objects.all().order_by('-created_at')
    data = []

    for t in txs:
        data.append({
            "id": t.id,
            "action": t.action,
            "amount": str(t.amount),
            "sender_account": t.sender.id if t.sender else None,
            "recipient_account": t.recipient.id if t.recipient else None,
            "sender_owner": t.sender.user.username if t.sender else None,
            "recipient_owner": t.recipient.user.username if t.recipient else None,
            "timestamp": t.created_at
        })

    return Response(data)

# user views transaction
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_transactions(request):
    user = request.user

    # 客户必须有 client 角色
    if not hasattr(user, "client"):
        return Response({"error": "Permission denied"}, status=403)

    txs = Transaction.objects.filter(
        sender__user=user
    ) | Transaction.objects.filter(
        recipient__user=user
    )

    txs = txs.order_by('-created_at')
    data = []

    for t in txs:
        data.append({
            "id": t.id,
            "action": t.action,
            "amount": str(t.amount),
            "sender": t.sender.id if t.sender else None,
            "recipient": t.recipient.id if t.recipient else None,
            "timestamp": t.created_at
        })

    return Response(data)
