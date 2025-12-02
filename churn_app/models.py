from django.db import models
from django.utils import timezone

# -------------------------- 1. User 表（用户超类）--------------------------
class User(models.Model):
    user_id = models.BigAutoField(primary_key=True, verbose_name="用户唯一ID")
    username = models.CharField(max_length=50, unique=True, null=False, verbose_name="用户名（登录用）")
    password = models.CharField(max_length=100, null=False, verbose_name="密码")
    create_time = models.DateTimeField(
        null=False, 
        default=timezone.now, 
        verbose_name="账号创建时间"
    )
    update_time = models.DateTimeField(
        null=False, 
        auto_now=True, 
        verbose_name="账号更新时间"
    )

    class Meta:
        db_table = "User"  # 对应数据库表名
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username

# -------------------------- 2. Client 表（客户子类，关联User）--------------------------
class Client(models.Model):
    client_id = models.BigAutoField(primary_key=True, verbose_name="客户唯一ID")
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        to_field="user_id", 
        unique=True, 
        null=False, 
        verbose_name="关联用户"
    )
    warning = models.PositiveSmallIntegerField(
        null=False, 
        default=0, 
        choices=[(0, "正常"), (1, "流失预警")], 
        verbose_name="流失预警"
    )
    age = models.PositiveTinyIntegerField(
        null=True, 
        blank=True, 
        verbose_name="年龄"
    )  # UNSIGNED 对应 PositiveTinyIntegerField（0-127，满足0-120需求）
    gender = models.CharField(
        max_length=6, 
        null=False, 
        choices=[("male", "男性"), ("female", "女性")], 
        verbose_name="性别"
    )
    dependent_count = models.PositiveTinyIntegerField(
        null=True, 
        blank=True, 
        default=0, 
        verbose_name="赡养人数"
    )
    education_level = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        default="Unknown", 
        choices=[
            ("College", "大学"),
            ("Doctorate", "博士"),
            ("Graduate", "研究生"),
            ("High School", "高中"),
            ("Post-Graduate", "博士后"),
            ("Uneducated", "未受教育"),
            ("Unknown", "未知")
        ], 
        verbose_name="教育程度"
    )
    marital_status = models.CharField(
        max_length=10, 
        null=True, 
        blank=True, 
        default="Unknown", 
        choices=[
            ("Divorced", "离异"),
            ("Married", "已婚"),
            ("Single", "单身"),
            ("Unknown", "未知")
        ], 
        verbose_name="婚姻状态"
    )
    income_level = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        default="Unknown", 
        choices=[
            ("$120K +", "12万美元以上"),
            ("$40K - $60K", "4-6万美元"),
            ("$60K - $80K", "6-8万美元"),
            ("$80K - $120K", "8-12万美元"),
            ("Less than $40K", "4万美元以下"),
            ("Unknown", "未知")
        ], 
        verbose_name="收入等级"
    )

    class Meta:
        db_table = "Client"
        verbose_name = "客户"
        verbose_name_plural = "客户"

    def __str__(self):
        return f"客户{self.client_id}（{self.user.username}）"

# -------------------------- 3. Staff 表（员工子类，关联User）--------------------------
class Staff(models.Model):
    staff_id = models.BigAutoField(primary_key=True, verbose_name="员工唯一ID")
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        to_field="user_id", 
        null=False, 
        verbose_name="关联用户"
    )
    position = models.CharField(
        max_length=50, 
        null=False, 
        default="manager", 
        verbose_name="职位"
    )

    class Meta:
        db_table = "Staff"
        verbose_name = "员工"
        verbose_name_plural = "员工"

    def __str__(self):
        return f"员工{self.staff_id}（{self.user.username}）"

# -------------------------- 4. DebitCard 表（借记卡）--------------------------
class DebitCard(models.Model):
    debit_id = models.BigAutoField(primary_key=True, verbose_name="借记卡唯一ID")
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        to_field="user_id", 
        null=False, 
        verbose_name="关联用户"
    )
    card_no = models.CharField(
        max_length=16, 
        unique=True, 
        null=False, 
        verbose_name="借记卡卡号"
    )
    balance = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        null=False, 
        default=0.00, 
        verbose_name="账户余额"
    )
    expire_date = models.DateField(null=False, verbose_name="卡片有效期")
    daily_limit = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        null=False, 
        default=5000.00, 
        verbose_name="单日取款限额"
    )
    debit_card_level = models.CharField(
        max_length=10, 
        null=False, 
        default="Bronze", 
        choices=[
            ("Bronze", "青铜"),
            ("Silver", "白银"),
            ("Gold", "黄金"),
            ("Platinum", "铂金"),
            ("Diamond", "钻石")
        ], 
        verbose_name="储蓄卡等级"
    )

    class Meta:
        db_table = "Debit_Card"
        verbose_name = "借记卡"
        verbose_name_plural = "借记卡"

    def __str__(self):
        return f"借记卡{self.card_no}（{self.user.username}）"

# -------------------------- 5. CreditCard 表（信用卡）--------------------------
class CreditCard(models.Model):
    credit_id = models.BigAutoField(primary_key=True, verbose_name="信用卡唯一ID")
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        to_field="user_id", 
        null=False, 
        verbose_name="关联用户"
    )
    card_no = models.CharField(
        max_length=16, 
        unique=True, 
        null=False, 
        verbose_name="信用卡卡号"
    )
    expire_date = models.DateField(null=False, verbose_name="卡片有效期")
    credit_limit = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        null=False, 
        verbose_name="信用额度"
    )
    available_limit = models.DecimalField(
        max_digits=18, 
        decimal_places=2, 
        null=False, 
        verbose_name="可用额度"
    )
    credit_card_level = models.CharField(
        max_length=10, 
        null=False, 
        default="Bronze", 
        choices=[
            ("Bronze", "青铜"),
            ("Silver", "白银"),
            ("Gold", "黄金"),
            ("Platinum", "铂金"),
            ("Diamond", "钻石")
        ], 
        verbose_name="信用卡等级"
    )

    class Meta:
        db_table = "Credit_Card"
        verbose_name = "信用卡"
        verbose_name_plural = "信用卡"

    def __str__(self):
        return f"信用卡{self.card_no}（{self.user.username}）"

# -------------------------- 6. Transaction 表（交易记录）--------------------------
class Transaction(models.Model):
    transaction_id = models.BigAutoField(primary_key=True, verbose_name="交易唯一ID")
    subject_card_no = models.CharField(
        max_length=16, 
        null=False, 
        verbose_name="交易主体卡号"
    )
    target_card_no = models.CharField(
        max_length=16, 
        null=True, 
        blank=True, 
        verbose_name="目标方卡号"
    )  # 存款/取款时为空
    transaction_type = models.CharField(
        max_length=10, 
        null=False, 
        choices=[
            ("remit", "汇款"),
            ("receive", "收款"),
            ("withdraw", "取款"),
            ("deposit", "存款")
        ], 
        verbose_name="交易类型"
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=False, 
        default=0.00, 
        verbose_name="交易金额"
    )
    create_time = models.DateTimeField(
        null=False, 
        auto_now_add=True, 
        verbose_name="交易创建时间"
    )
    end_time = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="交易结束时间"
    )
    status = models.CharField(
        max_length=10, 
        null=False, 
        choices=[
            ("success", "成功"),
            ("failed", "失败"),
            ("cancelled", "取消")
        ], 
        verbose_name="交易状态"
    )

    class Meta:
        db_table = "Transaction"
        verbose_name = "交易记录"
        verbose_name_plural = "交易记录"

    def __str__(self):
        return f"交易{self.transaction_id}（{self.get_transaction_type_display()}）"
