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
因子计算器基础类
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any

from sqlalchemy.orm import Session


class BaseFactorCalculator(ABC):
    """因子计算器基类"""

    def __init__(self, model_code: str, config: dict[str, Any] | None = None):
        """
        初始化因子计算器

        Args:
            model_code: 模型代码
            config: 模型配置
        """
        self.model_code = model_code
        self.config = config or {}

    @abstractmethod
    def calculate(self, db: Session, code: str, trade_date: date) -> float | None:
        """
        计算因子值

        Args:
            db: 数据库会话
            code: 股票代码（如：000001.SZ）
            trade_date: 交易日期

        Returns:
            因子值，如果无法计算则返回None
        """
        pass

    @abstractmethod
    def validate_config(self) -> tuple[bool, str]:
        """
        验证配置是否有效

        Returns:
            (是否有效, 错误信息)
        """
        pass

    def get_required_data_tables(self) -> list[str]:
        """
        获取所需的数据表列表

        Returns:
            数据表名称列表
        """
        return []

