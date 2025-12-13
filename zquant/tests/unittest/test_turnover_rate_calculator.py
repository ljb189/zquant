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
换手率因子计算器单元测试
"""

import unittest
from datetime import date, timedelta
from unittest.mock import patch

from zquant.factor.calculators.turnover_rate import TurnoverRateCalculator

from .base import BaseTestCase


class TestTurnoverRateCalculator(BaseTestCase):
    """换手率因子计算器测试"""

    def setUp(self):
        """每个测试方法执行前"""
        super().setUp()
        self.test_code = "000001.SZ"
        self.test_date = date(2025, 1, 10)

    # ==================== 基础换手率计算测试 ====================

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_basic_success(self, mock_get_data):
        """测试成功计算基础换手率"""
        # 设置mock返回值
        mock_get_data.return_value = [{"trade_date": "2025-01-10", "turnover_rate": 2.5}]

        # 创建计算器
        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate"})

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result, 2.5)
        mock_get_data.assert_called_once_with(self.db, ts_code=self.test_code, start_date=self.test_date, end_date=self.test_date)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_basic_no_data(self, mock_get_data):
        """测试没有数据时返回None"""
        # 设置mock返回空列表
        mock_get_data.return_value = []

        # 创建计算器
        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate"})

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果
        self.assertIsNone(result)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_basic_null_value(self, mock_get_data):
        """测试字段值为None时返回None"""
        # 设置mock返回值，但turnover_rate为None
        mock_get_data.return_value = [{"trade_date": "2025-01-10", "turnover_rate": None}]

        # 创建计算器
        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate"})

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果
        self.assertIsNone(result)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_basic_custom_field(self, mock_get_data):
        """测试使用自定义字段名"""
        # 设置mock返回值
        mock_get_data.return_value = [{"trade_date": "2025-01-10", "turnover_rate_f": 3.2}]

        # 创建计算器，使用自定义字段
        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate_f"})

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result, 3.2)

    # ==================== 移动平均换手率计算测试 ====================

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_success(self, mock_get_data):
        """测试成功计算移动平均换手率"""
        # 准备5天的历史数据
        start_date = self.test_date - timedelta(days=10)
        mock_data = []
        for i in range(5):
            trade_date = self.test_date - timedelta(days=4 - i)
            mock_data.append({"trade_date": trade_date.isoformat(), "turnover_rate": 2.0 + i * 0.1})

        mock_get_data.return_value = mock_data

        # 创建计算器，使用移动平均方法
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果：平均值应该是 (2.0 + 2.1 + 2.2 + 2.3 + 2.4) / 5 = 2.2
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 2.2, places=4)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_insufficient_data(self, mock_get_data):
        """测试数据不足window条时返回None"""
        # 准备少于5条的数据
        mock_data = [
            {"trade_date": (self.test_date - timedelta(days=2)).isoformat(), "turnover_rate": 2.0},
            {"trade_date": (self.test_date - timedelta(days=1)).isoformat(), "turnover_rate": 2.1},
        ]

        mock_get_data.return_value = mock_data

        # 创建计算器，窗口大小为5
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果：数据不足，应该返回None
        self.assertIsNone(result)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_with_missing_days(self, mock_get_data):
        """测试有缺失交易日的情况"""
        # 准备数据，但跳过某些日期（模拟非交易日）
        mock_data = []
        dates = [
            self.test_date - timedelta(days=6),  # 第1天
            self.test_date - timedelta(days=5),  # 第2天
            # 跳过第3天（非交易日）
            self.test_date - timedelta(days=3),  # 第4天
            self.test_date - timedelta(days=2),  # 第5天
            self.test_date - timedelta(days=1),  # 第6天
        ]
        for i, d in enumerate(dates):
            mock_data.append({"trade_date": d.isoformat(), "turnover_rate": 2.0 + i * 0.1})

        mock_get_data.return_value = mock_data

        # 创建计算器，窗口大小为5
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果：应该使用最近5条有效数据
        self.assertIsNotNone(result)
        # 平均值应该是最近5条数据的平均值
        expected_avg = sum([2.0 + i * 0.1 for i in range(5)]) / 5
        self.assertAlmostEqual(result, expected_avg, places=4)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_custom_window(self, mock_get_data):
        """测试自定义窗口大小"""
        # 准备10天的历史数据
        mock_data = []
        for i in range(10):
            trade_date = self.test_date - timedelta(days=9 - i)
            mock_data.append({"trade_date": trade_date.isoformat(), "turnover_rate": 1.0 + i * 0.1})

        mock_get_data.return_value = mock_data

        # 创建计算器，窗口大小为3
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 3}
        )

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果：应该使用最近3条数据
        self.assertIsNotNone(result)
        # 最近3条数据的平均值：(1.7 + 1.8 + 1.9) / 3 = 1.8
        self.assertAlmostEqual(result, 1.8, places=4)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_filters_null_values(self, mock_get_data):
        """测试过滤空值"""
        # 准备数据，其中部分值为None
        mock_data = [
            {"trade_date": (self.test_date - timedelta(days=4)).isoformat(), "turnover_rate": 2.0},
            {"trade_date": (self.test_date - timedelta(days=3)).isoformat(), "turnover_rate": None},  # 空值
            {"trade_date": (self.test_date - timedelta(days=2)).isoformat(), "turnover_rate": 2.2},
            {"trade_date": (self.test_date - timedelta(days=1)).isoformat(), "turnover_rate": None},  # 空值
            {"trade_date": self.test_date.isoformat(), "turnover_rate": 2.4},
            # 额外添加一些有效数据，确保有足够的有效数据
            {"trade_date": (self.test_date - timedelta(days=5)).isoformat(), "turnover_rate": 1.9},
            {"trade_date": (self.test_date - timedelta(days=6)).isoformat(), "turnover_rate": 1.8},
        ]

        mock_get_data.return_value = mock_data

        # 创建计算器，窗口大小为5
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        # 执行计算
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 验证结果：应该过滤掉None值，使用有效数据
        self.assertIsNotNone(result)
        # 有效数据：1.8, 1.9, 2.0, 2.2, 2.4，平均值 = 2.06
        self.assertAlmostEqual(result, 2.06, places=4)

    # ==================== 配置验证测试 ====================

    def test_validate_config_valid_basic(self):
        """测试基础配置验证通过"""
        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate"})
        is_valid, error_msg = calculator.validate_config()
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_validate_config_valid_ma(self):
        """测试移动平均配置验证通过"""
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )
        is_valid, error_msg = calculator.validate_config()
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "")

    def test_validate_config_invalid_source(self):
        """测试无效数据来源"""
        calculator = TurnoverRateCalculator(config={"source": "invalid_source", "field": "turnover_rate"})
        is_valid, error_msg = calculator.validate_config()
        self.assertFalse(is_valid)
        self.assertIn("不支持的数据来源", error_msg)

    def test_validate_config_empty_field(self):
        """测试空字段名"""
        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": ""})
        is_valid, error_msg = calculator.validate_config()
        self.assertFalse(is_valid)
        self.assertIn("字段名不能为空", error_msg)

    def test_validate_config_invalid_window_negative(self):
        """测试无效窗口大小（负数）"""
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": -1}
        )
        is_valid, error_msg = calculator.validate_config()
        self.assertFalse(is_valid)
        self.assertIn("移动平均窗口大小必须是正整数", error_msg)

    def test_validate_config_invalid_window_zero(self):
        """测试无效窗口大小（0）"""
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 0}
        )
        is_valid, error_msg = calculator.validate_config()
        self.assertFalse(is_valid)
        self.assertIn("移动平均窗口大小必须是正整数", error_msg)

    def test_validate_config_invalid_window_too_large(self):
        """测试无效窗口大小（超过60）"""
        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 61}
        )
        is_valid, error_msg = calculator.validate_config()
        self.assertFalse(is_valid)
        self.assertIn("移动平均窗口大小不能超过60", error_msg)

    # ==================== 边界情况测试 ====================

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_single_record(self, mock_get_data):
        """测试只有1条数据时（window=1）"""
        mock_data = [{"trade_date": self.test_date.isoformat(), "turnover_rate": 2.5}]
        mock_get_data.return_value = mock_data

        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 1}
        )

        result = calculator.calculate(self.db, self.test_code, self.test_date)

        self.assertIsNotNone(result)
        self.assertEqual(result, 2.5)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_all_null_values(self, mock_get_data):
        """测试所有值都为None"""
        mock_data = [
            {"trade_date": (self.test_date - timedelta(days=i)).isoformat(), "turnover_rate": None}
            for i in range(5)
        ]
        mock_get_data.return_value = mock_data

        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        result = calculator.calculate(self.db, self.test_code, self.test_date)

        self.assertIsNone(result)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_mixed_null_values(self, mock_get_data):
        """测试部分值为None的情况"""
        mock_data = [
            {"trade_date": (self.test_date - timedelta(days=4)).isoformat(), "turnover_rate": 2.0},
            {"trade_date": (self.test_date - timedelta(days=3)).isoformat(), "turnover_rate": None},
            {"trade_date": (self.test_date - timedelta(days=2)).isoformat(), "turnover_rate": 2.2},
            {"trade_date": (self.test_date - timedelta(days=1)).isoformat(), "turnover_rate": 2.3},
            {"trade_date": self.test_date.isoformat(), "turnover_rate": 2.4},
        ]
        mock_get_data.return_value = mock_data

        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 应该过滤掉None值，使用有效数据：2.0, 2.2, 2.3, 2.4
        # 但有效数据只有4条，不足5条，应该返回None
        self.assertIsNone(result)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_date_sorting(self, mock_get_data):
        """测试日期排序正确性"""
        # 准备乱序的数据
        mock_data = [
            {"trade_date": (self.test_date - timedelta(days=2)).isoformat(), "turnover_rate": 2.2},
            {"trade_date": (self.test_date - timedelta(days=4)).isoformat(), "turnover_rate": 2.0},
            {"trade_date": self.test_date.isoformat(), "turnover_rate": 2.4},
            {"trade_date": (self.test_date - timedelta(days=1)).isoformat(), "turnover_rate": 2.3},
            {"trade_date": (self.test_date - timedelta(days=3)).isoformat(), "turnover_rate": 2.1},
        ]
        mock_get_data.return_value = mock_data

        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 应该正确排序并使用最近5条数据
        self.assertIsNotNone(result)
        # 排序后的值：2.0, 2.1, 2.2, 2.3, 2.4，平均值 = 2.2
        self.assertAlmostEqual(result, 2.2, places=4)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_date_object_format(self, mock_get_data):
        """测试日期对象格式（而非字符串）"""
        # 准备数据，使用date对象而非字符串
        mock_data = []
        for i in range(5):
            trade_date = self.test_date - timedelta(days=4 - i)
            mock_data.append({"trade_date": trade_date, "turnover_rate": 2.0 + i * 0.1})

        mock_get_data.return_value = mock_data

        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        result = calculator.calculate(self.db, self.test_code, self.test_date)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 2.2, places=4)

    # ==================== 错误处理测试 ====================

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_exception_handling(self, mock_get_data):
        """测试异常情况下的错误处理"""
        # 设置mock抛出异常
        mock_get_data.side_effect = Exception("数据库连接失败")

        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate"})

        # 执行计算，应该捕获异常并返回None
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        self.assertIsNone(result)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_invalid_value_type(self, mock_get_data):
        """测试无效值类型（非数字）"""
        # 设置mock返回值，但turnover_rate是字符串
        mock_get_data.return_value = [{"trade_date": "2025-01-10", "turnover_rate": "invalid"}]

        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate"})

        # 执行计算，应该处理异常并返回None
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        self.assertIsNone(result)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_invalid_date_format(self, mock_get_data):
        """测试无效日期格式的处理"""
        # 准备数据，其中日期格式无效
        mock_data = [
            {"trade_date": "invalid-date", "turnover_rate": 2.0},
            {"trade_date": (self.test_date - timedelta(days=1)).isoformat(), "turnover_rate": 2.1},
            {"trade_date": (self.test_date - timedelta(days=2)).isoformat(), "turnover_rate": 2.2},
            {"trade_date": (self.test_date - timedelta(days=3)).isoformat(), "turnover_rate": 2.3},
            {"trade_date": (self.test_date - timedelta(days=4)).isoformat(), "turnover_rate": 2.4},
        ]

        mock_get_data.return_value = mock_data

        calculator = TurnoverRateCalculator(
            config={"source": "daily_basic", "field": "turnover_rate", "method": "ma", "window": 5}
        )

        # 执行计算，应该跳过无效日期格式的记录
        result = calculator.calculate(self.db, self.test_code, self.test_date)

        # 应该使用有效的4条数据，但不足5条，返回None
        # 或者如果排序失败，也可能返回None
        # 这里我们期望它能处理无效日期，使用有效数据
        # 但由于有效数据不足5条，应该返回None
        self.assertIsNone(result)

    # ==================== 默认配置测试 ====================

    def test_default_config(self):
        """测试默认配置"""
        calculator = TurnoverRateCalculator()
        self.assertEqual(calculator.source, "daily_basic")
        self.assertEqual(calculator.field, "turnover_rate")
        self.assertIsNone(calculator.method)
        self.assertEqual(calculator.window, 5)

    @patch("zquant.factor.calculators.turnover_rate.DataService.get_daily_basic_data")
    def test_calculate_ma_default_window(self, mock_get_data):
        """测试使用默认窗口大小（5）"""
        # 准备5天的历史数据
        mock_data = []
        for i in range(5):
            trade_date = self.test_date - timedelta(days=4 - i)
            mock_data.append({"trade_date": trade_date.isoformat(), "turnover_rate": 2.0 + i * 0.1})

        mock_get_data.return_value = mock_data

        # 创建计算器，只指定method，不指定window（使用默认值5）
        calculator = TurnoverRateCalculator(config={"source": "daily_basic", "field": "turnover_rate", "method": "ma"})

        result = calculator.calculate(self.db, self.test_code, self.test_date)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 2.2, places=4)

