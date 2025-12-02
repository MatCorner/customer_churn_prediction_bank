# User 表（用户超类：存储公共属性）

|字段名|数据类型|用途说明|约束 / 备注|
|:----|:----|:----|:----|
|user_id|BIGINT|用户唯一 ID（主键）|自增（AUTO_INCREMENT），非空|
|username|VARCHAR(50)|用户名（登录用）|唯一（UNIQUE），非空|
|password|VARCHAR(100)|密码|非空|
|create_time|DATETIME|账号创建时间|非空，默认当前时间（CURRENT_TIMESTAMP）|
|update_time|DATETIME|账号更新时间|非空，默认当前时间，更新时自动刷新|


# Client 表（客户子类：User 的子类，存储特有属性）

|字段名|数据类型|用途说明|约束 / 备注|
|:----|:----|:----|:----|
|client_id|BIGINT|客户唯一 ID（主键）|自增（AUTO_INCREMENT），非空|
|user_id|BIGINT|关联 User 表的主键（外键）|非空，关联 User (user_id)，级联删除（ON DELETE CASCADE），唯一（一个 User 对应一个 Client）|
|warning|ENUM (0,1)|流失预警|非空，默认0，1则表示可能流失|
|age|TINYINT UNSIGNED|年龄|可空，范围 0-120（UNSIGNED 避免负数）；|
|gender|ENUM (' male ',' female ')|性别|非空|
|dependent_count|TINYINT UNSIGNED|赡养人数|可空，默认 0（范围 0-5，满足绝大多数家庭场景）|
|education_level|ENUM('College','Doctorate','Graduate','High School','Post-Graduate','Uneducated','Unknown')|教育程度|可空，默认'Unknown'|
|marital_status|ENUM('Divorced','Married','Single','Unknown')|婚姻状态|可空，默认'Unknown'|
|income_level|ENUM ('$120K +','$40K - $60K','$60K - $80K','$80K - $120K','Less than $40K','Unknown')|收入等级|可空，默认'Unknown'|


# Staff 表（员工子类：User 的子类，存储特有属性）

|字段名|数据类型|用途说明|约束 / 备注|
|:----|:----|:----|:----|
|staff_id|BIGINT|员工唯一 ID（主键）|自增，非空|
|user_id|BIGINT|关联 User 表的主键（外键）|非空，关联 User (user_id)，级联删除|
|position|VARCHAR(50)|职位|非空，默认为'manager'|


# Debit Card 表

|字段名|数据类型|用途说明|约束 / 备注|
|:----|:----|:----|:----|
|debit_id|BIGINT|借记卡唯一 ID（主键）|自增，非空|
|user_id|BIGINT|关联 User 表的主键|非空，关联 User (user_id)，级联删除|
|card_no|VARCHAR(16)|借记卡卡号（16 位）|唯一（UNIQUE），有自己的命名逻辑，不能与信用卡号重复，非空|
|balance|DECIMAL(18,2)|账户余额|非空，默认 0.00（禁止负数，需业务层控制）|
|expire_date|DATE|卡片有效期（如 2030-12）|非空|
|daily_limit|DECIMAL(18,2)|单日取款限额|非空，默认 5000.00|
|debit_card_level|ENUM('Bronze','Silver','Gold','Platinum','Diamond')|储蓄卡等级|非空，默认'Bronze'|


# Credit Card 表

|字段名|数据类型|用途说明|约束 / 备注|
|:----|:----|:----|:----|
|credit_id|BIGINT|信用卡唯一 ID（主键）|自增，非空|
|user_id|BIGINT|关联 User 表的主键|非空，关联 User (user_id)，级联删除|
|card_no|VARCHAR(16)|信用卡卡号（16 位）|唯一（UNIQUE），有自己的命名逻辑，不能与借记卡号重复，非空|
|expire_date|DATE|卡片有效期|非空|
|credit_limit|DECIMAL(18,2)|信用额度|非空（如 50000.00）|
|available_limit|DECIMAL(18,2)|可用额度|非空，默认等于 credit_limit|
|credit_card_level|ENUM('Bronze','Silver','Gold','Platinum','Diamond')|储蓄卡等级|非空，默认'Bronze'|


# Transaction表

|字段名|数据类型（|用途说明|约束 / 备注|
|:----|:----|:----|:----|
|transaction_id|BIGINT（自增）|交易记录的唯一标识（主键）|主键约束，自动递增，不可为空|
|subject_card_no|VARCHAR(16)|交易主体的银行卡号|非空|
|target_card_no|VARCHAR(16)|交易的目标方卡号|如果交易类型为存款和取款，则为NULL，否则必须写上相应的对手方卡号|
|transaction_type|VARCHAR(10)|交易类型('remit', '汇款'), ('receive', '收款'), ('withdraw', '取款'), ('deposit', '存款')|枚举约束（仅允许指定值）；最大长度 10 字符；不可为空|
|amount|DECIMAL(12,2)|交易金额|精度约束（12 位数字，2 位小数）；建议设置默认值0.0，不可为空|
|create_time|DATETIME|交易创建的时间|自动记录创建时间（插入时填充）；不可为空|
|end_time|DATETIME|交易结束的时间|可为空（处理中的交易无结束时间）；交易状态变更为成功 / 失败时更新|
|status|VARCHAR(10)|交易状态（'success' 成功、'failed' 失败、'cancelled' 取消）|枚举约束（仅允许指定值）；最大长度 10 字符；不可为空；默认值null|


