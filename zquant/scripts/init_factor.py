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
因子系统初始化脚本

功能：
1. 创建因子相关表（包括新的FactorConfig表，以factor_id为主键）
2. 初始化换手率因子定义和模型
3. 创建示例因子配置（使用新的FactorConfig表）
4. 支持从FactorDefinition.factor_config_json迁移数据到新表

注意：
- FactorConfig表以factor_id为主键，每个因子对应一条配置记录
- 配置以JSON格式存储在config_json字段中
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
script_dir = Path(__file__).resolve().parent  # zquant/scripts
zquant_dir = script_dir.parent  # zquant 目录
project_root = zquant_dir.parent  # 项目根目录（包含 zquant 目录的目录）
sys.path.insert(0, str(project_root))

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from zquant.database import SessionLocal, engine
from zquant.models.factor import FactorConfig, FactorDefinition, FactorModel
from zquant.services.factor import FactorService


def create_tables():
    """创建因子相关表"""
    logger.info("开始创建因子相关数据库表...")
    try:
        with engine.begin() as conn:  # 使用 begin() 自动管理事务
            # 创建因子定义表
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS zq_quant_factor_definitions (
                    id INTEGER AUTO_INCREMENT PRIMARY KEY,
                    factor_name VARCHAR(100) NOT NULL UNIQUE,
                    cn_name VARCHAR(100) NOT NULL,
                    en_name VARCHAR(100),
                    column_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_factor_name (factor_name),
                    INDEX idx_enabled (enabled)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
            )

            # 创建因子模型表
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS zq_quant_factor_models (
                    id INTEGER AUTO_INCREMENT PRIMARY KEY,
                    factor_id INTEGER NOT NULL,
                    model_name VARCHAR(100) NOT NULL,
                    model_code VARCHAR(50) NOT NULL,
                    config_json TEXT,
                    is_default BOOLEAN NOT NULL DEFAULT FALSE,
                    enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_factor_id (factor_id),
                    INDEX idx_model_code (model_code),
                    INDEX idx_is_default (is_default),
                    INDEX idx_enabled (enabled),
                    FOREIGN KEY (factor_id) REFERENCES zq_quant_factor_definitions(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
            )

            # 创建因子配置表（以factor_id为主键）
            conn.execute(
                text("""
                CREATE TABLE IF NOT EXISTS zq_quant_factor_configs (
                    factor_id INTEGER NOT NULL PRIMARY KEY,
                    config_json TEXT COMMENT '因子配置（JSON格式）：{"enabled": true, "mappings": [{"model_id": 1, "codes": [...]}]}',
                    enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_factor_id (factor_id),
                    INDEX idx_enabled (enabled),
                    FOREIGN KEY (factor_id) REFERENCES zq_quant_factor_definitions(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
            )

            # 检查并添加缺失的列（用于表已存在但结构不完整的情况）
            from sqlalchemy import inspect as sql_inspect
            inspector = sql_inspect(engine)
            
            # 检查因子定义表
            if "zq_quant_factor_definitions" in inspector.get_table_names():
                existing_columns = [col["name"] for col in inspector.get_columns("zq_quant_factor_definitions")]
                
                # 删除不需要的字段（如果存在）
                if "factor_type" in existing_columns:
                    logger.info("表 zq_quant_factor_definitions 包含不需要的 factor_type 列，正在删除...")
                    try:
                        # 先删除可能存在的索引
                        try:
                            conn.execute(text("ALTER TABLE zq_quant_factor_definitions DROP INDEX idx_factor_type"))
                        except:
                            pass
                        conn.execute(text("ALTER TABLE zq_quant_factor_definitions DROP COLUMN factor_type"))
                        logger.info("已删除 factor_type 列")
                    except Exception as e:
                        logger.warning(f"删除 factor_type 列失败: {e}")
                
                # 添加缺失的 enabled 列
                if "enabled" not in existing_columns:
                    logger.info("表 zq_quant_factor_definitions 缺少 enabled 列，正在添加...")
                    try:
                        conn.execute(text("ALTER TABLE zq_quant_factor_definitions ADD COLUMN enabled BOOLEAN NOT NULL DEFAULT TRUE"))
                        # 检查索引是否存在
                        existing_indexes = [idx["name"] for idx in inspector.get_indexes("zq_quant_factor_definitions")]
                        if "idx_enabled" not in existing_indexes:
                            conn.execute(text("ALTER TABLE zq_quant_factor_definitions ADD INDEX idx_enabled (enabled)"))
                        logger.info("已添加 enabled 列和索引")
                    except Exception as e:
                        logger.warning(f"添加 enabled 列失败（可能已存在）: {e}")
            
            # 检查因子模型表
            if "zq_quant_factor_models" in inspector.get_table_names():
                existing_columns = [col["name"] for col in inspector.get_columns("zq_quant_factor_models")]
                
                # 添加缺失的 enabled 列
                if "enabled" not in existing_columns:
                    logger.info("表 zq_quant_factor_models 缺少 enabled 列，正在添加...")
                    try:
                        conn.execute(text("ALTER TABLE zq_quant_factor_models ADD COLUMN enabled BOOLEAN NOT NULL DEFAULT TRUE"))
                        existing_indexes = [idx["name"] for idx in inspector.get_indexes("zq_quant_factor_models")]
                        if "idx_enabled" not in existing_indexes:
                            conn.execute(text("ALTER TABLE zq_quant_factor_models ADD INDEX idx_enabled (enabled)"))
                        logger.info("已添加 enabled 列和索引")
                    except Exception as e:
                        logger.warning(f"添加 enabled 列失败（可能已存在）: {e}")
                
                # 添加缺失的 is_default 列
                if "is_default" not in existing_columns:
                    logger.info("表 zq_quant_factor_models 缺少 is_default 列，正在添加...")
                    try:
                        conn.execute(text("ALTER TABLE zq_quant_factor_models ADD COLUMN is_default BOOLEAN NOT NULL DEFAULT FALSE"))
                        existing_indexes = [idx["name"] for idx in inspector.get_indexes("zq_quant_factor_models")]
                        if "idx_is_default" not in existing_indexes:
                            conn.execute(text("ALTER TABLE zq_quant_factor_models ADD INDEX idx_is_default (is_default)"))
                        logger.info("已添加 is_default 列和索引")
                    except Exception as e:
                        logger.warning(f"添加 is_default 列失败（可能已存在）: {e}")
                
                # 添加缺失的 config_json 列
                if "config_json" not in existing_columns:
                    logger.info("表 zq_quant_factor_models 缺少 config_json 列，正在添加...")
                    try:
                        conn.execute(text("ALTER TABLE zq_quant_factor_models ADD COLUMN config_json TEXT"))
                        logger.info("已添加 config_json 列")
                    except Exception as e:
                        logger.warning(f"添加 config_json 列失败（可能已存在）: {e}")
                
                # 添加缺失的 created_at 和 updated_at 列
                if "created_at" not in existing_columns:
                    logger.info("表 zq_quant_factor_models 缺少 created_at 列，正在添加...")
                    try:
                        conn.execute(text("ALTER TABLE zq_quant_factor_models ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
                        logger.info("已添加 created_at 列")
                    except Exception as e:
                        logger.warning(f"添加 created_at 列失败（可能已存在）: {e}")
                
                if "updated_at" not in existing_columns:
                    logger.info("表 zq_quant_factor_models 缺少 updated_at 列，正在添加...")
                    try:
                        conn.execute(text("ALTER TABLE zq_quant_factor_models ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
                        logger.info("已添加 updated_at 列")
                    except Exception as e:
                        logger.warning(f"添加 updated_at 列失败（可能已存在）: {e}")
            
            # 检查因子配置表
            if "zq_quant_factor_configs" in inspector.get_table_names():
                existing_columns = [col["name"] for col in inspector.get_columns("zq_quant_factor_configs")]
                
                # 检查是否是旧表结构（有id列）
                if "id" in existing_columns:
                    logger.warning("检测到旧的 zq_quant_factor_configs 表结构（有id列），需要运行迁移脚本重构表结构")
                else:
                    # 新表结构，检查缺失的列
                    if "config_json" not in existing_columns:
                        logger.info("表 zq_quant_factor_configs 缺少 config_json 列，正在添加...")
                        try:
                            conn.execute(text("ALTER TABLE zq_quant_factor_configs ADD COLUMN config_json TEXT COMMENT '因子配置（JSON格式）'"))
                            logger.info("已添加 config_json 列")
                        except Exception as e:
                            logger.warning(f"添加 config_json 列失败（可能已存在）: {e}")
                    
                    if "enabled" not in existing_columns:
                        logger.info("表 zq_quant_factor_configs 缺少 enabled 列，正在添加...")
                        try:
                            conn.execute(text("ALTER TABLE zq_quant_factor_configs ADD COLUMN enabled BOOLEAN NOT NULL DEFAULT TRUE"))
                            existing_indexes = [idx["name"] for idx in inspector.get_indexes("zq_quant_factor_configs")]
                            if "idx_enabled" not in existing_indexes:
                                conn.execute(text("ALTER TABLE zq_quant_factor_configs ADD INDEX idx_enabled (enabled)"))
                            logger.info("已添加 enabled 列和索引")
                        except Exception as e:
                            logger.warning(f"添加 enabled 列失败（可能已存在）: {e}")

            # 使用 engine.begin() 时，事务会在 with 块结束时自动提交
            logger.info("因子相关表创建完成")
            return True
    except Exception as e:
        logger.error(f"创建因子相关表失败: {e}")
        return False


def create_turnover_rate_factor(force: bool = False):
    """创建换手率因子定义和模型"""
    logger.info("开始创建换手率因子...")

    db = SessionLocal()
    try:
        # 检查是否已存在
        existing = FactorService.get_factor_definition_by_name(db, "turnover_rate")
        if existing and not force:
            logger.info("换手率因子已存在，跳过创建（使用 --force 强制重新创建）")
            return True

        # 如果存在且需要强制重新创建，先删除
        if existing and force:
            logger.info("删除已存在的换手率因子...")
            FactorService.delete_factor_definition(db, existing.id)

        # 创建因子定义
        factor_def = FactorService.create_factor_definition(
            db=db,
            factor_name="turnover_rate",
            cn_name="换手率",
            en_name="Turnover Rate",
            column_name="turnover_rate",
            description="换手率因子，反映股票交易的活跃程度",
            enabled=True,
        )

        # 创建默认模型
        default_model = FactorService.create_factor_model(
            db=db,
            factor_id=factor_def.id,
            model_name="换手率计算模型（每日指标）",
            model_code="turnover_rate",
            config_json={"source": "daily_basic", "field": "turnover_rate"},
            is_default=True,
            enabled=True,
        )

        # 创建第二个换手率模型（移动平均）
        ma_model = FactorService.create_factor_model(
            db=db,
            factor_id=factor_def.id,
            model_name="换手率计算模型（移动平均）",
            model_code="turnover_rate_ma",
            config_json={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5},
            is_default=False,
            enabled=True,
        )

        logger.info(f"成功创建换手率因子: factor_id={factor_def.id}, default_model_id={default_model.id}, ma_model_id={ma_model.id}")
        return True

    except Exception as e:
        logger.error(f"创建换手率因子失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_example_config(force: bool = False):
    """创建示例因子配置（多映射配置示例，使用新的FactorConfig表）"""
    logger.info("开始创建示例因子配置...")

    db = SessionLocal()
    try:
        # 获取换手率因子
        factor_def = FactorService.get_factor_definition_by_name(db, "turnover_rate")
        if not factor_def:
            logger.warning("换手率因子不存在，跳过创建示例配置")
            return True

        # 检查是否已存在配置
        try:
            existing_config = FactorService.get_factor_config_by_factor_id(db, factor_def.id)
            if existing_config and not force:
                logger.info("示例因子配置已存在，跳过创建（使用 --force 强制重新创建）")
                return True
            
            # 如果存在且需要强制重新创建，先删除
            if existing_config and force:
                logger.info("删除已存在的因子配置...")
                FactorService.delete_factor_config_by_factor_id(db, factor_def.id)
        except Exception:
            # 配置不存在，继续创建
            pass

        # 获取换手率因子的所有模型
        models, _ = FactorService.list_factor_models(db, factor_id=factor_def.id, limit=10)
        default_model = next((m for m in models if m.is_default), None)
        ma_model = next((m for m in models if m.model_code == "turnover_rate_ma"), None)

        if not default_model:
            logger.warning("未找到默认换手率模型，跳过创建示例配置")
            return True

        if not ma_model:
            logger.warning("未找到移动平均换手率模型，将只创建默认配置")

        # 创建多映射配置
        mappings = [
            {
                "model_id": default_model.id,
                "codes": None,  # 默认配置，用于所有未指定的股票
            }
        ]

        # 如果存在移动平均模型，添加特定股票代码的配置
        if ma_model:
            mappings.append(
                {
                    "model_id": ma_model.id,
                    "codes": ["000001.SZ", "000002.SZ"],  # 特定股票使用移动平均模型
                }
            )

        # 使用新的create_factor_config方法创建配置
        factor_config = {
            "enabled": True,
            "mappings": mappings,
        }
        
        FactorService.create_factor_config(
            db=db,
            factor_id=factor_def.id,
            config=factor_config,
        )

        logger.info(f"成功创建示例因子配置: 共 {len(mappings)} 个映射")
        for i, mapping in enumerate(mappings, 1):
            codes_str = ", ".join(mapping["codes"]) if mapping["codes"] else "默认配置（所有股票）"
            logger.info(f"  映射 {i}: model_id={mapping['model_id']}, codes={codes_str}")

        return True

    except Exception as e:
        logger.error(f"创建示例因子配置失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="因子系统初始化脚本")
    parser.add_argument("--force", action="store_true", help="强制重新创建（删除已存在的记录）")
    parser.add_argument("--tables-only", action="store_true", help="只创建表，不创建示例数据")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("因子系统初始化开始")
    logger.info("=" * 60)

    # 1. 创建表
    if not create_tables():
        logger.error("创建表失败，退出")
        sys.exit(1)

    if args.tables_only:
        logger.info("只创建表模式，跳过示例数据创建")
        logger.info("=" * 60)
        logger.info("因子系统初始化完成（仅创建表）")
        logger.info("=" * 60)
        return

    # 3. 创建换手率因子
    if not create_turnover_rate_factor(force=args.force):
        logger.error("创建换手率因子失败")
        sys.exit(1)

    # 4. 创建示例配置
    if not create_example_config(force=args.force):
        logger.warning("创建示例配置失败（不影响整体流程）")

    logger.info("=" * 60)
    logger.info("因子系统初始化完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

