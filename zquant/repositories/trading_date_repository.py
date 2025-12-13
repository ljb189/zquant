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
交易日历Repository

统一交易日历数据访问，提供缓存优化
"""

from datetime import date
from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import desc

from zquant.models.data import TustockTradecal
from zquant.utils.cache import get_cache


class TradingDateRepository:
    """交易日历Repository"""

    def __init__(self, db: Session):
        """
        初始化Repository

        Args:
            db: 数据库会话
        """
        self.db = db
        self.cache = get_cache()
        self._cache_prefix = "trading_date:"

    def get_latest_trading_date(self, exchange: str = "SSE") -> Optional[date]:
        """
        获取最后一个交易日

        Args:
            exchange: 交易所代码，默认SSE

        Returns:
            最后一个交易日，如果查询失败则返回None
        """
        cache_key = f"{self._cache_prefix}latest:{exchange}"
        cached = self.cache.get(cache_key)
        if cached:
            try:
                return date.fromisoformat(cached)
            except Exception:
                pass

        try:
            latest = (
                self.db.query(TustockTradecal.cal_date)
                .filter(
                    TustockTradecal.is_open == 1,
                    TustockTradecal.cal_date <= date.today(),
                    TustockTradecal.exchange == exchange,
                )
                .order_by(desc(TustockTradecal.cal_date))
                .first()
            )
            if latest and latest[0]:
                result = latest[0]
                # 缓存1小时
                self.cache.set(cache_key, result.isoformat(), ex=3600)
                return result
        except Exception as e:
            logger.warning(f"获取最后一个交易日失败: {e}")

        return None

    def is_trading_day(self, check_date: date, exchange: str = "SSE") -> bool:
        """
        判断指定日期是否为交易日

        Args:
            check_date: 要检查的日期
            exchange: 交易所代码，默认SSE

        Returns:
            是否为交易日
        """
        cache_key = f"{self._cache_prefix}is_trading:{exchange}:{check_date.isoformat()}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached == "1"

        try:
            record = (
                self.db.query(TustockTradecal)
                .filter(
                    TustockTradecal.cal_date == check_date,
                    TustockTradecal.exchange == exchange,
                )
                .first()
            )
            result = record is not None and record.is_open == 1
            # 缓存1天
            self.cache.set(cache_key, "1" if result else "0", ex=86400)
            return result
        except Exception as e:
            logger.warning(f"查询交易日历失败: {e}")
            return False

    def get_trading_dates(
        self, start_date: date, end_date: date, exchange: str = "SSE"
    ) -> list[date]:
        """
        获取指定日期范围内的交易日列表

        Args:
            start_date: 开始日期
            end_date: 结束日期
            exchange: 交易所代码，默认SSE

        Returns:
            交易日列表
        """
        cache_key = f"{self._cache_prefix}range:{exchange}:{start_date.isoformat()}:{end_date.isoformat()}"
        cached = self.cache.get(cache_key)
        if cached:
            try:
                import json
                date_strs = json.loads(cached)
                return [date.fromisoformat(d) for d in date_strs]
            except Exception:
                pass

        try:
            records = (
                self.db.query(TustockTradecal.cal_date)
                .filter(
                    TustockTradecal.cal_date >= start_date,
                    TustockTradecal.cal_date <= end_date,
                    TustockTradecal.is_open == 1,
                    TustockTradecal.exchange == exchange,
                )
                .order_by(TustockTradecal.cal_date)
                .all()
            )
            result = [record[0] for record in records]
            # 缓存1小时
            if result:
                import json
                date_strs = [d.isoformat() for d in result]
                self.cache.set(cache_key, json.dumps(date_strs), ex=3600)
            return result
        except Exception as e:
            logger.warning(f"获取交易日列表失败: {e}")
            return []

    def get_trading_calendar_records(
        self, start_date: date, end_date: date, exchange: Optional[str] = None
    ) -> list[dict]:
        """
        获取交易日历完整记录

        Args:
            start_date: 开始日期
            end_date: 结束日期
            exchange: 交易所代码，None表示所有交易所

        Returns:
            交易日历记录列表
        """
        try:
            query = self.db.query(TustockTradecal).filter(
                TustockTradecal.cal_date >= start_date,
                TustockTradecal.cal_date <= end_date,
            )

            if exchange:
                query = query.filter(TustockTradecal.exchange == exchange)

            records = query.order_by(TustockTradecal.cal_date).all()

            # 转换为字典列表
            result = []
            for record in records:
                result.append(
                    {
                        "id": record.id,
                        "exchange": record.exchange,
                        "cal_date": record.cal_date,
                        "is_open": record.is_open,
                        "pretrade_date": record.pretrade_date,
                        "created_by": record.created_by,
                        "created_time": record.created_time,
                        "updated_by": record.updated_by,
                        "updated_time": record.updated_time,
                    }
                )
            return result
        except Exception as e:
            logger.warning(f"获取交易日历记录失败: {e}")
            return []
