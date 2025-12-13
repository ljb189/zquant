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
数据同步策略基类

定义统一的数据同步接口
"""

from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.orm import Session


class DataSyncStrategy(ABC):
    """数据同步策略接口"""

    @abstractmethod
    def sync(self, db: Session, config: dict[str, Any], extra_info: dict | None = None) -> dict[str, Any]:
        """
        执行数据同步

        Args:
            db: 数据库会话
            config: 同步配置
            extra_info: 额外信息字典，可包含 created_by 和 updated_by 字段

        Returns:
            同步结果字典，包含 success, count, message 等字段
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        获取策略名称

        Returns:
            策略名称
        """
        pass
