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
API相关常量
"""

# 分页相关
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 1000

# 缓存过期时间（秒）
CACHE_EXPIRE_SHORT = 300  # 5分钟
CACHE_EXPIRE_MEDIUM = 3600  # 1小时
CACHE_EXPIRE_LONG = 86400  # 1天

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30
