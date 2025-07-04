#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据文件系统中的章节文件自动更新 config.toml
"""

import tomllib
import toml
import re
from pathlib import Path
import sys

def parse_chinese_content(file_path: Path) -> dict[int, str]:
    """解析中文对照文件"""
    chinese_map = {}
    if not file_path.exists():
        print(f"❌ 中文文件不存在: {file_path}")
        return {}
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = re.match(r'^(.*?)\s*\[\[(\d+)\]\]$', line)
            if match:
                text = match.group(1).strip()
                sentence_id = int(match.group(2))
                chinese_map[sentence_id] = text
        
        print(f"✅ 解析中文内容: {len(chinese_map)} 条语句")
        return chinese_map
    except Exception as e:
        print(f"❌ 解析中文文件失败: {e}")
        return {}

def get_sentence_id_from_chapter(file_path: Path) -> int | None:
    """从英文章节的第一行获取句子ID"""
    if not file_path.exists():
        return None
    
    try:
        with file_path.open('r', encoding='utf-8') as f:
            first_line = f.readline()
        
        match = re.search(r'\[\[(\d+)', first_line)
        if match:
            return int(match.group(1))
        return None
    except Exception as e:
        print(f"❌ 读取章节文件失败 {file_path}: {e}")
        return None

def main():
    """主函数"""
    config_path = Path("config.toml")
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)

    print(f"📖 正在加载配置文件: {config_path}")
    with config_path.open("rb") as f:
        config = tomllib.load(f)

    novels_config = config.get("novels", {})
    
    for book_id, book_config in novels_config.items():
        print(f"\n📚 处理书籍: {book_id}")
        book_path = Path("books") / book_id
        cn_file_path = Path(book_config.get("cn", ""))

        if not cn_file_path or not book_path.exists():
            print(f"  ⚠️  跳过 {book_id}: 未配置 'cn' 文件或书籍目录不存在。")
            continue

        chinese_map = parse_chinese_content(cn_file_path)
        if not chinese_map:
            print(f"  ⚠️  跳过 {book_id}: 无法从 {cn_file_path} 解析中文内容。")
            continue

        new_chap_config = {}
        chapter_files = sorted(list(book_path.glob("????.txt")))

        print(f"  🔍 找到 {len(chapter_files)} 个章节文件。")

        for chap_file in chapter_files:
            chapter_num_str = chap_file.stem
            try:
                chapter_num = int(chapter_num_str)
            except ValueError:
                print(f"  ⚠️  跳过无效的章节文件名: {chap_file}")
                continue

            sentence_id = get_sentence_id_from_chapter(chap_file)
            
            default_title = f"第{chapter_num}章 待定"
            title = default_title

            if sentence_id is not None:
                title = chinese_map.get(sentence_id, default_title)
            else:
                print(f"  - 无法从 {chap_file} 的第一行找到句子ID。")

            # 使用 aPath.as_posix() 来确保路径在不同操作系统下的一致性
            new_chap_config[str(chapter_num)] = {
                'en': chap_file.as_posix(),
                'title': title
            }
            print(f"  - 第 {chapter_num} 章: '{title}'")

        # 更新 config 对象中的章节信息
        if "chap" not in config["novels"][book_id]:
            config["novels"][book_id]["chap"] = {}
        
        config["novels"][book_id]["chap"] = new_chap_config

    # --- 新的写入逻辑 ---
    print("\n🔄 准备更新配置文件...")
    
    # 1. 读取原始 config.toml 内容
    try:
        original_content = config_path.read_text(encoding="utf-8")
        lines = original_content.splitlines()
    except Exception as e:
        print(f"❌ 读取原始配置文件失败: {e}")
        return

    # 2. 准备要写入的新内容
    new_content_lines = []
    in_chap_section = False
    chap_section_processed = set()

    # 遍历原始文件的每一行
    for line in lines:
        stripped_line = line.strip()
        
        # 检查是否进入了一个新的 [novels.BOOK_ID.chap] section
        match = re.match(r'\[novels\.([^.]+)\.chap\]', stripped_line)
        if match:
            book_id = match.group(1)
            in_chap_section = True
            
            # 如果这个 book_id 在我们处理的 novel config 中
            if book_id in novels_config:
                chap_section_processed.add(book_id)
                
                # 添加 section header
                new_content_lines.append(stripped_line)
                
                # 生成新的、格式化的章节条目
                chap_config = config.get("novels", {}).get(book_id, {}).get("chap", {})
                for num, info in chap_config.items():
                    # 确保 title 中的双引号被转义
                    title_escaped = info['title'].replace('"', '\\"')
                    en_path = info['en']
                    new_line = f'{num} = {{en = "{en_path}", title = "{title_escaped}"}}'
                    new_content_lines.append(new_line)
                continue # 跳过旧的章节条目

        # 如果在 chap section 中，但不是 header，就跳过旧行
        if in_chap_section and stripped_line and not stripped_line.startswith('['):
            continue
        
        # 如果离开了 chap section
        if in_chap_section and stripped_line.startswith('['):
            in_chap_section = False
        
        # 保留原始行
        new_content_lines.append(line)

    # 3. 如果原始文件中没有 chap section，则在文件末尾追加
    for book_id, book_config in novels_config.items():
        if book_id not in chap_section_processed and "chap" in book_config:
            new_content_lines.append(f"\n[novels.{book_id}.chap]")
            chap_config = book_config["chap"]
            for num, info in chap_config.items():
                title_escaped = info['title'].replace('"', '\\"')
                en_path = info['en']
                new_line = f'{num} = {{en = "{en_path}", title = "{title_escaped}"}}'
                new_content_lines.append(new_line)

    # 4. 将更新后的内容写回文件
    try:
        with config_path.open("w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(new_content_lines))
        print(f"✅ 配置文件 {config_path} 更新成功！")
    except Exception as e:
        print(f"❌ 写入配置文件失败: {e}")

if __name__ == "__main__":
    main() 