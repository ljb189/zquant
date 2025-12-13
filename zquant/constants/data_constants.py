# Copyright 2025 ZQuant Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: kevin
# Contact:
#     - Email: kevin@vip.qq.com
#     - Wechat: zquant2025
#     - Issues: https://github.com/yoyoung/zquant/issues
#     - Documentation: https://github.com/yoyoung/zquant/blob/main/README.md
#     - Repository: https://github.com/yoyoung/zquant

"""
数据相关常量
"""

from datetime import date

# 视图名称（从models.data导入，保持兼容）
from zquant.models.data import (
    TUSTOCK_DAILY_VIEW_NAME,
    TUSTOCK_DAILY_BASIC_VIEW_NAME,
    TUSTOCK_FACTOR_VIEW_NAME,
    TUSTOCK_STKFACTORPRO_VIEW_NAME,
)

# 默认日期
DEFAULT_START_DATE = date(2025, 1, 1)

# 表名前缀
DATA_TABLE_PREFIX = "zq_data_"
DAILY_TABLE_PREFIX = "zq_data_tustock_daily_"
DAILY_BASIC_TABLE_PREFIX = "zq_data_tustock_daily_basic_"

# 交易所代码
EXCHANGE_SSE = "SSE"  # 上海证券交易所
EXCHANGE_SZSE = "SZSE"  # 深圳证券交易所
EXCHANGE_BJ = "BJ"  # 北京证券交易所

# 数据同步相关
DEFAULT_SYNC_BATCH_SIZE = 1000  # 默认批量同步大小
