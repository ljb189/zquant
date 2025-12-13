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
用户相关Pydantic模型
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserBase(BaseModel):
    """用户基础模型"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名（3-50个字符）")
    email: EmailStr = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    """创建用户模型"""

    password: str = Field(
        ..., min_length=8, max_length=128, description="密码（至少8位，包含大小写字母、数字和特殊字符）"
    )
    password_confirm: str = Field(..., description="确认密码")
    role_id: int = Field(..., description="角色ID")

    @model_validator(mode="after")
    def validate_password_match(self):
        """验证密码确认"""
        if self.password != self.password_confirm:
            raise ValueError("两次输入的密码不一致")
        return self


class UserUpdate(BaseModel):
    """更新用户模型"""

    email: EmailStr | None = Field(None, description="邮箱地址")
    is_active: bool | None = Field(None, description="是否激活")
    role_id: int | None = Field(None, description="角色ID")


class PasswordReset(BaseModel):
    """密码重置模型"""

    password: str = Field(
        ..., min_length=8, max_length=128, description="新密码（至少8位，包含大小写字母、数字和特殊字符）"
    )
    password_confirm: str = Field(..., description="确认新密码")

    @model_validator(mode="after")
    def validate_password_match(self):
        """验证密码确认"""
        if self.password != self.password_confirm:
            raise ValueError("两次输入的密码不一致")
        return self


class UserInDB(UserBase):
    """数据库中的用户模型"""

    id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """用户响应模型"""

    id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """角色基础模型"""

    name: str = Field(..., description="角色名称")
    description: str | None = Field(None, description="角色描述")


class RoleCreate(RoleBase):
    """创建角色模型"""


class RoleUpdate(BaseModel):
    """更新角色模型"""

    name: str | None = Field(None, description="角色名称")
    description: str | None = Field(None, description="角色描述")


class RoleResponse(RoleBase):
    """角色响应模型"""

    id: int = Field(..., description="角色ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """权限基础模型"""

    name: str = Field(..., description="权限名称")
    resource: str = Field(..., description="资源类型，如：user, data, backtest")
    action: str = Field(..., description="操作类型，如：create, read, update, delete")
    description: str | None = Field(None, description="权限描述")


class PermissionCreate(PermissionBase):
    """创建权限模型"""


class PermissionUpdate(BaseModel):
    """更新权限模型"""

    name: str | None = Field(None, description="权限名称")
    resource: str | None = Field(None, description="资源类型")
    action: str | None = Field(None, description="操作类型")
    description: str | None = Field(None, description="权限描述")


class PermissionResponse(PermissionBase):
    """权限响应模型"""

    id: int = Field(..., description="权限ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token响应模型"""

    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")


class TokenData(BaseModel):
    """Token数据模型"""

    user_id: int | None = Field(None, description="用户ID")
    username: str | None = Field(None, description="用户名")


class LoginRequest(BaseModel):
    """登录请求模型"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class APIKeyCreate(BaseModel):
    """创建API密钥请求模型"""

    name: str | None = Field(None, max_length=100, description="密钥名称/描述")


class APIKeyResponse(BaseModel):
    """API密钥响应模型"""

    id: int = Field(..., description="API密钥ID")
    access_key: str = Field(..., description="访问密钥")
    name: str | None = Field(None, description="密钥名称/描述")
    is_active: bool = Field(..., description="是否激活")
    last_used_at: datetime | None = Field(None, description="最后使用时间")
    created_at: datetime = Field(..., description="创建时间")
    expires_at: datetime | None = Field(None, description="过期时间，None表示永不过期")

    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    """创建API密钥响应模型（包含secret_key，仅返回一次）"""

    id: int = Field(..., description="API密钥ID")
    access_key: str = Field(..., description="访问密钥")
    secret_key: str = Field(..., description="密钥（仅返回一次，请妥善保管）")
    name: str | None = Field(None, description="密钥名称/描述")
    created_at: datetime = Field(..., description="创建时间")
    expires_at: datetime | None = Field(None, description="过期时间，None表示永不过期")
    message: str = Field("请妥善保管secret_key，系统不会再次显示", description="提示消息")


class PageResponse(BaseModel):
    """分页响应模型"""

    items: list[Any] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    skip: int = Field(..., description="跳过记录数")
    limit: int = Field(..., description="限制返回记录数")

    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """角色响应模型（包含权限列表）"""

    permissions: list[PermissionResponse] = Field(default_factory=list, description="权限列表")

    class Config:
        from_attributes = True


class AssignPermissionsRequest(BaseModel):
    """分配权限请求模型"""

    permission_ids: list[int] = Field(..., description="权限ID列表")


# ============ 我的自选相关 Schema ============


class FavoriteCreate(BaseModel):
    """创建自选请求模型"""

    code: str = Field(..., min_length=6, max_length=6, description="股票代码（6位数字），如：000001")
    comment: str | None = Field(None, max_length=2000, description="关注理由")
    fav_datettime: datetime | None = Field(None, description="自选日期")


class FavoriteUpdate(BaseModel):
    """更新自选请求模型"""

    comment: str | None = Field(None, max_length=2000, description="关注理由")
    fav_datettime: datetime | None = Field(None, description="自选日期")


class FavoriteResponse(BaseModel):
    """自选响应模型"""

    id: int = Field(..., description="自选ID")
    user_id: int = Field(..., description="用户ID")
    code: str = Field(..., description="股票代码（6位数字）")
    comment: str | None = Field(None, description="关注理由")
    fav_datettime: datetime | None = Field(None, description="自选日期")
    created_by: str | None = Field(None, description="创建人")
    created_time: datetime = Field(..., description="创建时间")
    updated_by: str | None = Field(None, description="修改人")
    updated_time: datetime = Field(..., description="更新时间")
    # 关联股票信息（可选）
    stock_name: str | None = Field(None, description="股票名称")
    stock_ts_code: str | None = Field(None, description="TS代码")

    class Config:
        from_attributes = True


class FavoriteListRequest(BaseModel):
    """查询自选列表请求模型"""

    code: str | None = Field(None, description="股票代码（精确查询）")
    start_date: date | None = Field(None, description="开始日期（自选日期范围）")
    end_date: date | None = Field(None, description="结束日期（自选日期范围）")
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(100, ge=1, le=1000, description="每页记录数")
    order_by: str | None = Field("created_time", description="排序字段：id, code, fav_datettime, created_time")
    order: str | None = Field("desc", description="排序方向：asc 或 desc")


class FavoriteListResponse(BaseModel):
    """自选列表响应模型"""

    items: list[FavoriteResponse] = Field(..., description="自选列表")
    total: int = Field(..., description="总记录数")
    skip: int = Field(..., description="跳过记录数")
    limit: int = Field(..., description="限制返回记录数")


# ============ 我的持仓相关 Schema ============


class PositionCreate(BaseModel):
    """创建持仓请求模型"""

    code: str = Field(..., min_length=6, max_length=6, description="股票代码（6位数字），如：000001")
    quantity: float = Field(..., gt=0, description="持仓数量（股数），必须大于0")
    avg_cost: float = Field(..., gt=0, description="平均成本价（元），必须大于0")
    buy_date: date | None = Field(None, description="买入日期")
    current_price: float | None = Field(None, gt=0, description="当前价格（元），可选，可从行情数据获取")
    comment: str | None = Field(None, max_length=2000, description="备注")


class PositionUpdate(BaseModel):
    """更新持仓请求模型"""

    quantity: float | None = Field(None, gt=0, description="持仓数量（股数），必须大于0")
    avg_cost: float | None = Field(None, gt=0, description="平均成本价（元），必须大于0")
    buy_date: date | None = Field(None, description="买入日期")
    current_price: float | None = Field(None, gt=0, description="当前价格（元），可选")
    comment: str | None = Field(None, max_length=2000, description="备注")


class PositionResponse(BaseModel):
    """持仓响应模型"""

    id: int = Field(..., description="持仓ID")
    user_id: int = Field(..., description="用户ID")
    code: str = Field(..., description="股票代码（6位数字）")
    quantity: float = Field(..., description="持仓数量（股数）")
    avg_cost: float = Field(..., description="平均成本价（元）")
    buy_date: date | None = Field(None, description="买入日期")
    current_price: float | None = Field(None, description="当前价格（元）")
    market_value: float | None = Field(None, description="市值（元）")
    profit: float | None = Field(None, description="盈亏（元）")
    profit_pct: float | None = Field(None, description="盈亏比例（%）")
    comment: str | None = Field(None, description="备注")
    created_by: str | None = Field(None, description="创建人")
    created_time: datetime = Field(..., description="创建时间")
    updated_by: str | None = Field(None, description="修改人")
    updated_time: datetime = Field(..., description="更新时间")
    # 关联股票信息（可选）
    stock_name: str | None = Field(None, description="股票名称")
    stock_ts_code: str | None = Field(None, description="TS代码")

    class Config:
        from_attributes = True


class PositionListRequest(BaseModel):
    """查询持仓列表请求模型"""

    code: str | None = Field(None, description="股票代码（精确查询）")
    start_date: date | None = Field(None, description="开始日期（买入日期范围）")
    end_date: date | None = Field(None, description="结束日期（买入日期范围）")
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(100, ge=1, le=1000, description="每页记录数")
    order_by: str | None = Field("created_time", description="排序字段：id, code, buy_date, created_time")
    order: str | None = Field("desc", description="排序方向：asc 或 desc")


class PositionListResponse(BaseModel):
    """持仓列表响应模型"""

    items: list[PositionResponse] = Field(..., description="持仓列表")
    total: int = Field(..., description="总记录数")
    skip: int = Field(..., description="跳过记录数")
    limit: int = Field(..., description="限制返回记录数")
