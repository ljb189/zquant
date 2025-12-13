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
股票列表同步策略
"""

from typing import Any
from sqlalchemy.orm import Session

from zquant.data.etl.scheduler import DataScheduler
from zquant.services.sync_strategies.base import DataSyncStrategy


class StockListSyncStrategy(DataSyncStrategy):
    """股票列表同步策略"""

    def __init__(self):
        self.data_scheduler = DataScheduler()

    def sync(self, db: Session, config: dict[str, Any], extra_info: dict | None = None) -> dict[str, Any]:
        """
        同步股票列表

        Args:
            db: 数据库会话
            config: 同步配置（此策略不需要额外配置）
            extra_info: 额外信息字典

        Returns:
            同步结果字典
        """
        count = self.data_scheduler.sync_stock_list(db, extra_info)
        return {
            "success": True,
            "count": count,
            "message": f"成功同步 {count} 条股票列表"
        }

    def get_strategy_name(self) -> str:
        return "sync_stock_list"
