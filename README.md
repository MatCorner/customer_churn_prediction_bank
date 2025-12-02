

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

