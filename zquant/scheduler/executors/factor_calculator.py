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
因子计算定时任务执行器
"""

from datetime import date

from loguru import logger
from sqlalchemy.orm import Session

from zquant.database import get_db_context
from sqlalchemy.orm import Session

from zquant.models.scheduler import TaskExecution, TaskType
from zquant.scheduler.base import TaskExecutor
from zquant.services.factor_calculation import FactorCalculationService


class FactorCalculatorExecutor(TaskExecutor):
    """因子计算执行器"""

    def get_task_type(self) -> TaskType:
        return TaskType.COMMON_TASK

    def execute(self, db: Session, config: dict, execution: TaskExecution | None = None) -> dict:
        """
        执行因子计算任务

        Args:
            db: 数据库会话
            config: 任务配置，支持以下字段：
                - task_action: 必须为 "calculate_factor"
                - factor_id: 因子ID（可选，None表示计算所有启用的因子）
                - codes: 股票代码列表（可选，None表示使用配置中的codes）
                - start_date: 开始日期（可选，与end_date一起使用，表示日期范围，ISO格式字符串；都不提供则使用今日）
                - end_date: 结束日期（可选，与start_date一起使用，表示日期范围，ISO格式字符串；都不提供则使用今日）
            execution: 执行记录对象（可选）

        Returns:
            执行结果字典
        """
        task_action = config.get("task_action")
        if task_action != "calculate_factor":
            raise ValueError(f"因子计算执行器只支持 task_action='calculate_factor'，当前为: {task_action}")

        factor_id = config.get("factor_id")
        codes = config.get("codes")
        
        start_date_str = config.get("start_date")
        start_date = date.fromisoformat(start_date_str) if start_date_str else None
        
        end_date_str = config.get("end_date")
        end_date = date.fromisoformat(end_date_str) if end_date_str else None

        logger.info(
            f"开始执行因子计算任务: factor_id={factor_id}, codes={codes}, "
            f"start_date={start_date}, end_date={end_date}"
        )

        # 使用 task_action 构建 extra_info
        extra_info = None
        if task_action:
            extra_info = {"created_by": task_action, "updated_by": task_action}

        try:
            # 执行因子计算
            result = FactorCalculationService.calculate_factor(
                db=db,
                factor_id=factor_id,
                codes=codes,
                start_date=start_date,
                end_date=end_date,
                extra_info=extra_info,
            )

            logger.info(
                f"因子计算任务完成: 成功={result['calculated_count']}, "
                f"数据不完整={result.get('invalid_count', 0)}, 失败={result['failed_count']}, "
                f"消息={result['message']}"
            )

            return {
                "success": result["success"],
                "message": result["message"],
                "calculated_count": result["calculated_count"],
                "failed_count": result["failed_count"],
                "invalid_count": result.get("invalid_count", 0),
                "details": result.get("details", [])[:10],  # 只返回前10条详情，避免日志过大
            }

        except Exception as e:
            error_msg = f"因子计算任务执行失败: {e!s}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "calculated_count": 0,
                "failed_count": 0,
                "details": [],
            }

