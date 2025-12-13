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
因子计算器工厂
"""

from typing import Any

from loguru import logger

from zquant.factor.calculators.base import BaseFactorCalculator
from zquant.factor.calculators.turnover_rate import TurnoverRateCalculator

# 注册的计算器映射
CALCULATOR_REGISTRY: dict[str, type[BaseFactorCalculator]] = {
    TurnoverRateCalculator.MODEL_CODE: TurnoverRateCalculator,
    "turnover_rate_ma": TurnoverRateCalculator,  # 移动平均换手率使用相同的计算器类
}


def register_calculator(model_code: str, calculator_class: type[BaseFactorCalculator]):
    """
    注册因子计算器

    Args:
        model_code: 模型代码
        calculator_class: 计算器类
    """
    CALCULATOR_REGISTRY[model_code] = calculator_class
    logger.info(f"注册因子计算器: {model_code} -> {calculator_class.__name__}")


def create_calculator(model_code: str, config: dict[str, Any] | None = None) -> BaseFactorCalculator:
    """
    创建因子计算器实例

    Args:
        model_code: 模型代码
        config: 模型配置

    Returns:
        因子计算器实例

    Raises:
        ValueError: 如果模型代码不存在
    """
    if model_code not in CALCULATOR_REGISTRY:
        raise ValueError(f"未知的因子计算器模型代码: {model_code}")

    calculator_class = CALCULATOR_REGISTRY[model_code]
    calculator = calculator_class(config=config)

    # 验证配置
    is_valid, error_msg = calculator.validate_config()
    if not is_valid:
        raise ValueError(f"因子计算器配置无效: {error_msg}")

    return calculator


def get_available_calculators() -> list[str]:
    """
    获取所有可用的计算器模型代码列表

    Returns:
        模型代码列表
    """
    return list(CALCULATOR_REGISTRY.keys())

