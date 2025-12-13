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
日线数据同步策略
"""

from typing import Any
from loguru import logger
from sqlalchemy.orm import Session

from zquant.data.etl.scheduler import DataScheduler
from zquant.services.sync_strategies.base import DataSyncStrategy
from zquant.repositories.trading_date_repository import TradingDateRepository


class DailyDataSyncStrategy(DataSyncStrategy):
    """日线数据同步策略（单只股票）"""

    def __init__(self):
        self.data_scheduler = DataScheduler()

    def sync(self, db: Session, config: dict[str, Any], extra_info: dict | None = None) -> dict[str, Any]:
        """
        同步单只股票的日线数据

        Args:
            db: 数据库会话
            config: 同步配置，必须包含 ts_code 或 symbol，可选 start_date, end_date
            extra_info: 额外信息字典

        Returns:
            同步结果字典
        """
        ts_code = config.get("ts_code") or config.get("symbol")  # 兼容旧配置
        if not ts_code:
            raise ValueError("同步日线数据需要指定 ts_code 参数")

        start_date = config.get("start_date")
        end_date = config.get("end_date")
        count = self.data_scheduler.sync_daily_data(db, ts_code, start_date, end_date, extra_info)
        return {
            "success": True,
            "count": count,
            "ts_code": ts_code,
            "message": f"成功同步 {ts_code} 的 {count} 条日线数据"
        }

    def get_strategy_name(self) -> str:
        return "sync_daily_data"


class AllDailyDataSyncStrategy(DataSyncStrategy):
    """日线数据同步策略（所有股票）"""

    def __init__(self):
        self.data_scheduler = DataScheduler()

    def sync(self, db: Session, config: dict[str, Any], extra_info: dict | None = None) -> dict[str, Any]:
        """
        同步所有股票的日线数据

        Args:
            db: 数据库会话
            config: 同步配置，可选 start_date, end_date, codelist
            extra_info: 额外信息字典

        Returns:
            同步结果字典
        """
        start_date = config.get("start_date")
        end_date = config.get("end_date")
        codelist = config.get("codelist")  # 可以是字符串（逗号分隔）或列表

        # 处理 codelist：如果是字符串，转换为列表
        if isinstance(codelist, str):
            codelist = [code.strip() for code in codelist.split(",") if code.strip()]
        elif codelist is None:
            codelist = None

        from datetime import date

        # 判断是否所有参数都未传入
        all_params_empty = not codelist and not start_date and not end_date

        if all_params_empty:
            # 使用Repository获取最后一个交易日
            trading_date_repo = TradingDateRepository(db)
            latest_date = trading_date_repo.get_latest_trading_date()
            if latest_date:
                start_date = end_date = latest_date.strftime("%Y%m%d")
                logger.info(f"所有参数均无传入，使用最后一个交易日: {start_date}")
            else:
                # 如果无法获取，使用今日
                today = date.today()
                start_date = end_date = today.strftime("%Y%m%d")
                logger.info(f"无法获取最后一个交易日，使用今日: {start_date}")

        # 处理部分参数未传入的情况
        if not start_date:
            # 无start-date传参，默认开始时间为20250101
            start_date = "20250101"
            logger.info(f"未提供start-date，使用默认值: {start_date}")

        if not end_date:
            # 无end-date传参，默认结束时间为同步当日
            end_date = date.today().strftime("%Y%m%d")
            logger.info(f"未提供end-date，使用默认值: {end_date}")

        # 无codelist传参，默认同步所有code的数据（codelist=None）
        if codelist:
            logger.info(f"指定股票列表，共 {len(codelist)} 只股票")

        result = self.data_scheduler.sync_all_daily_data(db, start_date, end_date, extra_info, codelist)
        return {
            "success": True,
            "total": result.get("total", 0),
            "success_count": result.get("success", 0),
            "failed_count": len(result.get("failed", [])),
            "failed_symbols": result.get("failed", []),
            "message": f"同步完成: 成功 {result.get('success', 0)}/{result.get('total', 0)}"
        }

    def get_strategy_name(self) -> str:
        return "sync_all_daily_data"
