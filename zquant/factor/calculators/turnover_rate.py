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
换手率因子计算器
"""

from datetime import date, timedelta

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from zquant.factor.calculators.base import BaseFactorCalculator
from zquant.services.data import DataService


class TurnoverRateCalculator(BaseFactorCalculator):
    """换手率因子计算器"""

    MODEL_CODE = "turnover_rate"

    def __init__(self, config: dict | None = None):
        """
        初始化换手率计算器

        Args:
            config: 配置字典，支持以下字段：
                - source: 数据来源，可选值：daily_basic（每日指标表，默认）, custom（自定义）
                - field: 字段名，默认使用turnover_rate
                - method: 计算方法，可选值：None（直接取值，默认）, "ma"（移动平均）
                - window: 移动平均窗口大小（仅当method="ma"时有效），默认5
        """
        super().__init__(self.MODEL_CODE, config)
        self.source = self.config.get("source", "daily_basic")
        self.field = self.config.get("field", "turnover_rate")
        self.method = self.config.get("method")  # None 或 "ma"
        self.window = self.config.get("window", 5)  # 移动平均窗口，默认5

    def calculate(self, db: Session, code: str, trade_date: date) -> float | None:
        """
        计算换手率因子值

        Args:
            db: 数据库会话
            code: 股票代码（如：000001.SZ）
            trade_date: 交易日期

        Returns:
            换手率值，如果无法计算则返回None
        """
        try:
            if self.source == "daily_basic":
                # 如果使用移动平均方法
                if self.method == "ma":
                    # 获取历史数据：往前推 window * 2 天（确保有足够交易日数据）
                    start_date = trade_date - timedelta(days=self.window * 2)
                    daily_basic_data = DataService.get_daily_basic_data(
                        db, ts_code=code, start_date=start_date, end_date=trade_date
                    )
                    
                    if not daily_basic_data:
                        logger.warning(f"未找到 {code} 在 {start_date} 到 {trade_date} 期间的每日指标数据")
                        return -1

                    # 过滤有效数据：只取有 turnover_rate 值的记录
                    valid_records = []
                    for record in daily_basic_data:
                        value = record.get(self.field)
                        record_date = record.get("trade_date")
                        if value is not None and record_date is not None:
                            try:
                                # 确保日期是 date 对象或 ISO 格式字符串，以便正确排序
                                if isinstance(record_date, str):
                                    # 如果是字符串，尝试解析为 date 对象
                                    try:
                                        record_date = date.fromisoformat(record_date)
                                    except ValueError:
                                        # 如果解析失败，使用字符串排序（ISO 格式可以直接排序）
                                        pass
                                valid_records.append((record_date, float(value)))
                            except (ValueError, TypeError) as e:
                                logger.debug(f"跳过无效记录: trade_date={record_date}, value={value}, error={e}")
                                continue

                    if not valid_records:
                        logger.warning(f"{code} 在 {start_date} 到 {trade_date} 期间的 {self.field} 字段全部为空")
                        return None

                    # 按日期排序（确保是升序）
                    valid_records.sort(key=lambda x: x[0] if isinstance(x[0], date) else date.fromisoformat(x[0]) if isinstance(x[0], str) else x[0])

                    # 取最近 window 条记录
                    recent_records = valid_records[-self.window:]

                    # 如果有效数据不足 window 条，返回 None
                    if len(recent_records) < self.window:
                        logger.warning(
                            f"{code} 在 {start_date} 到 {trade_date} 期间的有效数据不足 {self.window} 条（实际 {len(recent_records)} 条）"
                        )
                        return -1

                    # 计算移动平均值
                    values = [value for _, value in recent_records]
                    ma_value = sum(values) / len(values)
                    logger.debug(
                        f"{code} 在 {trade_date} 的 {self.window}日移动平均换手率: {ma_value:.4f} "
                        f"(基于 {len(recent_records)} 条数据)"
                    )
                    return ma_value
                else:
                    # 直接获取当日的换手率值
                    daily_basic_data = DataService.get_daily_basic_data(db, ts_code=code, start_date=trade_date, end_date=trade_date)
                    
                    if not daily_basic_data:
                        logger.warning(f"未找到 {code} 在 {trade_date} 的每日指标数据")
                        return -1

                    # 获取第一条记录
                    record = daily_basic_data[0]
                    turnover_rate = record.get(self.field)

                    if turnover_rate is None:
                        logger.warning(f"{code} 在 {trade_date} 的 {self.field} 字段为空")
                        return None

                    return float(turnover_rate)
            else:
                logger.error(f"不支持的数据来源: {self.source}")
                return None

        except Exception as e:
            logger.error(f"计算换手率因子失败: code={code}, trade_date={trade_date}, error={e}")
            return None

    def validate_config(self) -> tuple[bool, str]:
        """
        验证配置是否有效

        Returns:
            (是否有效, 错误信息)
        """
        if self.source not in ["daily_basic", "custom"]:
            return False, f"不支持的数据来源: {self.source}"

        if not self.field:
            return False, "字段名不能为空"

        # 验证移动平均配置
        if self.method == "ma":
            if not isinstance(self.window, int) or self.window <= 0:
                return False, f"移动平均窗口大小必须是正整数，当前值: {self.window}"
            if self.window > 60:
                return False, f"移动平均窗口大小不能超过60，当前值: {self.window}"

        return True, ""

    def get_required_data_tables(self) -> list[str]:
        """
        获取所需的数据表列表

        Returns:
            数据表名称列表
        """
        if self.source == "daily_basic":
            return ["zq_data_tustock_daily_basic_*"]
        return []

