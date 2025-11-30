from django.db import models

from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('manager', 'Manager'),
    )
    # Link to built-in Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    age = models.IntegerField(null=True, blank=True)             # only for customers
    marital_status = models.CharField(max_length=20, blank=True) # only for customers
    balance = models.FloatField(default=0)                       # only for customers
    tenure = models.IntegerField(default=0)                      # only for customers

    # 顾客注册时间
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    action = models.CharField(max_length=50, choices=[
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.amount} ({self.action})"


# 1. 用户超类表（User）
class User(models.Model):
    user_id = models.BigAutoField(primary_key=True, verbose_name="用户唯一ID")
    username = models.CharField(max_length=50, unique=True, verbose_name="用户名（登录用）", help_text="登录用户名，唯一")
    password = models.CharField(max_length=100, verbose_name="密码（存储加密值）")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="账号创建时间")  # 创建时自动赋值
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")         # 更新时自动刷新

    class Meta:
        db_table = "User"  # 对应数据库中的User表（和你的SQL表名一致）
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return f"用户{self.user_id}：{self.username}"


# 2. 客户子类表（Client）
class Client(models.Model):
    # 流失状态枚举（对应SQL的ENUM）
    ATTRITION_CHOICES = [
        ('Existing Customer', '存续客户'),
        ('Attrited Customer', '流失客户'),
    ]
    # 教育程度枚举
    EDUCATION_CHOICES = [
        ('College', '大专'),
        ('Doctorate', '博士'),
        ('Graduate', '研究生'),
        ('High School', '高中'),
        ('Post-Graduate', '博士后'),
        ('Uneducated', '未受过教育'),
        ('Unknown', '未知'),
    ]
    # 婚姻状态枚举
    MARITAL_CHOICES = [
        ('Divorced', '离异'),
        ('Married', '已婚'),
        ('Single', '单身'),
        ('Unknown', '未知'),
    ]
    # 收入等级枚举
    INCOME_CHOICES = [
        ('$120K +', '12万美元以上'),
        ('$40K - $60K', '4-6万美元'),
        ('$60K - $80K', '6-8万美元'),
        ('$80K - $120K', '8-12万美元'),
        ('Less than $40K', '低于4万美元'),
        ('Unknown', '未知'),
    ]

    client_id = models.BigAutoField(primary_key=True, verbose_name="客户唯一ID")
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        db_column="user_id",  # 对应数据库字段名user_id
        related_name="client",
        verbose_name="关联用户ID"
    )
    attrition_flag = models.CharField(
        max_length=20, 
        choices=ATTRITION_CHOICES, 
        default='Existing Customer', 
        verbose_name="流失状态"
    )
    age = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="年龄")  # TINYINT UNSIGNED → PositiveSmallIntegerField
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', '男'), ('Female', '女')], 
        verbose_name="性别"
    )
    dependent_count = models.PositiveSmallIntegerField(default=0, null=True, blank=True, verbose_name="赡养人数")
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='Unknown', verbose_name="教育程度")
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, default='Unknown', verbose_name="婚姻状态")
    income_level = models.CharField(max_length=20, choices=INCOME_CHOICES, default='Unknown', verbose_name="收入等级")

    class Meta:
        db_table = "Client"  # 对应数据库Client表
        verbose_name = "客户"
        verbose_name_plural = "客户"
        unique_together = [["user"]]  # 对应SQL的uk_client_userid（user_id唯一）

    def __str__(self):
        return f"客户{self.client_id}（{self.attrition_flag}）"


# 3. 员工子类表（Staff）
class Staff(models.Model):
    POSITION_CHOICES = [
        ('Teller', '柜员'),
        ('Manager', '经理'),
        ('Supervisor', '主管'),
        ('Branch Director', '行长'),
    ]

    staff_id = models.BigAutoField(primary_key=True, verbose_name="员工唯一ID")
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        db_column="user_id",
        related_name="staff",
        verbose_name="关联用户ID"
    )
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default='Manager', verbose_name="职位")

    class Meta:
        db_table = "Staff"  # 对应数据库Staff表
        verbose_name = "员工"
        verbose_name_plural = "员工"
        unique_together = [["user"]]  # 对应SQL的uk_staff_userid

    def __str__(self):
        return f"员工{self.staff_id}：{self.position}"


# 4. 账户超类表（Account）
class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('Debit Card', '借记卡'),
        ('Credit Card', '信用卡'),
    ]

    account_id = models.BigAutoField(primary_key=True, verbose_name="账户唯一ID")
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        db_column="user_id",
        related_name="accounts",
        verbose_name="关联用户ID"
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, verbose_name="账户类型")
    open_date = models.DateField(verbose_name="开户日期")
    status = models.SmallIntegerField(default=1, verbose_name="状态", help_text="0=冻结/1=正常/2=销户")
    last_trans_time = models.DateTimeField(null=True, blank=True, verbose_name="最后交易时间")

    class Meta:
        db_table = "Account"  # 对应数据库Account表
        verbose_name = "账户"
        verbose_name_plural = "账户"

    def __str__(self):
        return f"账户{self.account_id}（{self.account_type}）"


# 5. 借记卡子类表（Debit_Card）
class DebitCard(models.Model):  # Django类名建议驼峰，表名仍为Debit_Card
    debit_id = models.BigAutoField(primary_key=True, verbose_name="借记卡唯一ID")
    account = models.OneToOneField(
        Account, 
        on_delete=models.CASCADE, 
        db_column="account_id",
        related_name="debit_card",
        verbose_name="关联账户ID"
    )
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, verbose_name="账户余额")
    card_no = models.CharField(max_length=16, unique=True, verbose_name="16位卡号")
    expire_date = models.DateField(verbose_name="卡片有效期")
    daily_limit = models.DecimalField(max_digits=18, decimal_places=2, default=5000.00, verbose_name="单日取款限额")
    total_trans_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="总交易金额")
    total_trans_count = models.PositiveIntegerField(default=0, verbose_name="总交易次数")
    avg_trans_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="平均单笔金额")
    monthly_avg_consume = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="月均消费")
    trans_active_month = models.PositiveSmallIntegerField(default=0, verbose_name="近12个月活跃月份")

    class Meta:
        db_table = "Debit_Card"  # 对应数据库Debit_Card表
        verbose_name = "借记卡"
        verbose_name_plural = "借记卡"

    def __str__(self):
        return f"借记卡{self.debit_id}：{self.card_no}"


# 6. 信用卡子类表（Credit_Card）
class CreditCard(models.Model):  # Django类名驼峰，表名Credit_Card
    credit_id = models.BigAutoField(primary_key=True, verbose_name="信用卡唯一ID")
    account = models.OneToOneField(
        Account, 
        on_delete=models.CASCADE, 
        db_column="account_id",
        related_name="credit_card",
        verbose_name="关联账户ID"
    )
    card_no = models.CharField(max_length=16, unique=True, verbose_name="16位卡号")
    expire_date = models.DateField(verbose_name="卡片有效期")
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="信用额度")
    available_limit = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="可用额度")
    total_trans_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="总消费金额")
    total_trans_count = models.PositiveIntegerField(default=0, verbose_name="总消费次数")
    avg_trans_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="平均单笔消费")
    monthly_avg_consume = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="月均消费")
    trans_active_month = models.PositiveSmallIntegerField(default=0, verbose_name="近12个月活跃月份")
    install_count = models.PositiveIntegerField(default=0, verbose_name="累计分期次数")
    install_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="累计分期金额")
    overdue_count = models.PositiveSmallIntegerField(default=0, verbose_name="累计逾期次数")
    max_overdue_days = models.PositiveSmallIntegerField(default=0, verbose_name="最长逾期天数")
    min_pay_count = models.PositiveIntegerField(default=0, verbose_name="累计最低还款次数")
    total_interest_fee = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, verbose_name="累计利息+手续费")
    credit_utilization = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="平均额度使用率（%）")

    class Meta:
        db_table = "Credit_Card"  # 对应数据库Credit_Card表
        verbose_name = "信用卡"
        verbose_name_plural = "信用卡"

    def __str__(self):
        return f"信用卡{self.credit_id}：{self.card_no}"
