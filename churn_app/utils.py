import random

def predict_churn_dummy(client):
    """
    Dummy prediction logic (placeholder).
    Replace with actual ML model later.
    """
    # 模拟一个流失概率 0~1
    churn_score = round(random.uniform(0, 1), 2)

    # 风险等级
    if churn_score > 0.7:
        risk = "high"
    elif churn_score > 0.4:
        risk = "medium"
    else:
        risk = "low"

    return churn_score, risk
