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
Windows兼容的日志文件处理器
解决Windows系统上日志文件滚动时的权限错误问题
"""

import logging
import os
import platform
import shutil
import time
from logging.handlers import TimedRotatingFileHandler


class WindowsCompatibleTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Windows兼容的按时间滚动的文件处理器

    在Windows系统上，当日志文件被其他程序（如日志查看器）打开时，
    使用os.rename()会失败。这个处理器使用复制+删除策略来避免这个问题。
    """

    def doRollover(self):
        """
        执行日志文件滚动

        在Windows系统上，如果重命名失败，会尝试使用复制+删除策略。
        如果仍然失败，会记录错误但不会中断日志记录。
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # 计算新的日志文件名
        currentTime = int(time.time())
        dst = self.baseFilename + "." + time.strftime(self.suffix, time.localtime(currentTime))

        # 尝试重命名（在Linux/Mac上通常可以工作）
        try:
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(self.baseFilename, dst)
        except (OSError, PermissionError) as e:
            # Windows系统上，如果文件被占用，重命名会失败
            # 尝试使用复制+清空策略
            if platform.system() == "Windows":
                try:
                    if os.path.exists(dst):
                        os.remove(dst)
                    # 使用复制而不是重命名
                    shutil.copy2(self.baseFilename, dst)
                    # 尝试清空原文件（如果失败也不影响，至少备份已创建）
                    try:
                        # 使用追加模式打开，然后截断到0（这样即使文件被占用也能工作）
                        with open(self.baseFilename, "r+", encoding=self.encoding) as f:
                            f.seek(0)
                            f.truncate(0)
                    except (OSError, PermissionError):
                        # 清空失败不影响，至少备份文件已创建
                        pass
                except (OSError, PermissionError) as e2:
                    # 如果复制也失败，记录错误但继续使用当前文件
                    # 这样不会中断日志记录
                    if self.stream is None:
                        self.stream = self._open()
                    # 使用标准logging记录错误（避免循环）
                    logging.getLogger().error(
                        f"日志文件滚动失败: {e2}. 将继续写入当前日志文件。"
                        f"请关闭可能打开日志文件的程序（如日志查看器、编辑器等）。"
                    )
                    return
            else:
                # 非Windows系统，如果重命名失败，记录错误
                if self.stream is None:
                    self.stream = self._open()
                logging.getLogger().error(f"日志文件滚动失败: {e}")
                return

        # 删除旧的日志文件
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                try:
                    os.remove(s)
                except (OSError, PermissionError):
                    # 删除失败不影响主流程
                    pass

        # 重新打开日志文件
        if not self.delay:
            self.stream = self._open()

