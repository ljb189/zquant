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
因子相关数据库模型
"""

import json
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from zquant.database import Base


class FactorDefinition(Base):
    """因子定义表"""

    __tablename__ = "zq_quant_factor_definitions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factor_name = Column(String(100), nullable=False, unique=True, index=True, comment="因子名称（唯一标识）")
    cn_name = Column(String(100), nullable=False, comment="中文简称")
    en_name = Column(String(100), nullable=True, comment="英文简称")
    column_name = Column(String(100), nullable=False, comment="因子表数据列名")
    description = Column(Text, nullable=True, comment="因子详细描述")
    enabled = Column(Boolean, default=True, nullable=False, index=True, comment="是否启用")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    models = relationship("FactorModel", back_populates="factor", cascade="all, delete-orphan")
    config = relationship("FactorConfig", back_populates="factor", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_factor_name", "factor_name"),
        Index("idx_enabled", "enabled"),
    )

    def get_factor_config(self) -> dict:
        """
        获取因子配置字典
        
        Returns:
            配置字典，格式：{"enabled": bool, "mappings": [{"model_id": int, "codes": list[str]|None}, ...]}
        """
        if self.config:
            return self.config.get_config()
        return {"enabled": True, "mappings": []}

    def set_factor_config(self, config: dict):
        """
        设置因子配置
        
        Args:
            config: 配置字典，格式：{"enabled": bool, "mappings": [{"model_id": int, "codes": list[str]|None}, ...]}
        """
        if config:
            # 验证配置格式
            if not isinstance(config, dict):
                raise ValueError("配置必须是字典类型")
            if "mappings" not in config:
                config["mappings"] = []
            if "enabled" not in config:
                config["enabled"] = True
            
            # 验证mappings格式
            mappings = config.get("mappings", [])
            if not isinstance(mappings, list):
                raise ValueError("mappings必须是列表类型")
            
            for mapping in mappings:
                if not isinstance(mapping, dict):
                    raise ValueError("每个mapping必须是字典类型")
                if "model_id" not in mapping:
                    raise ValueError("每个mapping必须包含model_id字段")
                if "codes" in mapping and mapping["codes"] is not None and not isinstance(mapping["codes"], list):
                    raise ValueError("codes必须是列表类型或None")
            
            # 创建或更新 FactorConfig 关系对象
            if not self.config:
                from zquant.models.factor import FactorConfig
                self.config = FactorConfig(factor_id=self.id)
            self.config.set_config(config)
        else:
            # 如果 config 为空，删除配置对象
            if self.config:
                # 注意：这里不直接删除，而是清空配置，让调用方决定是否删除
                self.config.set_config({"enabled": True, "mappings": []})


class FactorModel(Base):
    """因子模型表"""

    __tablename__ = "zq_quant_factor_models"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    factor_id = Column(Integer, ForeignKey("zq_quant_factor_definitions.id"), nullable=False, index=True, comment="因子ID")
    model_name = Column(String(100), nullable=False, comment="模型名称")
    model_code = Column(String(50), nullable=False, comment="模型代码（用于识别计算器类型）")
    config_json = Column(Text, nullable=True, comment="模型配置（JSON格式）")
    is_default = Column(Boolean, default=False, nullable=False, index=True, comment="是否默认算法")
    enabled = Column(Boolean, default=True, nullable=False, index=True, comment="是否启用")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    factor = relationship("FactorDefinition", back_populates="models")

    __table_args__ = (
        Index("idx_factor_id", "factor_id"),
        Index("idx_model_code", "model_code"),
        Index("idx_is_default", "is_default"),
        Index("idx_enabled", "enabled"),
    )

    def get_config(self) -> dict:
        """获取模型配置字典"""
        if self.config_json:
            return json.loads(self.config_json)
        return {}

    def set_config(self, config: dict):
        """设置模型配置"""
        self.config_json = json.dumps(config) if config else None


class FactorConfig(Base):
    """
    因子配置表
    
    以factor_id为主键，每个因子对应一条配置记录。
    配置以JSON格式存储在config_json字段中。
    """

    __tablename__ = "zq_quant_factor_configs"

    factor_id = Column(Integer, ForeignKey("zq_quant_factor_definitions.id"), primary_key=True, index=True, comment="因子ID（主键）")
    config_json = Column(Text, nullable=True, comment="因子配置（JSON格式）：{\"enabled\": true, \"mappings\": [{\"model_id\": 1, \"codes\": [...]}]}")
    enabled = Column(Boolean, default=True, nullable=False, index=True, comment="是否启用")
    created_by = Column(String(50), nullable=True, info={"name": "创建人"}, comment="创建人")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_by = Column(String(50), nullable=True, info={"name": "修改人"}, comment="修改人")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    factor = relationship("FactorDefinition", back_populates="config")

    __table_args__ = (
        Index("idx_factor_id", "factor_id"),
        Index("idx_enabled", "enabled"),
    )

    def get_config(self) -> dict:
        """
        获取因子配置字典
        
        Returns:
            配置字典，格式：{"enabled": bool, "mappings": [{"model_id": int, "codes": list[str]|None}, ...]}
        """
        if self.config_json:
            try:
                return json.loads(self.config_json)
            except (json.JSONDecodeError, TypeError):
                return {"enabled": True, "mappings": []}
        return {"enabled": True, "mappings": []}

    def set_config(self, config: dict):
        """
        设置因子配置
        
        Args:
            config: 配置字典，格式：{"enabled": bool, "mappings": [{"model_id": int, "codes": list[str]|None}, ...]}
        """
        if config:
            # 验证配置格式
            if not isinstance(config, dict):
                raise ValueError("配置必须是字典类型")
            if "mappings" not in config:
                config["mappings"] = []
            if "enabled" not in config:
                config["enabled"] = True
            
            # 验证mappings格式
            mappings = config.get("mappings", [])
            if not isinstance(mappings, list):
                raise ValueError("mappings必须是列表类型")
            
            for mapping in mappings:
                if not isinstance(mapping, dict):
                    raise ValueError("每个mapping必须是字典类型")
                if "model_id" not in mapping:
                    raise ValueError("每个mapping必须包含model_id字段")
                if "codes" in mapping and mapping["codes"] is not None and not isinstance(mapping["codes"], list):
                    raise ValueError("codes必须是列表类型或None")
            
            self.config_json = json.dumps(config, ensure_ascii=False)
            # 同步enabled字段
            self.enabled = config.get("enabled", True)
        else:
            self.config_json = None
            self.enabled = True

    def get_codes_list(self) -> list[str]:
        """
        获取配置中所有mappings的股票代码列表
        
        Returns:
            股票代码列表，如果所有mappings的codes都是None或空列表，返回空列表（表示默认配置）
        """
        config = self.get_config()
        mappings = config.get("mappings", [])
        
        all_codes = []
        for mapping in mappings:
            codes = mapping.get("codes")
            if codes and isinstance(codes, list):
                all_codes.extend(codes)
        
        return all_codes

    def set_codes_list(self, codes: list[str]):
        """
        设置配置中的codes列表（兼容旧代码，已废弃）
        
        注意：此方法已废弃。因子配置现在使用mappings格式，每个mapping可以有不同的codes。
        请使用set_config方法代替。
        
        Args:
            codes: 股票代码列表
        """
        config = self.get_config()
        mappings = config.get("mappings", [])
        
        # 如果mappings为空，创建一个默认mapping
        if not mappings:
            # 需要model_id，但这里没有，所以创建一个空的mapping
            # 注意：这可能会导致问题，因为mapping需要model_id
            mappings = [{"model_id": None, "codes": codes}]
        else:
            # 更新第一个mapping的codes
            if mappings:
                mappings[0]["codes"] = codes if codes else None
        
        config["mappings"] = mappings
        self.set_config(config)

