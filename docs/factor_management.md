# 因子管理功能文档

## 概述

因子管理系统提供了完整的量化因子加工通用方案和流程，包括因子定义、因子模型、因子配置的管理，以及因子计算的定时任务调度。

## 功能特性

- ✅ **因子定义管理**：定义因子的基本信息（因子名、中文简称、英文简称、列名、描述）
- ✅ **因子模型管理**：为每个因子配置不同的计算算法/模型，支持多个算法，可设置默认算法
- ✅ **因子配置管理**：为特定股票代码配置因子模型，支持批量配置
- ✅ **因子计算**：通过定时任务调度，按配置规则自动计算因子
- ✅ **数据检查**：计算前自动检查当日数据是否已同步
- ✅ **结果存储**：计算结果按股票代码分表存储（`zq_quant_factor_spacex_{code}`）
- ✅ **结果查询**：支持查询因子计算结果

## 数据库表结构

### 1. 因子定义表 (`zq_quant_factor_definitions`)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键ID |
| factor_name | VARCHAR(100) | 因子名称（唯一标识） |
| cn_name | VARCHAR(100) | 中文简称 |
| en_name | VARCHAR(100) | 英文简称 |
| column_name | VARCHAR(100) | 因子表数据列名 |
| description | TEXT | 因子详细描述 |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 2. 因子模型表 (`zq_quant_factor_models`)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键ID |
| factor_id | INTEGER | 因子ID（外键） |
| model_name | VARCHAR(100) | 模型名称 |
| model_code | VARCHAR(50) | 模型代码（用于识别计算器类型） |
| config_json | TEXT | 模型配置（JSON格式） |
| is_default | BOOLEAN | 是否默认算法 |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 3. 因子配置表 (`zq_quant_factor_configs`)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键ID |
| factor_id | INTEGER | 因子ID（外键） |
| model_id | INTEGER | 模型ID（外键，NULL表示使用默认算法） |
| codes | TEXT | 股票代码列表（逗号分隔，NULL表示所有股票） |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4. 因子结果表 (`zq_quant_factor_spacex_{code}`)

按股票代码分表存储，例如：`zq_quant_factor_spacex_000001`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键ID |
| trade_date | DATE | 交易日期 |
| {column_name} | FLOAT | 因子值（列名由因子定义中的column_name决定） |
| created_at | DATETIME | 创建时间 |

## API接口文档

### 因子定义管理

#### 创建因子定义
```
POST /api/v1/factor/definitions
```

请求体：
```json
{
  "factor_name": "turnover_rate",
  "cn_name": "换手率",
  "en_name": "Turnover Rate",
  "column_name": "turnover_rate",
  "description": "换手率因子，反映股票交易的活跃程度",
  "enabled": true
}
```

#### 获取因子定义列表
```
GET /api/v1/factor/definitions?skip=0&limit=20&enabled=true&order_by=id&order=desc
```

#### 获取因子定义详情
```
GET /api/v1/factor/definitions/{id}
```

#### 更新因子定义
```
PUT /api/v1/factor/definitions/{id}
```

#### 删除因子定义
```
DELETE /api/v1/factor/definitions/{id}
```

### 因子模型管理

#### 创建因子模型
```
POST /api/v1/factor/models
```

请求体：
```json
{
  "factor_id": 1,
  "model_name": "换手率计算模型（每日指标）",
  "model_code": "turnover_rate",
  "config_json": {
    "source": "daily_basic",
    "field": "turnover_rate"
  },
  "is_default": true,
  "enabled": true
}
```

#### 获取因子模型列表
```
GET /api/v1/factor/models?factor_id=1&skip=0&limit=20
```

#### 获取因子模型详情
```
GET /api/v1/factor/models/{id}
```

#### 更新因子模型
```
PUT /api/v1/factor/models/{id}
```

#### 删除因子模型
```
DELETE /api/v1/factor/models/{id}
```

### 因子配置管理

#### 创建因子配置
```
POST /api/v1/factor/configs
```

请求体：
```json
{
  "factor_id": 1,
  "model_id": null,
  "codes": ["000001.SZ", "000002.SZ"],
  "enabled": true
}
```

#### 获取因子配置列表
```
GET /api/v1/factor/configs?factor_id=1&skip=0&limit=20
```

#### 获取因子配置详情
```
GET /api/v1/factor/configs/{id}
```

#### 更新因子配置
```
PUT /api/v1/factor/configs/{id}
```

#### 删除因子配置
```
DELETE /api/v1/factor/configs/{id}
```

### 因子计算

#### 手动触发因子计算
```
POST /api/v1/factor/calculate
```

请求体（单日计算，使用今日）：
```json
{
  "factor_id": 1,
  "codes": ["000001.SZ"]
}
```

请求体（日期范围计算）：
```json
{
  "factor_id": 1,
  "codes": ["000001.SZ"],
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

### 因子结果查询

#### 查询因子计算结果
```
POST /api/v1/factor/results
```

请求体：
```json
{
  "code": "000001.SZ",
  "factor_name": "turnover_rate",
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

## 因子计算流程

### 1. 数据检查

因子计算前会自动检查：
- 当日数据是否已同步
- 是否为交易日

### 2. 获取计算配置

根据因子配置表获取需要计算的股票代码列表和对应的模型：
- 如果配置中指定了codes，使用指定的codes
- 如果配置中codes为空，计算所有股票
- 如果配置中指定了model_id，使用指定的模型
- 如果配置中model_id为NULL，使用默认模型

### 3. 因子计算

调用对应的因子计算器进行计算：
- 根据model_code创建计算器实例
- 传入配置参数
- 执行计算逻辑

### 4. 结果存储

将计算结果存储到对应的分表中：
- 表名格式：`zq_quant_factor_spacex_{code}`
- 如果记录已存在，更新；否则插入新记录

## 因子计算器开发

### 基础计算器类

所有因子计算器需要继承 `BaseFactorCalculator` 类：

```python
from zquant.factor.calculators.base import BaseFactorCalculator

class MyFactorCalculator(BaseFactorCalculator):
    MODEL_CODE = "my_factor"
    
    def __init__(self, config: dict | None = None):
        super().__init__(self.MODEL_CODE, config)
    
    def calculate(self, db: Session, code: str, trade_date: date) -> float | None:
        # 实现计算逻辑
        pass
    
    def validate_config(self) -> tuple[bool, str]:
        # 验证配置
        return True, ""
```

### 注册计算器

在 `zquant/factor/calculators/factory.py` 中注册：

```python
from zquant.factor.calculators.factory import register_calculator
from zquant.factor.calculators.my_factor import MyFactorCalculator

register_calculator(MyFactorCalculator.MODEL_CODE, MyFactorCalculator)
```

## 定时任务配置

### 创建因子计算定时任务

通过定时任务系统创建因子计算任务：

**单日计算（使用今日）：**
```json
{
  "name": "因子计算任务",
  "task_type": "common_task",
  "cron_expression": "0 18 * * *",
  "description": "每日18:00执行因子计算",
  "config": {
    "task_action": "calculate_factor",
    "factor_id": null,
    "codes": null
  },
  "enabled": true
}
```

**日期范围计算：**
```json
{
  "name": "因子计算任务（日期范围）",
  "task_type": "common_task",
  "description": "计算指定日期范围内的因子",
  "config": {
    "task_action": "calculate_factor",
    "factor_id": null,
    "codes": null,
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "enabled": false
}
```

配置说明：
- `task_action`: 必须为 `"calculate_factor"`
- `factor_id`: 因子ID（可选，NULL表示计算所有启用的因子）
- `codes`: 股票代码列表（可选，NULL表示使用配置中的codes）
- `start_date`: 开始日期（可选，ISO格式字符串，如 "2025-01-01"，与end_date一起使用表示日期范围；都不提供则使用今日）
- `end_date`: 结束日期（可选，ISO格式字符串，如 "2025-01-31"，与start_date一起使用表示日期范围；都不提供则使用今日）

## 初始化脚本

### 运行初始化脚本

```bash
# 创建表并初始化示例数据
python zquant/scripts/init_factor.py

# 只创建表
python zquant/scripts/init_factor.py --tables-only

# 强制重新创建（删除已存在的记录）
python zquant/scripts/init_factor.py --force
```

### 初始化内容

1. 创建因子相关表（因子定义表、因子模型表、因子配置表）
2. 创建换手率因子定义和模型
3. 创建示例因子配置

## 使用示例

### 1. 创建因子定义

```python
from zquant.services.factor import FactorService

factor_def = FactorService.create_factor_definition(
    db=db,
    factor_name="turnover_rate",
    cn_name="换手率",
    en_name="Turnover Rate",
    column_name="turnover_rate",
    description="换手率因子",
    enabled=True
)
```

### 2. 创建因子模型

```python
model = FactorService.create_factor_model(
    db=db,
    factor_id=factor_def.id,
    model_name="换手率计算模型",
    model_code="turnover_rate",
    config_json={"source": "daily_basic", "field": "turnover_rate"},
    is_default=True,
    enabled=True
)
```

### 3. 创建因子配置

```python
config = FactorService.create_factor_config(
    db=db,
    factor_id=factor_def.id,
    model_id=None,  # 使用默认模型
    codes=["000001.SZ", "000002.SZ"],  # 指定股票代码
    enabled=True
)
```

### 4. 执行因子计算

```python
from zquant.services.factor_calculation import FactorCalculationService

# 单日计算（使用今日）
result = FactorCalculationService.calculate_factor(
    db=db,
    factor_id=1,
    codes=["000001.SZ"]
)

# 日期范围计算
result = FactorCalculationService.calculate_factor(
    db=db,
    factor_id=1,
    codes=["000001.SZ"],
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31)
)
```

### 5. 查询因子结果

```python
results = FactorCalculationService.get_factor_results(
    db=db,
    code="000001.SZ",
    factor_name="turnover_rate",
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31)
)
```

## 注意事项

1. **数据同步**：因子计算前需要确保当日数据已同步
2. **交易日检查**：系统会自动检查是否为交易日
3. **表名规范**：因子结果表按code分表，表名格式为 `zq_quant_factor_spacex_{code}`
4. **配置优先级**：因子配置中的codes和model_id优先级高于默认值
5. **计算器注册**：新增因子计算器需要在factory中注册才能使用

## 常见问题

### Q: 如何添加新的因子计算器？

A: 
1. 创建计算器类，继承 `BaseFactorCalculator`
2. 实现 `calculate` 和 `validate_config` 方法
3. 在 `factory.py` 中注册计算器

### Q: 因子计算结果存储在哪里？

A: 按股票代码分表存储，表名格式为 `zq_quant_factor_spacex_{code}`，例如 `zq_quant_factor_spacex_000001`

### Q: 如何配置定时任务自动计算因子？

A: 在定时任务系统中创建任务，设置 `task_action` 为 `"calculate_factor"`，配置Cron表达式即可

### Q: 因子计算失败怎么办？

A: 检查：
1. 当日数据是否已同步
2. 是否为交易日
3. 因子配置是否正确
4. 计算器配置是否有效

