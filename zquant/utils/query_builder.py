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
查询构建器

提供链式查询构建，统一数据库查询逻辑
"""

from typing import Any, Optional, TypeVar, Generic
from datetime import date
from sqlalchemy.orm import Query, Session
from sqlalchemy import desc, asc

T = TypeVar("T")


class QueryBuilder(Generic[T]):
    """查询构建器，支持链式调用"""

    def __init__(self, db: Session, model_class: type[T]):
        """
        初始化查询构建器

        Args:
            db: 数据库会话
            model_class: 模型类
        """
        self.db = db
        self.model_class = model_class
        self._query: Query[T] = db.query(model_class)

    def filter(self, *conditions) -> "QueryBuilder[T]":
        """
        添加过滤条件

        Args:
            *conditions: SQLAlchemy过滤条件

        Returns:
            self，支持链式调用
        """
        if conditions:
            self._query = self._query.filter(*conditions)
        return self

    def filter_by(self, **kwargs) -> "QueryBuilder[T]":
        """
        添加等值过滤条件

        Args:
            **kwargs: 字段名和值的映射

        Returns:
            self，支持链式调用
        """
        if kwargs:
            self._query = self._query.filter_by(**kwargs)
        return self

    def order_by(self, *fields, desc: bool = False) -> "QueryBuilder[T]":
        """
        添加排序条件

        Args:
            *fields: 排序字段
            desc: 是否降序，默认False（升序）

        Returns:
            self，支持链式调用
        """
        if fields:
            if desc:
                self._query = self._query.order_by(*[desc(f) for f in fields])
            else:
                self._query = self._query.order_by(*fields)
        return self

    def limit(self, limit: int) -> "QueryBuilder[T]":
        """
        限制返回记录数

        Args:
            limit: 最大记录数

        Returns:
            self，支持链式调用
        """
        if limit and limit > 0:
            self._query = self._query.limit(limit)
        return self

    def offset(self, offset: int) -> "QueryBuilder[T]":
        """
        设置偏移量

        Args:
            offset: 偏移量

        Returns:
            self，支持链式调用
        """
        if offset and offset >= 0:
            self._query = self._query.offset(offset)
        return self

    def paginate(self, page: int = 1, page_size: int = 20) -> "QueryBuilder[T]":
        """
        添加分页

        Args:
            page: 页码（从1开始）
            page_size: 每页记录数

        Returns:
            self，支持链式调用
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        offset = (page - 1) * page_size
        return self.offset(offset).limit(page_size)

    def date_range(self, date_field: Any, start_date: Optional[date] = None, end_date: Optional[date] = None) -> "QueryBuilder[T]":
        """
        添加日期范围过滤

        Args:
            date_field: 日期字段
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            self，支持链式调用
        """
        if start_date:
            self._query = self._query.filter(date_field >= start_date)
        if end_date:
            self._query = self._query.filter(date_field <= end_date)
        return self

    def build(self) -> Query[T]:
        """
        构建查询对象

        Returns:
            SQLAlchemy查询对象
        """
        return self._query

    def all(self) -> list[T]:
        """
        执行查询并返回所有结果

        Returns:
            结果列表
        """
        return self._query.all()

    def first(self) -> Optional[T]:
        """
        执行查询并返回第一条结果

        Returns:
            第一条结果，如果不存在则返回None
        """
        return self._query.first()

    def count(self) -> int:
        """
        获取查询结果数量

        Returns:
            结果数量
        """
        return self._query.count()

    def exists(self) -> bool:
        """
        检查是否存在结果

        Returns:
            是否存在结果
        """
        return self._query.first() is not None
