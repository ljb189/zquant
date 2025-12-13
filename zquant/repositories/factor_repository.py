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
因子数据Repository

统一因子相关数据访问
"""

from datetime import date
from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import text

from zquant.models.factor import FactorDefinition, FactorConfig, FactorModel


class FactorRepository:
    """因子数据Repository"""

    def __init__(self, db: Session):
        """
        初始化Repository

        Args:
            db: 数据库会话
        """
        self.db = db

    def get_factor_definitions(
        self, enabled: Optional[bool] = None, limit: Optional[int] = None
    ) -> list[FactorDefinition]:
        """
        获取因子定义列表

        Args:
            enabled: 是否启用，None表示不筛选
            limit: 限制数量

        Returns:
            因子定义列表
        """
        query = self.db.query(FactorDefinition)
        if enabled is not None:
            query = query.filter(FactorDefinition.enabled == enabled)
        query = query.order_by(FactorDefinition.id)
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_factor_definition_by_id(self, factor_id: int) -> Optional[FactorDefinition]:
        """
        根据ID获取因子定义

        Args:
            factor_id: 因子ID

        Returns:
            因子定义，如果不存在则返回None
        """
        return self.db.query(FactorDefinition).filter(FactorDefinition.id == factor_id).first()

    def get_factor_definition_by_name(
        self, factor_name: str
    ) -> Optional[FactorDefinition]:
        """
        根据名称获取因子定义

        Args:
            factor_name: 因子名称

        Returns:
            因子定义，如果不存在则返回None
        """
        return (
            self.db.query(FactorDefinition)
            .filter(FactorDefinition.factor_name == factor_name)
            .first()
        )

    def get_factor_config(self, factor_id: int) -> Optional[FactorConfig]:
        """
        获取因子配置

        Args:
            factor_id: 因子ID

        Returns:
            因子配置，如果不存在则返回None
        """
        return (
            self.db.query(FactorConfig)
            .filter(
                FactorConfig.factor_id == factor_id, FactorConfig.enabled == True
            )
            .first()
        )

    def get_factor_model(self, model_id: int) -> Optional[FactorModel]:
        """
        获取因子模型

        Args:
            model_id: 模型ID

        Returns:
            因子模型，如果不存在则返回None
        """
        return (
            self.db.query(FactorModel)
            .filter(FactorModel.id == model_id, FactorModel.enabled == True)
            .first()
        )

    def get_default_factor_model(self, factor_id: int) -> Optional[FactorModel]:
        """
        获取默认因子模型

        Args:
            factor_id: 因子ID

        Returns:
            默认因子模型，如果不存在则返回None
        """
        return (
            self.db.query(FactorModel)
            .filter(
                FactorModel.factor_id == factor_id,
                FactorModel.is_default == True,
                FactorModel.enabled == True,
            )
            .first()
        )

    def get_factor_results(
        self,
        code: str,
        factor_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[dict]:
        """
        获取因子计算结果

        Args:
            code: 股票代码
            factor_name: 因子名称（None表示查询所有因子）
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            因子结果列表
        """
        # 提取code的数字部分
        code_num = code.split(".")[0] if "." in code else code
        table_name = f"zq_quant_factor_spacex_{code_num}"

        # 检查表是否存在
        try:
            check_sql = text(
                f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = :table_name"
            )
            result = self.db.execute(check_sql, {"table_name": table_name}).fetchone()
            if not result or result[0] == 0:
                logger.warning(f"因子结果表不存在: {table_name}")
                return []
        except Exception as e:
            logger.error(f"检查表是否存在失败: {table_name}, error={e}")
            return []

        # 构建查询SQL
        query_sql = f"SELECT * FROM `{table_name}` WHERE 1=1"
        params = {}

        if start_date:
            query_sql += " AND trade_date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query_sql += " AND trade_date <= :end_date"
            params["end_date"] = end_date

        query_sql += " ORDER BY trade_date DESC"

        try:
            result = self.db.execute(text(query_sql), params)
            rows = result.fetchall()
            columns = result.keys()

            records = []
            for row in rows:
                row_dict = dict(zip(columns, row, strict=False))
                records.append(row_dict)

            return records
        except Exception as e:
            logger.error(f"查询因子结果失败: {table_name}, error={e}")
            return []
