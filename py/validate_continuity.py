#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本：检查小说章节的连续性

功能:
- 遍历 `books` 目录下的所有书籍。
- 对每本书籍：
  1. 检查章节文件（如 0001.txt, 0002.txt）的序号是否连续无中断。
  2. 检查每一行末尾 `[[ID ...]]` 中的 ID 是否全局连续递增（包括跨文件）。
- 输出所有发现的不连续问题。
- 如果发现任何错误，脚本将以非零状态码退出。
"""

import re
import sys
from pathlib import Path

# 正则表达式：从行尾的 [[...]] 标签中提取 ID
LINE_ID_PATTERN = re.compile(r'\[\[(\d+)\s+.*\]\]$')

def extract_line_id(line: str) -> int | None:
    """从行中提取数字ID。"""
    match = LINE_ID_PATTERN.search(line.strip())
    if match:
        return int(match.group(1))
    return None

def validate_book_continuity(book_path: Path) -> int:
    """
    验证单本书籍的文件和行ID的连续性。
    返回发现的错误数量。
    """
    print(f"📖 正在检查书籍: {book_path.name}")
    errors_found = 0
    
    # 1. 查找并排序章节文件
    chapter_files = sorted(
        [p for p in book_path.glob("*.txt") if p.stem.isdigit()],
        key=lambda p: int(p.stem)
    )

    if not chapter_files:
        print("  🟡 警告: 未找到任何章节文件。")
        return 0

    # 2. 检查文件编号是否有间隙
    expected_file_num = 1
    for file_path in chapter_files:
        file_num = int(file_path.stem)
        if file_num != expected_file_num:
            print(f"  ❌ 文件序号不连续! 期望: {str(expected_file_num).zfill(4)}.txt, 但找到: {file_path.name}")
            errors_found += 1
            expected_file_num = file_num  # 从当前文件号继续检查
        expected_file_num += 1

    # 3. 检查所有文件中行ID的连续性
    last_line_id = 0
    for file_path in chapter_files:
        try:
            with file_path.open('r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    current_id = extract_line_id(line)

                    if current_id is None:
                        print(f"  ❌ 格式错误: 在 {file_path.name}, 行 {i} 未找到ID标签")
                        print(f"     内容: {line}")
                        errors_found += 1
                        continue

                    if current_id <= last_line_id:
                        print(f"  ❌ ID未递增: 在 {file_path.name}, 行 {i}")
                        print(f"     期望 ID 大于 {last_line_id}, 但找到: {current_id}")
                        errors_found += 1
                    
                    last_line_id = current_id
        except Exception as e:
            print(f"  🚨 读取文件时出错: {file_path}")
            print(f"     错误信息: {e}\n")
            errors_found += 1
            
    if errors_found == 0:
        print("  ✅ 未发现连续性错误。")
    
    print("-" * 20)
    return errors_found

def main():
    """主函数，对所有书籍运行检查。"""
    books_root = Path("books")
    total_errors = 0
    
    print("🚀 开始检查书籍连续性...")
    
    book_dirs = [d for d in books_root.iterdir() if d.is_dir()]

    if not book_dirs:
        print("❌ 错误: 在 'books/' 目录下未找到任何书籍目录。")
        sys.exit(1)

    for book_path in book_dirs:
        # 仅当目录中包含数字命名的txt文件时才进行检查
        if any(p for p in book_path.glob("*.txt") if p.stem.isdigit()):
             total_errors += validate_book_continuity(book_path)

    print("\n" + "="*50)
    if total_errors == 0:
        print("✅ 所有书籍均通过连续性检查！")
    else:
        print(f"⚠️ 检查完成! 共发现 {total_errors} 处连续性错误。")
        sys.exit(1)
    print("="*50)

if __name__ == "__main__":
    main() 