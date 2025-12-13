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
价格数据Repository

统一价格数据访问，支持批量查询优化
"""

from datetime import date
from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session

from zquant.data.processor import DataProcessor


class PriceDataRepository:
    """价格数据Repository"""

    def __init__(self, db: Session):
        """
        初始化Repository

        Args:
            db: 数据库会话
        """
        self.db = db

    def get_daily_data(
        self,
        ts_code: str | list[str] | None = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """
        获取日线数据

        Args:
            ts_code: TS代码，单个代码如：000001.SZ，多个代码如：['000001.SZ', '000002.SZ']，None表示查询所有
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            日线数据列表
        """
        return DataProcessor.get_daily_data_records(
            self.db, ts_code=ts_code, start_date=start_date, end_date=end_date
        )

    def batch_get_daily_data(
        self, ts_codes: list[str], start_date: date, end_date: date
    ) -> dict[str, list[dict]]:
        """
        批量获取多个股票的价格数据

        Args:
            ts_codes: TS代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            按股票代码分组的数据字典 {ts_code: [records]}
        """
        # 使用批量查询接口
        all_records = DataProcessor.get_daily_data_records(
            self.db, ts_code=ts_codes, start_date=start_date, end_date=end_date
        )

        # 按ts_code分组
        result: dict[str, list[dict]] = {}
        for record in all_records:
            code = record.get("ts_code")
            if code:
                if code not in result:
                    result[code] = []
                result[code].append(record)

        return result

    def get_daily_basic_data(
        self,
        ts_code: str | list[str] | None = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """
        获取每日指标数据

        Args:
            ts_code: TS代码，单个代码如：000001.SZ，多个代码如：['000001.SZ', '000002.SZ']，None表示查询所有
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            每日指标数据列表
        """
        return DataProcessor.get_daily_basic_data_records(
            self.db, ts_code=ts_code, start_date=start_date, end_date=end_date
        )

    def batch_get_daily_basic_data(
        self, ts_codes: list[str], start_date: date, end_date: date
    ) -> dict[str, list[dict]]:
        """
        批量获取多个股票的每日指标数据

        Args:
            ts_codes: TS代码列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            按股票代码分组的数据字典 {ts_code: [records]}
        """
        # 使用批量查询接口
        all_records = DataProcessor.get_daily_basic_data_records(
            self.db, ts_code=ts_codes, start_date=start_date, end_date=end_date
        )

        # 按ts_code分组
        result: dict[str, list[dict]] = {}
        for record in all_records:
            code = record.get("ts_code")
            if code:
                if code not in result:
                    result[code] = []
                result[code].append(record)

        return result
