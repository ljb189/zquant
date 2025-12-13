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
数据同步策略工厂

根据task_action创建对应的同步策略
"""

from zquant.services.sync_strategies.base import DataSyncStrategy
from zquant.services.sync_strategies.stock_list_strategy import StockListSyncStrategy
from zquant.services.sync_strategies.trading_calendar_strategy import TradingCalendarSyncStrategy
from zquant.services.sync_strategies.daily_data_strategy import DailyDataSyncStrategy, AllDailyDataSyncStrategy
from zquant.services.sync_strategies.daily_basic_strategy import DailyBasicSyncStrategy


class SyncStrategyFactory:
    """数据同步策略工厂"""

    # 策略注册表
    _strategies: dict[str, type[DataSyncStrategy]] = {
        "sync_stock_list": StockListSyncStrategy,
        "sync_trading_calendar": TradingCalendarSyncStrategy,
        "sync_daily_data": DailyDataSyncStrategy,
        "sync_all_daily_data": AllDailyDataSyncStrategy,
        "sync_daily_basic_data": DailyBasicSyncStrategy,
    }

    @classmethod
    def create_strategy(cls, task_action: str) -> DataSyncStrategy:
        """
        创建同步策略

        Args:
            task_action: 任务动作（如：sync_stock_list, sync_daily_data等）

        Returns:
            数据同步策略实例

        Raises:
            ValueError: 如果task_action不支持
        """
        strategy_class = cls._strategies.get(task_action)
        if not strategy_class:
            raise ValueError(
                f"不支持的任务动作: {task_action}。"
                f"支持的 action: {', '.join(cls._strategies.keys())}"
            )
        return strategy_class()

    @classmethod
    def register_strategy(cls, task_action: str, strategy_class: type[DataSyncStrategy]):
        """
        注册新的同步策略

        Args:
            task_action: 任务动作
            strategy_class: 策略类
        """
        cls._strategies[task_action] = strategy_class

    @classmethod
    def get_supported_actions(cls) -> list[str]:
        """
        获取支持的任务动作列表

        Returns:
            支持的任务动作列表
        """
        return list(cls._strategies.keys())
