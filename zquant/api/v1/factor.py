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
因子管理API
"""

from datetime import date, datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from zquant.api.deps import get_current_active_user
from zquant.core.exceptions import NotFoundError
from zquant.core.permissions import is_admin
from zquant.database import get_db
from zquant.models.user import User
from zquant.schemas.factor import (
    FactorCalculationRequest,
    FactorCalculationResponse,
    FactorConfigCreate,
    FactorConfigGroupedListResponse,
    FactorConfigGroupedResponse,
    FactorConfigListResponse,
    FactorConfigResponse,
    FactorConfigSingleCreate,
    FactorConfigSingleUpdate,
    FactorConfigUpdate,
    FactorDefinitionCreate,
    FactorDefinitionListResponse,
    FactorDefinitionResponse,
    FactorDefinitionUpdate,
    FactorModelCreate,
    FactorModelListResponse,
    FactorModelResponse,
    FactorModelUpdate,
    FactorResultItem,
    FactorResultQueryRequest,
    FactorResultResponse,
)
from zquant.services.factor import FactorService
from zquant.services.factor_calculation import FactorCalculationService

router = APIRouter()


# ==================== 因子定义管理 ====================

@router.post("/definitions", response_model=FactorDefinitionResponse, status_code=status.HTTP_201_CREATED, summary="创建因子定义")
def create_factor_definition(
    factor_data: FactorDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建因子定义（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        factor_def = FactorService.create_factor_definition(
            db=db,
            factor_name=factor_data.factor_name,
            cn_name=factor_data.cn_name,
            en_name=factor_data.en_name,
            column_name=factor_data.column_name,
            description=factor_data.description,
            enabled=factor_data.enabled,
            factor_config=factor_data.factor_config,
        )
        return FactorDefinitionResponse.from_orm(factor_def)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建因子定义失败: {e!s}")


@router.get("/definitions", response_model=FactorDefinitionListResponse, summary="获取因子定义列表")
def list_factor_definitions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    enabled: bool | None = Query(None),
    order_by: str | None = Query(None, description="排序字段：id, factor_name, cn_name, created_at, updated_at"),
    order: str = Query("desc", description="排序方向：asc 或 desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子定义列表"""
    try:
        items, total = FactorService.list_factor_definitions(
            db=db, skip=skip, limit=limit, enabled=enabled, order_by=order_by, order=order
        )
        return FactorDefinitionListResponse(
            items=[FactorDefinitionResponse.from_orm(item) for item in items], total=total
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子定义列表失败: {e!s}")


@router.get("/definitions/{factor_id}", response_model=FactorDefinitionResponse, summary="获取因子定义")
def get_factor_definition(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子定义"""
    try:
        factor_def = FactorService.get_factor_definition(db, factor_id)
        return FactorDefinitionResponse.from_orm(factor_def)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子定义失败: {e!s}")


@router.put("/definitions/{factor_id}", response_model=FactorDefinitionResponse, summary="更新因子定义")
def update_factor_definition(
    factor_id: int,
    factor_data: FactorDefinitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新因子定义（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        factor_def = FactorService.update_factor_definition(
            db=db,
            factor_id=factor_id,
            cn_name=factor_data.cn_name,
            en_name=factor_data.en_name,
            column_name=factor_data.column_name,
            description=factor_data.description,
            enabled=factor_data.enabled,
            factor_config=factor_data.factor_config,
        )
        return FactorDefinitionResponse.from_orm(factor_def)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"更新因子定义失败: {e!s}")


@router.delete("/definitions/{factor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除因子定义")
def delete_factor_definition(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除因子定义（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        FactorService.delete_factor_definition(db, factor_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"删除因子定义失败: {e!s}")


# ==================== 因子模型管理 ====================

@router.post("/models", response_model=FactorModelResponse, status_code=status.HTTP_201_CREATED, summary="创建因子模型")
def create_factor_model(
    model_data: FactorModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建因子模型（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        model = FactorService.create_factor_model(
            db=db,
            factor_id=model_data.factor_id,
            model_name=model_data.model_name,
            model_code=model_data.model_code,
            config_json=model_data.config_json,
            is_default=model_data.is_default,
            enabled=model_data.enabled,
        )
        return FactorModelResponse.from_orm(model)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建因子模型失败: {e!s}")


@router.get("/models", response_model=FactorModelListResponse, summary="获取因子模型列表")
def list_factor_models(
    factor_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    enabled: bool | None = Query(None),
    order_by: str | None = Query(None, description="排序字段：id, model_name, model_code, created_at, updated_at"),
    order: str = Query("desc", description="排序方向：asc 或 desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子模型列表"""
    try:
        items, total = FactorService.list_factor_models(
            db=db, factor_id=factor_id, skip=skip, limit=limit, enabled=enabled, order_by=order_by, order=order
        )
        return FactorModelListResponse(items=[FactorModelResponse.from_orm(item) for item in items], total=total)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子模型列表失败: {e!s}")


@router.get("/models/{model_id}", response_model=FactorModelResponse, summary="获取因子模型")
def get_factor_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子模型"""
    try:
        model = FactorService.get_factor_model(db, model_id)
        return FactorModelResponse.from_orm(model)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子模型失败: {e!s}")


@router.put("/models/{model_id}", response_model=FactorModelResponse, summary="更新因子模型")
def update_factor_model(
    model_id: int,
    model_data: FactorModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新因子模型（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        model = FactorService.update_factor_model(
            db=db,
            model_id=model_id,
            model_name=model_data.model_name,
            model_code=model_data.model_code,
            config_json=model_data.config_json,
            is_default=model_data.is_default,
            enabled=model_data.enabled,
        )
        return FactorModelResponse.from_orm(model)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"更新因子模型失败: {e!s}")


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除因子模型")
def delete_factor_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除因子模型（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        FactorService.delete_factor_model(db, model_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"删除因子模型失败: {e!s}")


# ==================== 因子配置管理（新表结构，标准RESTful接口） ====================

@router.post("/configs", response_model=FactorConfigResponse, status_code=status.HTTP_201_CREATED, summary="创建因子配置")
def create_factor_config(
    config_data: FactorConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建因子配置（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        config = FactorService.create_factor_config(
            db=db,
            factor_id=config_data.factor_id,
            config=config_data.to_config_dict(),
        )
        return FactorConfigResponse.from_orm(config)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建因子配置失败: {e!s}")


@router.get("/configs", response_model=FactorConfigListResponse, summary="获取因子配置列表")
def list_factor_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    enabled: bool | None = Query(None),
    order_by: str | None = Query(None, description="排序字段：factor_id, created_at, updated_at"),
    order: str = Query("desc", description="排序方向：asc 或 desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子配置列表"""
    try:
        items, total = FactorService.list_factor_configs(
            db=db, skip=skip, limit=limit, enabled=enabled, order_by=order_by, order=order
        )
        return FactorConfigListResponse(
            items=[FactorConfigResponse.from_orm(item) for item in items], total=total
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子配置列表失败: {e!s}")


@router.get("/configs/{factor_id}", response_model=FactorConfigResponse, summary="获取因子配置")
def get_factor_config_by_id(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子配置"""
    try:
        config = FactorService.get_factor_config_by_factor_id(db, factor_id)
        return FactorConfigResponse.from_orm(config)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子配置失败: {e!s}")


@router.put("/configs/{factor_id}", response_model=FactorConfigResponse, summary="更新因子配置")
def update_factor_config_by_id(
    factor_id: int,
    config_data: FactorConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新因子配置（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        # 获取当前配置
        current_config_obj = FactorService.get_factor_config_by_factor_id(db, factor_id)
        current_config = current_config_obj.get_config()
        
        # 转换为新的配置字典
        new_config = config_data.to_config_dict(current_config)
        
        config = FactorService.update_factor_config_by_factor_id(
            db=db,
            factor_id=factor_id,
            config=new_config,
            updated_by=current_user.username,
        )
        return FactorConfigResponse.from_orm(config)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"更新因子配置失败: {e!s}")


@router.delete("/configs/{factor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除因子配置")
def delete_factor_config_by_id(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除因子配置（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        FactorService.delete_factor_config_by_factor_id(db, factor_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"删除因子配置失败: {e!s}")


# ==================== 因子配置管理（基于JSON，已废弃，向后兼容） ====================

@router.get("/definitions/{factor_id}/config", response_model=dict, summary="获取因子配置（已废弃）")
def get_factor_config(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取因子配置（已废弃）
    
    注意：此接口已废弃，请使用 GET /api/v1/factor/configs/{factor_id} 代替
    """
    try:
        # 尝试从新表获取
        try:
            config_obj = FactorService.get_factor_config_by_factor_id(db, factor_id)
            return config_obj.get_config()
        except NotFoundError:
            # 如果新表不存在，从旧表获取（向后兼容）
            config = FactorService.get_factor_config(db, factor_id)
            return config
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子配置失败: {e!s}")


@router.put("/definitions/{factor_id}/config", response_model=dict, summary="更新因子配置（已废弃）")
def update_factor_config(
    factor_id: int,
    factor_config: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新因子配置（已废弃）
    
    注意：此接口已废弃，请使用 PUT /api/v1/factor/configs/{factor_id} 代替
    """
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        # 尝试更新新表
        try:
            config_obj = FactorService.get_factor_config_by_factor_id(db, factor_id)
            config_obj = FactorService.update_factor_config_by_factor_id(
                db, factor_id, factor_config, updated_by=current_user.username
            )
            return config_obj.get_config()
        except NotFoundError:
            # 如果新表不存在，更新旧表（向后兼容）
            factor_def = FactorService.update_factor_config(db, factor_id, factor_config)
            return factor_def.get_factor_config()
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"更新因子配置失败: {e!s}")


@router.delete("/definitions/{factor_id}/config", status_code=status.HTTP_204_NO_CONTENT, summary="删除因子配置（已废弃）")
def delete_factor_config(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除因子配置（已废弃）
    
    注意：此接口已废弃，请使用 DELETE /api/v1/factor/configs/{factor_id} 代替
    """
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        # 尝试删除新表
        try:
            FactorService.delete_factor_config_by_factor_id(db, factor_id)
        except NotFoundError:
            # 如果新表不存在，清空旧表配置（向后兼容）
            factor_def = FactorService.get_factor_definition(db, factor_id)
            factor_def.set_factor_config({})
            db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"删除因子配置失败: {e!s}")


# ==================== 因子配置管理（已废弃，仅用于向后兼容） ====================

@router.post("/configs", response_model=FactorConfigGroupedResponse, status_code=status.HTTP_201_CREATED, summary="创建因子配置（支持多映射）（已废弃）")
def create_factor_config(
    config_data: FactorConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建因子配置（支持多映射）（已废弃）
    
    注意：此接口已废弃，请使用 PUT /definitions/{factor_id}/config 代替
    """
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        # 转换映射数据格式为JSON配置格式
        factor_config = {
            "enabled": config_data.enabled,
            "mappings": [{"model_id": m.model_id, "codes": m.codes} for m in config_data.mappings]
        }
        
        # 使用新的update_factor_config方法
        factor_def = FactorService.update_factor_config(
            db=db,
            factor_id=config_data.factor_id,
            factor_config=factor_config,
        )
        
        config = factor_def.get_factor_config()
        mappings = [FactorConfigResponse(
            id=0,  # 占位符，实际不存在
            factor_id=config_data.factor_id,
            model_id=m.get("model_id"),
            codes=m.get("codes"),
            enabled=config.get("enabled", True),
            created_at=factor_def.created_at,
            updated_at=factor_def.updated_at,
        ) for m in config.get("mappings", [])]
        
        return FactorConfigGroupedResponse(
            factor_id=config_data.factor_id,
            enabled=config.get("enabled", True),
            mappings=mappings,
            created_at=factor_def.created_at,
            updated_at=factor_def.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建因子配置失败: {e!s}")


@router.get("/configs/grouped", response_model=FactorConfigGroupedListResponse, summary="获取因子配置列表（按因子分组）")
def list_factor_configs_grouped(
    enabled: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子配置列表（按因子ID分组，每个因子包含所有映射）"""
    try:
        # 获取所有配置
        all_configs, _ = FactorService.list_factor_configs(db=db, enabled=enabled, limit=10000)
        
        # 按factor_id分组
        grouped: dict[int, list] = {}
        for config in all_configs:
            if config.factor_id not in grouped:
                grouped[config.factor_id] = []
            grouped[config.factor_id].append(config)
        
        # 构建响应
        items = []
        for factor_id, configs in grouped.items():
            if configs:
                items.append(FactorConfigGroupedResponse(
                    factor_id=factor_id,
                    enabled=configs[0].enabled,
                    mappings=[FactorConfigResponse.from_orm(c) for c in configs],
                    created_at=min(c.created_at for c in configs),
                    updated_at=max(c.updated_at for c in configs),
                ))
        
        return FactorConfigGroupedListResponse(items=items, total=len(items))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子配置列表失败: {e!s}")


@router.put("/configs/by-factor/{factor_id}", response_model=FactorConfigGroupedResponse, summary="更新因子配置（按因子ID，支持多映射）（已废弃）")
def update_factor_config_by_factor(
    factor_id: int,
    config_data: FactorConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新因子配置（按因子ID，支持批量更新映射）（已废弃）
    
    注意：此接口已废弃，请使用 PUT /definitions/{factor_id}/config 代替
    """
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        # 获取当前配置
        current_config = FactorService.get_factor_config(db, factor_id)
        
        # 如果提供了mappings，更新mappings
        if config_data.mappings is not None:
            current_config["mappings"] = [{"model_id": m.model_id, "codes": m.codes} for m in config_data.mappings]
        
        # 如果提供了enabled，更新enabled
        if config_data.enabled is not None:
            current_config["enabled"] = config_data.enabled
        
        # 使用新的update_factor_config方法
        factor_def = FactorService.update_factor_config(
            db=db,
            factor_id=factor_id,
            factor_config=current_config,
        )
        
        config = factor_def.get_factor_config()
        mappings = [FactorConfigResponse(
            id=0,  # 占位符，实际不存在
            factor_id=factor_id,
            model_id=m.get("model_id"),
            codes=m.get("codes"),
            enabled=config.get("enabled", True),
            created_at=factor_def.created_at,
            updated_at=factor_def.updated_at,
        ) for m in config.get("mappings", [])]
        
        return FactorConfigGroupedResponse(
            factor_id=factor_id,
            enabled=config.get("enabled", True),
            mappings=mappings,
            created_at=factor_def.created_at,
            updated_at=factor_def.updated_at,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"更新因子配置失败: {e!s}")


@router.delete("/configs/by-factor/{factor_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除因子配置（按因子ID，删除该因子的所有配置）（已废弃）")
def delete_factor_config_by_factor(
    factor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除因子配置（按因子ID，删除该因子的所有配置）（已废弃）
    
    注意：此接口已废弃，请使用 DELETE /definitions/{factor_id}/config 代替
    """
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        # 使用新的方法删除配置
        factor_def = FactorService.get_factor_definition(db, factor_id)
        factor_def.set_factor_config({})
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"删除因子配置失败: {e!s}")


@router.get("/configs", response_model=FactorConfigListResponse, summary="获取因子配置列表（扁平列表）")
def list_factor_configs(
    factor_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    enabled: bool | None = Query(None),
    order_by: str | None = Query(None, description="排序字段：id, factor_id, model_id, created_at, updated_at"),
    order: str = Query("desc", description="排序方向：asc 或 desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取因子配置列表（扁平列表，每个映射一条记录）"""
    try:
        items, total = FactorService.list_factor_configs(
            db=db, factor_id=factor_id, skip=skip, limit=limit, enabled=enabled, order_by=order_by, order=order
        )
        return FactorConfigListResponse(items=[FactorConfigResponse.from_orm(item) for item in items], total=total)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取因子配置列表失败: {e!s}")


@router.put("/configs", response_model=FactorConfigResponse, summary="更新单个因子配置（使用查询参数）")
def update_factor_config(
    config_id: int = Query(..., description="配置ID"),
    config_data: FactorConfigSingleUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """更新单个因子配置（使用查询参数，避免路径参数冲突）（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        config = FactorService.update_factor_config(
            db=db,
            config_id=config_id,
            model_id=config_data.model_id,
            codes=config_data.codes,
            enabled=config_data.enabled,
        )
        return FactorConfigResponse.from_orm(config)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"更新因子配置失败: {e!s}")


@router.delete("/configs", status_code=status.HTTP_204_NO_CONTENT, summary="删除因子配置")
def delete_factor_config(
    config_id: int = Query(..., description="配置ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """删除因子配置（使用查询参数，避免路径参数冲突）（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        FactorService.delete_factor_config(db, config_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"删除因子配置失败: {e!s}")


# ==================== 因子计算 ====================

@router.post("/calculate", response_model=FactorCalculationResponse, summary="手动触发因子计算")
def calculate_factor(
    request: FactorCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """手动触发因子计算（需要管理员权限）"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    try:
        # 从 current_user 构建 extra_info
        extra_info = {"created_by": current_user.username, "updated_by": current_user.username}
        
        result = FactorCalculationService.calculate_factor(
            db=db,
            factor_id=request.factor_id,
            codes=request.codes,
            start_date=request.start_date,
            end_date=request.end_date,
            extra_info=extra_info,
        )
        return FactorCalculationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"因子计算失败: {e!s}")


# ==================== 因子结果查询 ====================

@router.post("/results", response_model=FactorResultResponse, summary="查询因子计算结果")
def get_factor_results(
    request: FactorResultQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """查询因子计算结果"""
    try:
        items = FactorCalculationService.get_factor_results(
            db=db,
            code=request.code,
            factor_name=request.factor_name,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        # 如果没有指定因子名称，返回所有因子
        if not request.factor_name:
            return FactorResultResponse(
                code=request.code,
                factor_name="all",
                items=[FactorResultItem(**item) for item in items],
                total=len(items),
            )

        # 获取因子定义，确定列名
        factor_def = FactorService.get_factor_definition_by_name(db, request.factor_name)
        if not factor_def:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"因子定义不存在: {request.factor_name}")

        # 过滤出该因子的数据
        column_name = factor_def.column_name
        filtered_items = []
        for item in items:
            if column_name in item:
                filtered_items.append(
                    {
                        "id": item.get("id"),
                        "trade_date": date.fromisoformat(item["trade_date"]) if isinstance(item["trade_date"], str) else item["trade_date"],
                        "factor_value": item.get(column_name),
                        "created_at": item.get("created_at"),
                    }
                )

        return FactorResultResponse(
            code=request.code,
            factor_name=request.factor_name,
            items=[FactorResultItem(**item) for item in filtered_items],
            total=len(filtered_items),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"查询因子结果失败: {e!s}")

