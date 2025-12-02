

| 模块          | API 功能      | Method | URL                              |
| ----------- | ----------- | ------ | -------------------------------- |
| Auth        | 注册          | POST   | /api/register/                   |
| Auth        | 登录 (JWT)    | POST   | /api/login/                      |
| Profile     | 查看自己资料      | GET    | /api/profile/me/                 |
| Profile     | 更新资料        | PUT    | /api/profile/me/                 |
| Account     | 创建账户        | POST   | /api/accounts/                   |
| Account     | 查看我的所有账户    | GET    | /api/accounts/                   |
| Account     | 查看某个账户详情    | GET    | /api/accounts/<id>/              |
| Transaction | 存款          | POST   | /api/transactions/deposit/       |
| Transaction | 取款          | POST   | /api/transactions/withdraw/      |
| Transaction | 转账          | POST   | /api/transactions/transfer/      |
| Transaction | 查看账户交易历史    | GET    | /api/accounts/<id>/transactions/ |
| Loan        | 申请贷款        | POST   | /api/loans/                      |
| Loan        | 查看我的贷款      | GET    | /api/loans/                      |
| Behavior    | 查看行为日志（管理员） | GET    | /api/behavior/                   |

Register:
URLS: POST http://127.0.0.1:8000/api/register/
HEADERS: Content-Type: application/json
Body (Raw Json): {
  "username": "customer1",
  "password": "123456",
  "role": "customer",
  "age": 30,
  "marital_status": "Single",
  "balance": 1000,
  "tenure": 12
}

Login:
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json
{
  "username": "customer1",
  "password": "123456"
}
{
  "refresh": "...",
  "access": "..."   <-- 用这个 access token 调用后续 API
}

调用受保护 API（带 Token）
例如查看所有用户（仅员工可访问）
GET http://127.0.0.1:8000/api/list_users/
Headers: Authorization: Bearer <access_token>
返回示例: [
  {
    "id": 1,
    "username": "customer1",
    "role": "customer",
    "age": 30,
    "marital_status": "Single",
    "balance": 1000,
    "tenure": 12,
    "churn_score": 0.72,
    "churn_risk": "high"
  },
  {
    "id": 2,
    "username": "customer2",
    "role": "customer",
    "age": 25,
    "marital_status": "Married",
    "balance": 500,
    "tenure": 6,
    "churn_score": 0.35,
    "churn_risk": "low"
  }
]

创建交易（POST）(Client)
POST http://127.0.0.1:8000/api/transactions/
Authorization: Bearer <access_token>
Content-Type: application/json
{
  "action": "transfer",
  "amount": 100,
  "recipient_id": 2
}
返回示例:
{
  "message": "Transaction completed successfully"
}

查看单个用户信息（GET）User
GET http://127.0.0.1:8000/api/my_profile/1/
Authorization: Bearer <access_token>
{
  "id": 1,
  "username": "customer1",
  "role": "customer",
  "age": 30,
  "marital_status": "Single",
  "balance": 900,
  "tenure": 12,
  "churn_score": 0.72,
  "churn_risk": "high"
}

