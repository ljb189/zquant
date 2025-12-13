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
股票信息Repository

统一股票数据访问，提供批量查询和缓存优化
"""

from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session

from zquant.models.data import Tustock
from zquant.utils.cache import get_cache


class StockRepository:
    """股票信息Repository"""

    def __init__(self, db: Session):
        """
        初始化Repository

        Args:
            db: 数据库会话
        """
        self.db = db
        self.cache = get_cache()
        self._cache_prefix = "stock:"
        # 内存缓存：symbol -> ts_code 映射
        self._symbol_to_ts_code_cache: dict[str, str] = {}

    def get_ts_code_by_symbol(self, symbol: str) -> Optional[str]:
        """
        根据symbol获取ts_code

        Args:
            symbol: 股票代码（6位数字）

        Returns:
            TS代码，如果不存在则返回None
        """
        # 先查内存缓存
        if symbol in self._symbol_to_ts_code_cache:
            return self._symbol_to_ts_code_cache[symbol]

        # 查Redis缓存
        cache_key = f"{self._cache_prefix}symbol_to_ts:{symbol}"
        cached = self.cache.get(cache_key)
        if cached:
            self._symbol_to_ts_code_cache[symbol] = cached
            return cached

        # 查数据库
        try:
            stock = self.db.query(Tustock).filter(Tustock.symbol == symbol).first()
            if stock:
                ts_code = stock.ts_code
                # 更新缓存
                self._symbol_to_ts_code_cache[symbol] = ts_code
                self.cache.set(cache_key, ts_code, ex=86400)  # 缓存1天
                return ts_code
        except Exception as e:
            logger.warning(f"查询股票代码失败: {e}")

        return None

    def batch_get_ts_codes_by_symbols(self, symbols: list[str]) -> dict[str, str]:
        """
        批量根据symbol获取ts_code

        Args:
            symbols: 股票代码列表

        Returns:
            映射字典 {symbol: ts_code}
        """
        result = {}
        symbols_to_query = []

        # 先查缓存
        for symbol in symbols:
            if symbol in self._symbol_to_ts_code_cache:
                result[symbol] = self._symbol_to_ts_code_cache[symbol]
            else:
                cache_key = f"{self._cache_prefix}symbol_to_ts:{symbol}"
                cached = self.cache.get(cache_key)
                if cached:
                    result[symbol] = cached
                    self._symbol_to_ts_code_cache[symbol] = cached
                else:
                    symbols_to_query.append(symbol)

        # 批量查询数据库
        if symbols_to_query:
            try:
                stocks = (
                    self.db.query(Tustock)
                    .filter(Tustock.symbol.in_(symbols_to_query))
                    .all()
                )
                for stock in stocks:
                    if stock.symbol:
                        result[stock.symbol] = stock.ts_code
                        # 更新缓存
                        self._symbol_to_ts_code_cache[stock.symbol] = stock.ts_code
                        cache_key = f"{self._cache_prefix}symbol_to_ts:{stock.symbol}"
                        self.cache.set(cache_key, stock.ts_code, ex=86400)
            except Exception as e:
                logger.warning(f"批量查询股票代码失败: {e}")

        return result

    def get_stock_by_ts_code(self, ts_code: str) -> Optional[dict]:
        """
        根据ts_code获取股票信息

        Args:
            ts_code: TS代码

        Returns:
            股票信息字典，如果不存在则返回None
        """
        cache_key = f"{self._cache_prefix}info:{ts_code}"
        cached = self.cache.get(cache_key)
        if cached:
            try:
                import json
                return json.loads(cached)
            except Exception:
                pass

        try:
            stock = self.db.query(Tustock).filter(Tustock.ts_code == ts_code).first()
            if stock:
                result = {
                    "ts_code": stock.ts_code,
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "exchange": stock.exchange,
                    "market": stock.market,
                    "list_status": stock.list_status,
                    "list_date": stock.list_date.isoformat() if stock.list_date else None,
                    "delist_date": stock.delist_date.isoformat() if stock.delist_date else None,
                }
                # 缓存1小时
                import json
                self.cache.set(cache_key, json.dumps(result), ex=3600)
                return result
        except Exception as e:
            logger.warning(f"查询股票信息失败: {e}")

        return None

    def get_stock_list(
        self,
        exchange: Optional[str] = None,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
    ) -> list[dict]:
        """
        获取股票列表

        Args:
            exchange: 交易所代码
            symbol: 股票代码
            name: 股票名称（模糊查询）

        Returns:
            股票列表
        """
        try:
            query = self.db.query(Tustock).filter(Tustock.delist_date.is_(None))

            if exchange:
                query = query.filter(Tustock.exchange == exchange)

            if symbol:
                query = query.filter(Tustock.symbol == symbol)

            if name:
                query = query.filter(Tustock.name.like(f"%{name}%"))

            stocks = query.all()

            result = []
            for stock in stocks:
                result.append(
                    {
                        "ts_code": stock.ts_code,
                        "symbol": stock.symbol,
                        "name": stock.name,
                        "area": stock.area,
                        "industry": stock.industry,
                        "fullname": stock.fullname,
                        "enname": stock.enname,
                        "cnspell": stock.cnspell,
                        "market": stock.market,
                        "exchange": stock.exchange,
                        "curr_type": stock.curr_type,
                        "list_status": stock.list_status,
                        "list_date": stock.list_date.isoformat() if stock.list_date else None,
                        "delist_date": stock.delist_date.isoformat() if stock.delist_date else None,
                        "is_hs": stock.is_hs,
                    }
                )
            return result
        except Exception as e:
            logger.warning(f"获取股票列表失败: {e}")
            return []
