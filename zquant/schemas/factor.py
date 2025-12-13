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
因子相关Pydantic模型
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


# ==================== 因子定义 Schema ====================

class FactorDefinitionCreate(BaseModel):
    """创建因子定义请求"""

    factor_name: str = Field(..., description="因子名称（唯一标识）")
    cn_name: str = Field(..., description="中文简称")
    en_name: str | None = Field(None, description="英文简称")
    column_name: str = Field(..., description="因子表数据列名")
    description: str | None = Field(None, description="因子详细描述")
    enabled: bool = Field(True, description="是否启用")
    factor_config: dict[str, Any] | None = Field(None, description="因子配置，格式：{\"enabled\": bool, \"mappings\": [{\"model_id\": int, \"codes\": list[str]|None}, ...]}")


class FactorDefinitionUpdate(BaseModel):
    """更新因子定义请求"""

    cn_name: str | None = Field(None, description="中文简称")
    en_name: str | None = Field(None, description="英文简称")
    column_name: str | None = Field(None, description="因子表数据列名")
    description: str | None = Field(None, description="因子详细描述")
    enabled: bool | None = Field(None, description="是否启用")
    factor_config: dict[str, Any] | None = Field(None, description="因子配置，格式：{\"enabled\": bool, \"mappings\": [{\"model_id\": int, \"codes\": list[str]|None}, ...]}")


class FactorDefinitionResponse(BaseModel):
    """因子定义响应"""

    id: int
    factor_name: str
    cn_name: str
    en_name: str | None
    column_name: str
    description: str | None
    enabled: bool
    factor_config: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应"""
        data = {
            "id": obj.id,
            "factor_name": obj.factor_name,
            "cn_name": obj.cn_name,
            "en_name": obj.en_name,
            "column_name": obj.column_name,
            "description": obj.description,
            "enabled": obj.enabled,
            "factor_config": obj.get_factor_config(),
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)


class FactorDefinitionListResponse(BaseModel):
    """因子定义列表响应"""

    items: list[FactorDefinitionResponse] = Field(..., description="因子定义列表")
    total: int = Field(..., description="总数")


# ==================== 因子模型 Schema ====================

class FactorModelCreate(BaseModel):
    """创建因子模型请求"""

    factor_id: int = Field(..., description="因子ID")
    model_name: str = Field(..., description="模型名称")
    model_code: str = Field(..., description="模型代码（用于识别计算器类型）")
    config_json: dict[str, Any] | None = Field(None, description="模型配置（JSON格式）")
    is_default: bool = Field(False, description="是否默认算法")
    enabled: bool = Field(True, description="是否启用")

    class Config:
        protected_namespaces = ()


class FactorModelUpdate(BaseModel):
    """更新因子模型请求"""

    model_name: str | None = Field(None, description="模型名称")
    model_code: str | None = Field(None, description="模型代码")
    config_json: dict[str, Any] | None = Field(None, description="模型配置")
    is_default: bool | None = Field(None, description="是否默认算法")
    enabled: bool | None = Field(None, description="是否启用")

    class Config:
        protected_namespaces = ()


class FactorModelResponse(BaseModel):
    """因子模型响应"""

    id: int
    factor_id: int
    model_name: str
    model_code: str
    config_json: dict[str, Any] | None
    is_default: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        protected_namespaces = ()

    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应"""
        data = {
            "id": obj.id,
            "factor_id": obj.factor_id,
            "model_name": obj.model_name,
            "model_code": obj.model_code,
            "config_json": obj.get_config(),
            "is_default": obj.is_default,
            "enabled": obj.enabled,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)


class FactorModelListResponse(BaseModel):
    """因子模型列表响应"""

    items: list[FactorModelResponse] = Field(..., description="因子模型列表")
    total: int = Field(..., description="总数")


# ==================== 因子配置 Schema ====================

class FactorConfigMappingItem(BaseModel):
    """因子配置映射项（模型-代码列表对）"""

    model_id: int = Field(..., description="模型ID")
    codes: list[str] | None = Field(None, description="股票代码列表，None或空列表表示默认配置")

    class Config:
        protected_namespaces = ()


class FactorConfigCreate(BaseModel):
    """创建因子配置请求（支持多个映射）"""

    factor_id: int = Field(..., description="因子ID")
    mappings: list[FactorConfigMappingItem] = Field(..., description="模型-代码列表映射对列表")
    enabled: bool = Field(True, description="是否启用")
    
    def to_config_dict(self) -> dict[str, Any]:
        """转换为配置字典"""
        return {
            "enabled": self.enabled,
            "mappings": [{"model_id": m.model_id, "codes": m.codes} for m in self.mappings]
        }


class FactorConfigUpdate(BaseModel):
    """更新因子配置请求（支持批量更新映射）"""

    mappings: list[FactorConfigMappingItem] | None = Field(None, description="模型-代码列表映射对列表（None表示不更新）")
    enabled: bool | None = Field(None, description="是否启用")
    
    def to_config_dict(self, current_config: dict[str, Any] | None = None) -> dict[str, Any]:
        """转换为配置字典"""
        config = current_config.copy() if current_config else {"enabled": True, "mappings": []}
        
        if self.mappings is not None:
            config["mappings"] = [{"model_id": m.model_id, "codes": m.codes} for m in self.mappings]
        
        if self.enabled is not None:
            config["enabled"] = self.enabled
        
        return config


class FactorConfigSingleCreate(BaseModel):
    """创建单个因子配置映射请求（向后兼容）"""

    factor_id: int = Field(..., description="因子ID")
    model_id: int | None = Field(None, description="模型ID（None表示使用默认算法）")
    codes: list[str] | None = Field(None, description="股票代码列表（逗号分隔），None表示所有股票")
    enabled: bool = Field(True, description="是否启用")

    class Config:
        protected_namespaces = ()


class FactorConfigSingleUpdate(BaseModel):
    """更新单个因子配置请求（向后兼容）"""

    model_id: int | None = Field(None, description="模型ID")
    codes: list[str] | None = Field(None, description="股票代码列表")
    enabled: bool | None = Field(None, description="是否启用")

    class Config:
        protected_namespaces = ()


class FactorConfigResponse(BaseModel):
    """因子配置响应"""

    factor_id: int = Field(..., description="因子ID（主键）")
    config: dict[str, Any] = Field(..., description="因子配置，格式：{\"enabled\": bool, \"mappings\": [{\"model_id\": int, \"codes\": list[str]|None}, ...]}")
    enabled: bool = Field(..., description="是否启用")
    created_by: str | None = Field(None, description="创建人")
    created_at: datetime = Field(..., description="创建时间")
    updated_by: str | None = Field(None, description="修改人")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
        protected_namespaces = ()

    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应"""
        data = {
            "factor_id": obj.factor_id,
            "config": obj.get_config(),
            "enabled": obj.enabled,
            "created_by": getattr(obj, "created_by", None),
            "created_at": obj.created_at,
            "updated_by": getattr(obj, "updated_by", None),
            "updated_at": obj.updated_at,
        }
        return cls(**data)


class FactorConfigListResponse(BaseModel):
    """因子配置列表响应"""

    items: list[FactorConfigResponse] = Field(..., description="因子配置列表")
    total: int = Field(..., description="总数")


class FactorConfigGroupedResponse(BaseModel):
    """因子配置分组响应（按factor_id分组）"""

    factor_id: int = Field(..., description="因子ID")
    enabled: bool = Field(..., description="是否启用")
    mappings: list[FactorConfigResponse] = Field(..., description="该因子的所有配置映射")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class FactorConfigGroupedListResponse(BaseModel):
    """因子配置分组列表响应"""

    items: list[FactorConfigGroupedResponse] = Field(..., description="因子配置分组列表")
    total: int = Field(..., description="总数")


# ==================== 因子计算 Schema ====================

class FactorCalculationRequest(BaseModel):
    """因子计算请求"""

    factor_id: int | None = Field(None, description="因子ID（None表示计算所有启用的因子）")
    codes: list[str] | None = Field(None, description="股票代码列表（None表示使用配置中的codes）")
    start_date: date | None = Field(None, description="开始日期（可选，参考日线数据处理逻辑：都不提供则使用最后一个交易日；部分提供时start_date默认2025-01-01）")
    end_date: date | None = Field(None, description="结束日期（可选，参考日线数据处理逻辑：都不提供则使用最后一个交易日；部分提供时end_date默认最后一个交易日）")


class FactorCalculationResponse(BaseModel):
    """因子计算响应"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    calculated_count: int = Field(0, description="计算的股票数量")
    failed_count: int = Field(0, description="失败的股票数量")
    details: list[dict[str, Any]] = Field(default_factory=list, description="详细信息")


# ==================== 因子结果 Schema ====================

class FactorResultItem(BaseModel):
    """因子结果项"""

    id: int | None
    trade_date: date
    factor_value: float | None
    created_at: datetime | None

    class Config:
        from_attributes = True


class FactorResultResponse(BaseModel):
    """因子结果响应"""

    code: str = Field(..., description="股票代码")
    factor_name: str = Field(..., description="因子名称")
    items: list[FactorResultItem] = Field(..., description="因子结果列表")
    total: int = Field(..., description="总数")


class FactorResultQueryRequest(BaseModel):
    """因子结果查询请求"""

    code: str = Field(..., description="股票代码")
    factor_name: str | None = Field(None, description="因子名称（None表示查询所有）")
    start_date: date | None = Field(None, description="开始日期")
    end_date: date | None = Field(None, description="结束日期")

