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
数据同步策略模块

使用Strategy模式统一数据同步逻辑
"""

from zquant.services.sync_strategies.base import DataSyncStrategy
from zquant.services.sync_strategies.stock_list_strategy import StockListSyncStrategy
from zquant.services.sync_strategies.trading_calendar_strategy import TradingCalendarSyncStrategy
from zquant.services.sync_strategies.daily_data_strategy import DailyDataSyncStrategy, AllDailyDataSyncStrategy
from zquant.services.sync_strategies.daily_basic_strategy import DailyBasicSyncStrategy
from zquant.services.sync_strategies.factory import SyncStrategyFactory

__all__ = [
    "DataSyncStrategy",
    "StockListSyncStrategy",
    "TradingCalendarSyncStrategy",
    "DailyDataSyncStrategy",
    "AllDailyDataSyncStrategy",
    "DailyBasicSyncStrategy",
    "SyncStrategyFactory",
]
