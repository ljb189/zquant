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
Tushare API辅助类

统一处理TushareClient初始化和错误处理
"""

from typing import Optional, Callable, Any
from loguru import logger
from sqlalchemy.orm import Session

from zquant.data.etl.tushare import TushareClient


class TushareAPIHelper:
    """Tushare API辅助类"""

    @staticmethod
    def get_client(db: Session) -> tuple[Optional[TushareClient], Optional[str]]:
        """
        获取TushareClient实例

        Args:
            db: 数据库会话

        Returns:
            (TushareClient实例, 错误消息)
            如果初始化失败，返回(None, 错误消息)
        """
        try:
            client = TushareClient(db=db)
            return client, None
        except Exception as e:
            error_msg = f"初始化Tushare客户端失败: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    @staticmethod
    def safe_call_api(
        func: Callable,
        *args,
        error_message: str = "API调用失败",
        **kwargs
    ) -> tuple[Optional[Any], Optional[str]]:
        """
        安全调用API方法

        Args:
            func: 要调用的API方法
            *args: 位置参数
            error_message: 错误消息前缀
            **kwargs: 关键字参数

        Returns:
            (API返回结果, 错误消息)
            如果调用失败，返回(None, 错误消息)
        """
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            error_msg = f"{error_message}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    @staticmethod
    def format_date_str(date_obj) -> str:
        """
        格式化日期为YYYYMMDD字符串

        Args:
            date_obj: 日期对象

        Returns:
            YYYYMMDD格式的字符串
        """
        if date_obj:
            return date_obj.strftime("%Y%m%d")
        return ""

    @staticmethod
    def parse_symbols(symbols_str: str) -> list[str]:
        """
        解析股票代码字符串为列表

        Args:
            symbols_str: 股票代码字符串（逗号分隔）

        Returns:
            股票代码列表
        """
        return [s.strip() for s in symbols_str.split(",") if s.strip()]

    @staticmethod
    def build_error_response(
        response_class: type,
        error_message: str,
        request_params: dict | None = None,
        **kwargs
    ) -> Any:
        """
        构建错误响应对象

        Args:
            response_class: 响应类
            error_message: 错误消息
            request_params: 请求参数
            **kwargs: 其他响应字段

        Returns:
            响应对象
        """
        default_params = {
            "success": False,
            "message": error_message,
        }
        if request_params is not None:
            default_params["request_params"] = request_params

        # 设置默认值
        defaults = {
            "data": [],
            "total_count": 0,
            "symbols": [],
            "ts_codes": [],
            "failed_codes": [],
            "total_db_records": 0,
            "total_api_records": 0,
            "consistent_count": 0,
            "difference_count": 0,
            "differences": [],
            "consistents": [],
        }

        # 合并参数
        params = {**defaults, **default_params, **kwargs}
        return response_class(**params)
