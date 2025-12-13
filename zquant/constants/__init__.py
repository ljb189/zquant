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
常量管理模块

统一管理项目中的常量
"""

from zquant.constants.data_constants import *
from zquant.constants.factor_constants import *
from zquant.constants.api_constants import *

__all__ = [
    # 数据常量
    "TUSTOCK_DAILY_VIEW_NAME",
    "TUSTOCK_DAILY_BASIC_VIEW_NAME",
    "DEFAULT_START_DATE",
    # 因子常量
    "FACTOR_TABLE_PREFIX",
    # API常量
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
]
