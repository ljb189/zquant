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
数据库类型转换工具
"""

from loguru import logger


def convert_sqlalchemy_type_to_mysql(sqlalchemy_type) -> str:
    """
    将SQLAlchemy类型转换为MySQL类型字符串
    Args:
        sqlalchemy_type: SQLAlchemy类型对象
    Returns:
        str: MySQL类型字符串
    """
    try:
        # 获取类型名称
        type_name = str(sqlalchemy_type).upper()

        # 类型映射
        type_mapping = {
            "DOUBLE": "DOUBLE",  # DOUBLE类型（8字节浮点数，精度更高）
            "FLOAT": "FLOAT",  # FLOAT类型（4字节浮点数）
            "INT": "INT",
            "INTEGER": "INT",
            "VARCHAR": str(sqlalchemy_type),  # VARCHAR(6) 等保持原样
            "DATE": "DATE",
            "DATETIME": "DATETIME",
            "TEXT": "TEXT",
            "BOOLEAN": "BOOLEAN",
            "DECIMAL": str(sqlalchemy_type),  # DECIMAL(10,2) 等保持原样
            "BIGINT": "BIGINT",
            "SMALLINT": "SMALLINT",
            "TINYINT": "TINYINT",
            "CHAR": str(sqlalchemy_type),  # CHAR(1) 等保持原样
            "LONGTEXT": "LONGTEXT",
            "MEDIUMTEXT": "MEDIUMTEXT",
            "TIMESTAMP": "TIMESTAMP",
            "TIME": "TIME",
            "YEAR": "YEAR",
            "BLOB": "BLOB",
            "LONGBLOB": "LONGBLOB",
            "MEDIUMBLOB": "MEDIUMBLOB",
            "TINYBLOB": "TINYBLOB",
        }

        # 处理VARCHAR类型
        if "VARCHAR" in type_name:
            return str(sqlalchemy_type)

        # 处理DECIMAL类型
        if "DECIMAL" in type_name:
            return str(sqlalchemy_type)

        # 处理CHAR类型
        if "CHAR" in type_name and "VARCHAR" not in type_name:
            return str(sqlalchemy_type)

        # 处理基本类型
        for sqlalchemy_pattern, mysql_type in type_mapping.items():
            if sqlalchemy_pattern in type_name:
                return mysql_type

        # 默认返回DOUBLE（日线数据已全部使用DOUBLE类型）
        logger.warning(f"Unknown SQLAlchemy type: {sqlalchemy_type}, using DOUBLE as default")
        return "DOUBLE"

    except Exception as e:
        logger.error(f"转换SQLAlchemy类型失败: {sqlalchemy_type}, error: {e}")
        return "DOUBLE"

