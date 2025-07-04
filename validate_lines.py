#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本：检查小说章节文件的行尾格式

功能:
- 遍历 `books` 目录下的所有书籍。
- 检查每个章节文件（如 0001.txt）中的每一行。
- 验证每一行是否都以 `[[数字 角色 情绪]]` 的格式结尾。
- 输出所有不符合规范的行，并报告其文件路径和行号。
"""

import re
from pathlib import Path
import sys

def validate_line_format(line: str) -> bool:
    """
    检查单行文本是否符合 `... [[id speaker emotion]]` 格式。
    
    Args:
        line: 要检查的文本行。

    Returns:
        如果格式正确则返回 True，否则返回 False。
    """
    # 正则表达式：匹配以 [[数字 角色 情绪]] 结尾的行
    # - `.*?`        : 匹配任意文本内容
    # - `\s*`        : 匹配文本和标记之间的任意空白
    # - `\[\[`       : 匹配字面上的 [[
    # - `(\d+)`      : 捕获一个或多个数字 (id)
    # - `\s+`        : 匹配一个或多个空白字符
    # - `([^\s\]]+)` : 捕获一个或多个非空白、非右方括号的字符 (speaker)
    # - `\s+`        : 匹配一个或多个空白字符
    # - `([^\]]+)`   : 捕获一个或多个非右方括号的字符 (emotion)
    # - `\]\]`       : 匹配字面上的 ]]
    # - `$`          : 确保标记在行尾
    pattern = re.compile(r'.*?\[\[\d+\s+[^\s\]]+\s+[^\]]+\]\]$')
    return pattern.match(line) is not None

def find_invalid_lines(root_dir: str = "books"):
    """
    在指定目录中查找所有不符合格式的行。

    Args:
        root_dir: 要扫描的根目录。
    """
    print(f"🚀 开始扫描目录: {root_dir}")
    
    root_path = Path(root_dir)
    if not root_path.is_dir():
        print(f"❌ 错误: 目录不存在 -> {root_dir}")
        sys.exit(1)
    
    invalid_lines_found = 0
    files_checked = 0

    # 使用 glob 查找所有数字命名的 .txt 文件
    # ** 会递归搜索所有子目录
    chapter_files = sorted(p for p in root_path.glob("**/*.txt") if p.stem.isdigit())

    if not chapter_files:
        print("🟡 警告: 未找到任何章节文件 (如 0001.txt)。")
        return

    for file_path in chapter_files:
        files_checked += 1
        try:
            with file_path.open('r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"  📖 正在检查: {file_path} ({len(lines)}行)")
            
            for i, line in enumerate(lines):
                line = line.strip()
                # 只检查非空行
                if line:
                    if not validate_line_format(line):
                        print(f"  ❌ 格式错误! -> 文件: {file_path}, 行号: {i+1}")
                        print(f"     内容: {line}\n")
                        invalid_lines_found += 1

        except Exception as e:
            print(f"  🚨 读取文件时出错: {file_path}")
            print(f"     错误信息: {e}\n")

    print("\n" + "="*50)
    if invalid_lines_found == 0:
        print(f"✅ 扫描完成! 在 {files_checked} 个文件中未发现格式错误。")
    else:
        print(f"⚠️ 扫描完成! 共在 {files_checked} 个文件中发现 {invalid_lines_found} 处格式错误。")
    print("="*50)

def main():
    """主函数"""
    find_invalid_lines()

if __name__ == "__main__":
    main() 