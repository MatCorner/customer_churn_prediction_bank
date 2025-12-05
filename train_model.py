import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# 1. Load Dataset
csv_path = 'BankChurners.csv'
if not os.path.exists(csv_path):
    raise FileNotFoundError("BankChurners.csv not found in root directory!")

df = pd.read_csv(csv_path)

# 2. Feature Selection (Must match Database Fields)
# Mapping CSV columns to our logical database fields
features = [
    'Attrition_Flag',       # Target
    'Customer_Age',         # Client.age
    'Gender',               # Client.gender
    'Dependent_count',      # Client.dependent_count
    'Education_Level',      # Client.education_level
    'Marital_Status',       # Client.marital_status
    'Income_Category',      # Client.income_level
    'Credit_Limit',         # CreditCard.credit_limit
    'Total_Revolving_Bal',  # CreditCard.balance (debt)
    'Total_Trans_Amt',      # CreditCard.total_trans_amount
    'Total_Trans_Ct'        # CreditCard.total_trans_count
]
df = df[features]

# 3. Preprocessing
# Convert Target: Attrited -> 1 (Churn), Existing -> 0 (Stay)
df['Target'] = df['Attrition_Flag'].apply(lambda x: 1 if 'Attrited' in x else 0)
df.drop('Attrition_Flag', axis=1, inplace=True)

# Encode Categorical Data
encoders = {}
cat_cols = ['Gender', 'Education_Level', 'Marital_Status', 'Income_Category']

print("--- Encoding Mappings ---")
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le
    print(f"{col}: {dict(zip(le.classes_, le.transform(le.classes_)))}")

# 4. Train Model
X = df.drop('Target', axis=1)
y = df['Target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\nTraining Random Forest Model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"Model Accuracy: {model.score(X_test, y_test):.2f}")

# 5. Save Model & Encoders
if not os.path.exists('churn_app'):
    os.makedirs('churn_app')

joblib.dump(model, 'churn_app/churn_model.pkl')
joblib.dump(encoders, 'churn_app/model_encoders.pkl')
print("\n✅ Model saved to churn_app/churn_model.pkl")