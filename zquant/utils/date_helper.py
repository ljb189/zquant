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
日期处理工具类

统一处理日期相关逻辑，包括交易日判断、日期范围处理等
"""

from datetime import date, timedelta
from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import desc

from zquant.models.data import TustockTradecal


class DateHelper:
    """日期处理工具类"""

    @staticmethod
    def get_latest_trading_date(db: Session, exchange: str = "SSE") -> Optional[date]:
        """
        获取最后一个交易日

        Args:
            db: 数据库会话
            exchange: 交易所代码，默认SSE

        Returns:
            最后一个交易日，如果查询失败则返回None
        """
        try:
            latest = (
                db.query(TustockTradecal.cal_date)
                .filter(
                    TustockTradecal.is_open == 1,
                    TustockTradecal.cal_date <= date.today(),
                    TustockTradecal.exchange == exchange,
                )
                .order_by(desc(TustockTradecal.cal_date))
                .first()
            )
            if latest and latest[0]:
                return latest[0]
        except Exception as e:
            logger.warning(f"获取最后一个交易日失败: {e}")

        return None

    @staticmethod
    def is_trading_day(db: Session, check_date: date, exchange: str = "SSE") -> bool:
        """
        判断指定日期是否为交易日

        Args:
            db: 数据库会话
            check_date: 要检查的日期
            exchange: 交易所代码，默认SSE

        Returns:
            是否为交易日
        """
        try:
            record = (
                db.query(TustockTradecal)
                .filter(
                    TustockTradecal.cal_date == check_date,
                    TustockTradecal.exchange == exchange,
                )
                .first()
            )
            return record is not None and record.is_open == 1
        except Exception as e:
            logger.warning(f"查询交易日历失败: {e}")
            return False

    @staticmethod
    def get_trading_dates(
        db: Session, start_date: date, end_date: date, exchange: str = "SSE"
    ) -> list[date]:
        """
        获取指定日期范围内的交易日列表

        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            exchange: 交易所代码，默认SSE

        Returns:
            交易日列表
        """
        try:
            records = (
                db.query(TustockTradecal.cal_date)
                .filter(
                    TustockTradecal.cal_date >= start_date,
                    TustockTradecal.cal_date <= end_date,
                    TustockTradecal.is_open == 1,
                    TustockTradecal.exchange == exchange,
                )
                .order_by(TustockTradecal.cal_date)
                .all()
            )
            return [record[0] for record in records]
        except Exception as e:
            logger.warning(f"获取交易日列表失败: {e}")
            return []

    @staticmethod
    def format_date_range(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session | None = None,
        default_start: Optional[date] = None,
    ) -> tuple[date, date]:
        """
        格式化日期范围，处理默认值逻辑

        Args:
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            db: 数据库会话（用于获取最后一个交易日）
            default_start: 默认开始日期（如果start_date未提供）

        Returns:
            (格式化后的开始日期, 格式化后的结束日期)

        规则：
            - 如果所有参数都未传入：start_date 和 end_date 都默认为最后一个交易日
            - 如果至少有一个参数传入：
              start_date 默认为 default_start 或 2025-01-01
              end_date 默认为最后一个交易日
        """
        all_params_empty = not start_date and not end_date

        # 获取最后一个交易日
        latest_trading_date = None
        if db:
            latest_trading_date = DateHelper.get_latest_trading_date(db)

        if all_params_empty:
            # 规则一：所有参数均未传入时，使用最后一个交易日
            if latest_trading_date:
                return latest_trading_date, latest_trading_date
            else:
                # 如果无法获取最后一个交易日，使用今日
                today = date.today()
                return today, today
        else:
            # 规则二：至少有一个参数传入时
            if not start_date:
                # start_date 未提供，使用默认值
                if default_start:
                    start_date = default_start
                else:
                    start_date = date(2025, 1, 1)

            if not end_date:
                # end_date 未提供，使用最后一个交易日
                if latest_trading_date:
                    end_date = latest_trading_date
                else:
                    end_date = date.today()

        return start_date, end_date
