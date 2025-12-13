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
请求日志中间件
记录所有API请求的详细信息，包括请求ID追踪
"""

from collections.abc import Callable
import json
import time
import uuid
from contextvars import ContextVar

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

# 请求ID上下文变量，用于在整个请求生命周期中追踪请求
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# 响应体大小限制（100KB）
MAX_RESPONSE_BODY_SIZE = 100 * 1024

# 排除记录的路径关键词
EXCLUDE_PATHS = ["/download", "/export", "/stream"]

# 排除记录的内容类型
EXCLUDE_CONTENT_TYPES = [
    "text/event-stream",
    "application/stream+json",
    "application/octet-stream",
    "image/",
    "video/",
    "audio/",
]


def get_request_id() -> str | None:
    """
    获取当前请求ID

    Returns:
        当前请求ID，如果不在请求上下文中则返回None
    """
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """
    设置当前请求ID

    Args:
        request_id: 请求ID
    """
    request_id_var.set(request_id)


def should_exclude_response(path: str, content_type: str | None) -> bool:
    """
    判断是否应该排除响应体记录

    Args:
        path: 请求路径
        content_type: 响应内容类型

    Returns:
        如果应该排除则返回True，否则返回False
    """
    # 检查路径是否包含排除关键词
    if any(exclude_path in path for exclude_path in EXCLUDE_PATHS):
        return True

    # 检查内容类型是否应该排除
    if content_type:
        content_type_lower = content_type.lower()
        if any(exclude_type in content_type_lower for exclude_type in EXCLUDE_CONTENT_TYPES):
            return True

    return False


def format_response_body(response_body_bytes: bytes, request_id: str, is_truncated: bool = False) -> str:
    """
    格式化响应体用于日志记录

    Args:
        response_body_bytes: 响应体字节数据
        request_id: 请求ID
        is_truncated: 是否被截断

    Returns:
        格式化后的响应体字符串
    """
    if not response_body_bytes:
        return "(empty)"

    # 尝试解码为UTF-8
    try:
        body_str = response_body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # 如果不是UTF-8，记录为十六进制（截断）
        hex_str = response_body_bytes.hex()[:200]  # 只显示前200个字符
        truncate_note = " (truncated)" if is_truncated else ""
        return f"(binary data, {len(response_body_bytes)} bytes{truncate_note}, hex preview: {hex_str}...)"

    # 尝试解析JSON
    try:
        body_json = json.loads(body_str)
        # 敏感信息脱敏
        if isinstance(body_json, dict):
            body_json = _sanitize_sensitive_data(body_json)
        formatted = json.dumps(body_json, ensure_ascii=False, indent=2)
        if is_truncated:
            formatted += f"\n... (truncated at {MAX_RESPONSE_BODY_SIZE} bytes)"
        return formatted
    except (json.JSONDecodeError, ValueError):
        # 不是JSON，直接返回字符串
        if is_truncated:
            body_str += f"\n... (truncated at {MAX_RESPONSE_BODY_SIZE} bytes)"
        return body_str


def _sanitize_sensitive_data(data: dict) -> dict:
    """
    脱敏敏感数据

    Args:
        data: 数据字典

    Returns:
        脱敏后的数据字典
    """
    sensitive_keys = ["password", "token", "secret", "api_key", "access_token", "refresh_token"]
    sanitized = {}
    for key, value in data.items():
        key_lower = key.lower()
        if any(sensitive_key in key_lower for sensitive_key in sensitive_keys):
            sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_sensitive_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                _sanitize_sensitive_data(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            sanitized[key] = value
    return sanitized


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录日志

        为每个请求生成唯一的请求ID，用于追踪整个请求生命周期。
        """
        start_time = time.time()

        # 生成或获取请求ID
        # 优先使用客户端提供的X-Request-ID头，否则生成新的UUID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request_id)

        # 在响应头中添加请求ID，方便客户端追踪
        response_headers = {"X-Request-ID": request_id}

        # 记录请求信息
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # 获取请求体（仅对POST/PUT/PATCH请求）
        # 注意：读取请求体后需要重新创建Request对象，否则后续无法读取
        body = None
        body_bytes = None

        if method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_str = body_bytes.decode("utf-8")
                    # 尝试解析JSON
                    try:
                        body = json.loads(body_str)
                    except:
                        body = body_str  # 如果不是JSON，保持原样
            except Exception as e:
                logger.debug(f"读取请求体失败: {e}")

        # 如果读取了请求体，需要重新创建Request对象，以便后续可以再次读取
        if body_bytes is not None:

            async def receive():
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            request = Request(request.scope, receive)

        # 获取认证信息（不记录完整token，只记录是否提供）
        auth_header = request.headers.get("authorization", "")
        has_auth = bool(auth_header)
        auth_type = "Bearer" if auth_header.startswith("Bearer") else "None"

        # 记录请求开始（包含请求ID）
        logger.info(
            f"[REQUEST] [{request_id[:8]}] {method} {path} | "
            f"Client: {client_host} | "
            f"Auth: {auth_type} | "
            f"Query: {query_params if query_params else 'None'}"
        )

        if body:
            # 敏感信息脱敏
            if isinstance(body, dict) and "password" in body:
                body_log = {**body, "password": "***"}
                logger.debug(f"[REQUEST BODY] [{request_id[:8]}] {json.dumps(body_log, ensure_ascii=False)}")
            else:
                body_str = json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else str(body)
                logger.debug(f"[REQUEST BODY] [{request_id[:8]}] {body_str}")

        # 处理请求
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # 记录响应信息
            status_code = response.status_code

            # 在响应头中添加请求ID
            for key, value in response_headers.items():
                response.headers[key] = value

            # 记录响应（包含请求ID）
            log_level = logger.info if status_code >= 400 else logger.debug
            log_level(
                f"[RESPONSE] [{request_id[:8]}] {method} {path} | Status: {status_code} | Time: {process_time:.3f}s"
            )

            # 记录响应体（仅在debug级别）
            try:
                # 获取响应内容类型
                content_type = response.headers.get("content-type", "")
                content_type_base = content_type.split(";")[0].strip() if content_type else None

                # 检查是否应该排除记录
                if not should_exclude_response(path, content_type_base):
                    # 读取响应体
                    response_body_bytes = b""
                    is_truncated = False
                    async for chunk in response.body_iterator:
                        response_body_bytes += chunk
                        # 如果已经达到或超过限制，停止读取
                        if len(response_body_bytes) >= MAX_RESPONSE_BODY_SIZE:
                            is_truncated = True
                            break

                    # 格式化响应体
                    formatted_body = format_response_body(response_body_bytes, request_id, is_truncated)

                    # 记录响应体
                    logger.debug(f"[RESPONSE BODY] [{request_id[:8]}] {formatted_body}")

                    # 重新创建Response对象，以便客户端可以正常接收响应
                    response = StarletteResponse(
                        content=response_body_bytes,
                        status_code=status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )
            except Exception as e:
                # 响应体读取失败不影响主流程
                logger.debug(f"[RESPONSE BODY] [{request_id[:8]}] 读取响应体失败: {e}")

            # 记录性能警告
            if process_time > 1.0:
                logger.warning(f"[PERFORMANCE] [{request_id[:8]}] {method} {path} 处理时间较长: {process_time:.3f}s")

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"[ERROR] [{request_id[:8]}] {method} {path} | Exception: {e!s} | Time: {process_time:.3f}s")
            import traceback

            logger.debug(f"[ERROR] [{request_id[:8]}] 错误堆栈:\n{traceback.format_exc()}")
            raise
        finally:
            # 清理请求ID上下文
            request_id_var.set(None)
