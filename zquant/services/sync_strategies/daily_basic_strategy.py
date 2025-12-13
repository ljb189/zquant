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
每日指标数据同步策略
"""

from typing import Any
from sqlalchemy.orm import Session

from zquant.data.etl.scheduler import DataScheduler
from zquant.services.sync_strategies.base import DataSyncStrategy


class DailyBasicSyncStrategy(DataSyncStrategy):
    """每日指标数据同步策略"""

    def __init__(self):
        self.data_scheduler = DataScheduler()

    def sync(self, db: Session, config: dict[str, Any], extra_info: dict | None = None) -> dict[str, Any]:
        """
        同步每日指标数据

        Args:
            db: 数据库会话
            config: 同步配置，可包含 start_date, end_date, codelist
            extra_info: 额外信息字典

        Returns:
            同步结果字典
        """
        start_date = config.get("start_date")
        end_date = config.get("end_date")
        codelist = config.get("codelist")

        # 处理 codelist：如果是字符串，转换为列表
        if isinstance(codelist, str):
            codelist = [code.strip() for code in codelist.split(",") if code.strip()]
        elif codelist is None:
            codelist = None

        result = self.data_scheduler.sync_daily_basic_data(db, start_date, end_date, extra_info, codelist)
        return {
            "success": True,
            "total": result.get("total", 0),
            "success_count": result.get("success", 0),
            "failed_count": len(result.get("failed", [])),
            "failed_symbols": result.get("failed", []),
            "message": f"同步完成: 成功 {result.get('success', 0)}/{result.get('total', 0)}"
        }

    def get_strategy_name(self) -> str:
        return "sync_daily_basic_data"
