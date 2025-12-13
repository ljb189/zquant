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
Repository层

统一数据访问接口，提供缓存和批量查询优化
"""

from zquant.repositories.trading_date_repository import TradingDateRepository
from zquant.repositories.stock_repository import StockRepository
from zquant.repositories.price_data_repository import PriceDataRepository
from zquant.repositories.factor_repository import FactorRepository

__all__ = [
    "TradingDateRepository",
    "StockRepository",
    "PriceDataRepository",
    "FactorRepository",
]
