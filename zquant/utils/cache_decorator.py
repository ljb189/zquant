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
缓存装饰器

提供方法结果缓存和重试机制
"""

import functools
import json
import hashlib
from typing import Callable, Any, Optional
from loguru import logger
import time

from zquant.utils.cache import get_cache


def cache_result(
    expire: int = 3600,
    key_prefix: Optional[str] = None,
    key_func: Optional[Callable] = None,
) -> Callable:
    """
    缓存方法结果的装饰器

    Args:
        expire: 缓存过期时间（秒），默认3600秒（1小时）
        key_prefix: 缓存键前缀，如果为None则使用函数名
        key_func: 自定义缓存键生成函数，接收函数参数，返回字符串

    Returns:
        装饰器函数

    使用示例:
        @cache_result(expire=1800, key_prefix="user_info")
        def get_user_info(user_id: int):
            # 查询用户信息
            return user_info

        @cache_result(key_func=lambda user_id, db: f"user:{user_id}")
        def get_user(user_id: int, db: Session):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                prefix = key_prefix or func.__name__
                # 将参数转换为字符串用于生成键
                key_parts = [prefix]
                # 处理位置参数
                for arg in args:
                    if isinstance(arg, (str, int, float, bool, type(None))):
                        key_parts.append(str(arg))
                    elif hasattr(arg, "__dict__"):
                        # 对于对象，使用类名和id
                        key_parts.append(f"{type(arg).__name__}:{id(arg)}")
                # 处理关键字参数
                for k, v in sorted(kwargs.items()):
                    if isinstance(v, (str, int, float, bool, type(None))):
                        key_parts.append(f"{k}:{str(v)}")
                    elif hasattr(v, "__dict__"):
                        key_parts.append(f"{k}:{type(v).__name__}:{id(v)}")
                
                # 生成MD5哈希作为键（避免键过长）
                key_str = ":".join(key_parts)
                cache_key = f"cache:{hashlib.md5(key_str.encode()).hexdigest()}"

            # 尝试从缓存获取
            cache = get_cache()
            cached = cache.get(cache_key)
            if cached is not None:
                try:
                    return json.loads(cached)
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失败，继续执行函数
                    pass

            # 执行函数
            result = func(*args, **kwargs)

            # 缓存结果
            try:
                result_json = json.dumps(result, default=str)
                cache.set(cache_key, result_json, ex=expire)
            except (TypeError, ValueError) as e:
                # 如果无法序列化，记录警告但不影响函数执行
                logger.warning(f"无法缓存结果 {cache_key}: {e}")

            return result

        return wrapper
    return decorator


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    失败重试装饰器

    Args:
        max_retries: 最大重试次数，默认3次
        delay: 初始延迟时间（秒），默认1秒
        backoff: 延迟时间倍数，默认2.0（每次重试延迟时间翻倍）
        exceptions: 需要重试的异常类型，默认所有异常

    Returns:
        装饰器函数

    使用示例:
        @retry_on_failure(max_retries=3, delay=1.0)
        def fetch_data_from_api():
            # 从API获取数据
            return data

        @retry_on_failure(max_retries=5, exceptions=(ConnectionError, TimeoutError))
        def connect_to_database():
            # 连接数据库
            return connection
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}，"
                            f"{current_delay}秒后重试"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} 重试 {max_retries} 次后仍然失败: {e}")
                        raise

            # 理论上不会到达这里
            if last_exception:
                raise last_exception

        return wrapper
    return decorator
