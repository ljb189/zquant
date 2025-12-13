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
任务执行器
"""

from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from zquant.models.scheduler import TaskExecution, TaskType
from zquant.scheduler.base import TaskExecutor


class DataSyncExecutor(TaskExecutor):
    """数据同步任务执行器（已重构为使用Strategy模式）"""

    def __init__(self):
        # 注意：已重构为使用Strategy模式，不再需要直接使用DataScheduler
        pass

    def get_task_type(self) -> TaskType:
        return TaskType.COMMON_TASK

    def execute(self, db: Session, config: dict[str, Any], execution: TaskExecution | None = None) -> dict[str, Any]:
        """执行数据同步任务"""
        # 优先使用 task_action，向后兼容 task_type
        task_action = config.get("task_action")

        # 向后兼容：如果没有 task_action，尝试从 task_type 推断
        if not task_action:
            task_type = config.get("task_type")
            if isinstance(task_type, TaskType):
                task_action = self._infer_task_action_from_type(task_type)
            elif isinstance(task_type, str):
                task_action = self._infer_task_action_from_string(task_type)

        if not task_action:
            raise ValueError("数据同步任务配置中必须包含 'task_action' 字段，或提供 'task_type' 字段（向后兼容）")

        # 获取任务名（用于构建 extra_info）
        task_name = None
        if execution and execution.task_id:
            from zquant.models.scheduler import ScheduledTask

            task = db.query(ScheduledTask).filter(ScheduledTask.id == execution.task_id).first()
            if task:
                task_name = task.name
        # 如果无法从 execution 获取，尝试从 config 获取
        if not task_name:
            task_name = config.get("job_name") or config.get("task_name")

        # 构建 extra_info Dict
        extra_info = None
        if task_name:
            extra_info = {"created_by": task_name, "updated_by": task_name}

        try:
            # 使用Strategy模式创建对应的同步策略
            from zquant.services.sync_strategies.factory import SyncStrategyFactory

            strategy = SyncStrategyFactory.create_strategy(task_action)
            return strategy.sync(db, config, extra_info)
        except ValueError as e:
            # 策略工厂抛出的ValueError，直接抛出
            raise
        except Exception as e:
            logger.error(f"执行数据同步任务失败: {e}")
            raise

    def _infer_task_action_from_type(self, task_type: TaskType) -> str | None:
        """从 TaskType 推断 task_action（向后兼容）"""
        # 注意：旧的 DATA_SYNC_* 类型可能已经不存在于枚举中，但可能存在于数据库中
        # 这里只处理可能存在的类型
        try:
            type_to_action = {
                TaskType.DATA_SYNC_STOCK_LIST: "sync_stock_list",
                TaskType.DATA_SYNC_TRADING_CALENDAR: "sync_trading_calendar",
                TaskType.DATA_SYNC_DAILY_DATA: "sync_daily_data",
                TaskType.DATA_SYNC_ALL_DAILY_DATA: "sync_all_daily_data",
            }
            return type_to_action.get(task_type)
        except AttributeError:
            # 如果 TaskType 中没有这些值，返回 None
            return None

    def _infer_task_action_from_string(self, task_type_str: str) -> str | None:
        """从字符串形式的 task_type 推断 task_action（向后兼容）"""
        string_to_action = {
            "data_sync_stock_list": "sync_stock_list",
            "data_sync_trading_calendar": "sync_trading_calendar",
            "data_sync_daily_data": "sync_daily_data",
            "data_sync_all_daily_data": "sync_all_daily_data",
        }
        return string_to_action.get(task_type_str)

    # 注意：原有的_sync_*方法已移除，现在使用Strategy模式
    # 如果需要保留这些方法作为向后兼容，可以保留，但建议使用Strategy模式


# 任务执行器注册表（延迟导入以避免循环依赖）
EXECUTOR_REGISTRY: dict[TaskType, TaskExecutor] = {}


def _init_executor_registry():
    """初始化执行器注册表（延迟导入）"""
    if not EXECUTOR_REGISTRY:
        from zquant.scheduler.executors.common_executor import CommonTaskExecutor
        from zquant.scheduler.executors.workflow_executor import WorkflowExecutor

        EXECUTOR_REGISTRY.update(
            {
                TaskType.MANUAL_TASK: CommonTaskExecutor(),  # 手动任务使用通用任务执行器
                TaskType.COMMON_TASK: CommonTaskExecutor(),
                TaskType.WORKFLOW: WorkflowExecutor(),
            }
        )


# 初始化注册表
_init_executor_registry()


def get_executor(task_type: TaskType) -> TaskExecutor:
    """获取任务执行器"""
    _init_executor_registry()  # 确保注册表已初始化
    executor = EXECUTOR_REGISTRY.get(task_type)
    if not executor:
        raise ValueError(f"未找到任务类型 {task_type} 的执行器")
    return executor
