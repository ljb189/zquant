# Copyright 2025 ZQuant Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
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
通知相关Pydantic模型
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from zquant.models.notification import NotificationType


class NotificationCreate(BaseModel):
    """创建通知请求模型"""

    user_id: int = Field(..., description="用户ID")
    type: NotificationType = Field(NotificationType.SYSTEM, description="通知类型")
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: str = Field(..., min_length=1, description="通知内容")
    extra_data: dict[str, Any] | None = Field(None, description="额外数据（JSON格式）")

    @field_validator("extra_data", mode="before")
    @classmethod
    def parse_extra_data(cls, v):
        """解析extra_data"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class NotificationUpdate(BaseModel):
    """更新通知请求模型"""

    is_read: bool | None = Field(None, description="是否已读")


class NotificationResponse(BaseModel):
    """通知响应模型"""

    id: int = Field(..., description="通知ID")
    user_id: int = Field(..., description="用户ID")
    type: str = Field(..., description="通知类型：system, task, data等")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    is_read: bool = Field(..., description="是否已读")
    extra_data: dict[str, Any] | None = Field(None, description="额外数据（JSON格式）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

    @field_validator("extra_data", mode="before")
    @classmethod
    def parse_extra_data(cls, v):
        """解析extra_data"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v


class NotificationListResponse(BaseModel):
    """通知列表响应（分页）"""

    items: list[NotificationResponse] = Field(..., description="通知列表")
    total: int = Field(..., description="总记录数")
    skip: int = Field(..., description="跳过记录数")
    limit: int = Field(..., description="限制返回记录数")

    class Config:
        from_attributes = True


class NotificationStatsResponse(BaseModel):
    """通知统计响应"""

    unread_count: int = Field(..., description="未读通知数")
    total_count: int = Field(..., description="总通知数")
