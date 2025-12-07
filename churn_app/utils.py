import os
import joblib
import pandas as pd
from django.conf import settings
from django.db.models import Sum
from churn_app.models import Transaction, DebitCard

# Paths to artifacts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'churn_app/churn_model.pkl')
ENCODER_PATH = os.path.join(settings.BASE_DIR, 'churn_app/model_encoders.pkl')

model = None
encoders = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODER_PATH)
        print("✅ utils.py: Model Loaded Successfully")
except Exception as e:
    print(f"❌ utils.py: Failed to load model: {e}")


def safe_encode(col_name, value):
    """Helper to encode categorical values."""
    if not encoders or col_name not in encoders:
        return 0
    try:
        return encoders[col_name].transform([value])[0]
    except ValueError:
        return 0


def predict_churn_dummy(client):
    """
    Real-time prediction logic based on actual DB transactions.
    """
    if not model:
        return 0.5, "Model Missing"

    # ============================================================
    # 1. Fetch Real Data from Database
    # ============================================================
    debit_card = client.user.debitcard_set.first()

    real_balance = 0.0
    real_trans_amt = 0.0
    real_trans_ct = 0

    if debit_card:
        real_balance = float(debit_card.balance)

        # Query the actual Transaction table
        txs = Transaction.objects.filter(subject_card_no=debit_card.card_no)

        # Count rows (Real number of user actions)
        real_trans_ct = txs.count()

        # Sum amount (Real volume of money moved)
        agg = txs.aggregate(total=Sum('amount'))
        real_trans_amt = float(agg['total']) if agg['total'] else 0.0

    # ============================================================
    # 2. Logic Mapping (Realistic Adjustment)
    # ============================================================

    # A. Transaction Count Adjustment (Time Acceleration)
    # Since manual testing is slow, we treat 1 click as 10 transactions.
    # This simulates "months" of activity in "minutes".
    # NO hardcoded "80", purely based on your clicks.
    adjusted_trans_ct = real_trans_ct * 3

    # B. Debt Simulation (Mapping Asset to Liability)
    # The model expects "Total_Revolving_Bal" (Credit Card Debt).
    # Logic: Higher Balance -> Higher Creditworthiness -> Simulating usage.
    # We map 50% of your debit balance as "active credit usage".
    simulated_revolving_bal = real_balance * 0.5

    # Cap it at 2500 (typical avg for credit cards) to prevent outliers
    if simulated_revolving_bal > 2500:
        simulated_revolving_bal = 2500

    # C. Credit Limit Simulation
    # Higher balance implies higher credit limit eligibility.
    simulated_credit_limit = max(real_balance * 2, 3000)

    # Debug info for verification
    print("\n" + "=" * 40)
    print(f"🤖 AI Real-Time Logic - User: {client.user.username}")
    print(f"💰 Balance: ${real_balance}")
    print(f"💳 Real Clicks: {real_trans_ct} * 10 = Model Input: {adjusted_trans_ct}")
    print(f"💸 Real Trans Amt: ${real_trans_amt}")
    print("=" * 40 + "\n")

    # ============================================================
    # 3. Build Feature Vector
    # ============================================================
    gender_map = {'male': 'M', 'female': 'F'}
    csv_gender = gender_map.get(client.gender, 'M')

    feature_values = [
        client.age if client.age else 40,
        safe_encode('Gender', csv_gender),
        client.dependent_count if client.dependent_count else 0,
        safe_encode('Education_Level', client.education_level),
        safe_encode('Marital_Status', client.marital_status),
        safe_encode('Income_Category', client.income_level),

        simulated_credit_limit,  # Credit_Limit
        simulated_revolving_bal,  # Total_Revolving_Bal
        real_trans_amt,  # Total_Trans_Amt (Use actual amount)
        adjusted_trans_ct  # Total_Trans_Ct (Real clicks * 10)
    ]

    feature_names = [
        'Customer_Age', 'Gender', 'Dependent_count', 'Education_Level',
        'Marital_Status', 'Income_Category', 'Credit_Limit',
        'Total_Revolving_Bal', 'Total_Trans_Amt', 'Total_Trans_Ct'
    ]

    # 4. Predict
    try:
        df_features = pd.DataFrame([feature_values], columns=feature_names)
        churn_prob = model.predict_proba(df_features)[0][1]
        churn_prob = round(churn_prob, 2)
        print(f"🎲 Calculated Probability: {churn_prob * 100}%")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0.5, "Error"

    # 5. Risk Thresholds
    if churn_prob >= 0.7:
        risk = "high"
    elif churn_prob >= 0.4:
        risk = "medium"
    else:
        risk = "low"

    return churn_prob, risk