#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说数据构建脚本
根据 config.toml 生成网站所需的 JSON 数据文件
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
import time

import tomllib  # Python 3.11+

class NovelDataBuilder:
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = config_path
        self.config = None
        self.chinese_content = {}  # 全局中文内容映射
        self.data_dir = Path("data")
        
        # 确保 data 目录存在
        self.data_dir.mkdir(exist_ok=True)
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'rb') as f:
                self.config = tomllib.load(f)
            print(f"✅ 成功加载配置文件: {self.config_path}")
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {self.config_path}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 解析配置文件失败: {e}")
            sys.exit(1)
    
    def parse_chinese_content(self, file_path: str) -> Dict[int, str]:
        """解析中文对照文件"""
        chinese_map = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 匹配格式: 文本内容 [[数字]]
                match = re.match(r'^(.*?)\s*\[\[(\d+)\]\]$', line)
                if match:
                    text = match.group(1).strip()
                    sentence_id = int(match.group(2))
                    chinese_map[sentence_id] = text
            
            print(f"✅ 解析中文内容: {len(chinese_map)} 条语句")
            return chinese_map
            
        except FileNotFoundError:
            print(f"❌ 中文文件不存在: {file_path}")
            return {}
        except Exception as e:
            print(f"❌ 解析中文文件失败: {e}")
            return {}
    
    def parse_english_chapter(self, file_path: str) -> List[Dict[str, Any]]:
        """解析英文章节文件"""
        sentences = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 匹配格式: 文本内容 [[数字 说话者 情绪]]
                match = re.match(r'^(.*?)\s*\[\[(\d+)\s+([^\s]+)\s+([^\]]+)\]\]$', line)
                if match:
                    english_text = match.group(1).strip()
                    sentence_id = int(match.group(2))
                    speaker = match.group(3)
                    emotion = match.group(4)
                    
                    sentence = {
                        "id": sentence_id,
                        "en": english_text,
                        "speaker": speaker,
                        "emotion": emotion
                    }
                    sentences.append(sentence)
            
            print(f"✅ 解析英文章节 {os.path.basename(file_path)}: {len(sentences)} 条语句")
            return sentences
            
        except FileNotFoundError:
            print(f"❌ 英文章节文件不存在: {file_path}")
            return []
        except Exception as e:
            print(f"❌ 解析英文章节失败: {e}")
            return []
    
    def check_local_audio_exists(self, local_audio_path: Path, chapter_id: str, sentence_id: int) -> bool:
        """检查本地音频文件是否存在"""
        audio_file = local_audio_path / chapter_id / f"{sentence_id}.wav"
        return audio_file.exists()
    
    def check_chapter_audio(self, local_audio_path: Path, chapter_id: str, sentences: List[Dict]) -> List[int]:
        """检查一个章节的所有音频文件"""
        available_audio = []
        
        # 检查章节目录是否存在
        chapter_audio_dir = local_audio_path / chapter_id
        if not chapter_audio_dir.exists():
            print(f"  ⚠️  音频目录不存在: {chapter_audio_dir}")
            return available_audio
        
        # 逐个检查每个语句的音频文件
        for sentence in sentences:
            sentence_id = sentence["id"]
            if self.check_local_audio_exists(local_audio_path, chapter_id, sentence_id):
                available_audio.append(sentence_id)
        
        print(f"  📻 章节 {chapter_id}: {len(available_audio)}/{len(sentences)} 条语句有音频")
        return available_audio
    
    def build_book_data(self, book_id: str, book_config: Dict) -> tuple:
        """构建单本书的数据"""
        print(f"\n📚 处理书籍: {book_id} - {book_config.get('title', book_id)}")
        
        # 加载中文对照内容
        cn_file = book_config.get('cn')
        if cn_file:
            chinese_content = self.parse_chinese_content(cn_file)
        else:
            print("⚠️  没有配置中文对照文件")
            chinese_content = {}
        
        # 书籍数据结构
        book_data = {
            "bookId": book_id,
            "bookTitle": book_config.get('title', book_id),
            "chapters": {}
        }
        
        # 音频数据结构
        audio_data = {
            "bookId": book_id,
            "audioBaseUrl": self.config.get('url', '') + book_config.get('audio', ''),
            "availability": {}
        }
        
        # 章节信息（用于主索引）
        chapters_info = []
        
        # 处理章节
        chap_config = book_config.get('chap', {})
        
        # 获取本地音频目录路径
        local_audio_path = Path(book_config.get('audio', ''))
        if not local_audio_path.exists():
            print(f"⚠️  本地音频目录不存在: {local_audio_path}")
            print(f"    将创建空的音频可用性数据")
        
        for chap_num, chap_info in chap_config.items():
            chapter_id = str(chap_num).zfill(4)  # 格式化为 0001, 0002 等
            
            print(f"  📖 处理章节 {chapter_id}: {chap_info.get('title', '')}")
            
            # 解析英文章节
            en_file = chap_info.get('en')
            if not en_file:
                print(f"    ⚠️  章节 {chapter_id} 没有配置英文文件")
                continue
            
            sentences = self.parse_english_chapter(en_file)
            if not sentences:
                print(f"    ⚠️  章节 {chapter_id} 没有解析到语句")
                continue
            
            # 添加中文内容
            for sentence in sentences:
                sentence_id = sentence["id"]
                sentence["cn"] = chinese_content.get(sentence_id, "")
            
            # 检查本地音频可用性
            print(f"  🔍 检查章节 {chapter_id} 的本地音频文件...")
            available_audio = self.check_chapter_audio(local_audio_path, chapter_id, sentences)
            
            # 保存数据
            book_data["chapters"][chapter_id] = sentences
            audio_data["availability"][chapter_id] = available_audio
            
            # 添加到章节信息
            chapters_info.append({
                "id": chapter_id,
                "title": chap_info.get('title', f'第{chap_num}章')
            })
        
        return book_data, audio_data, chapters_info
    
    def build_all_data(self):
        """构建所有数据"""
        print("🚀 开始构建小说数据...")
        
        # 主索引数据
        novels_index = []
        
        # 处理每本书
        novels_config = self.config.get('novels', {})
        for book_id, book_config in novels_config.items():
            book_data, audio_data, chapters_info = self.build_book_data(book_id, book_config)
            
            # 保存书籍内容文件
            book_file = self.data_dir / f"{book_id}.json"
            with open(book_file, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存书籍内容: {book_file}")
            
            # 保存音频数据文件
            audio_file = self.data_dir / f"{book_id}_audio.json"
            with open(audio_file, 'w', encoding='utf-8') as f:
                json.dump(audio_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 保存音频数据: {audio_file}")
            
            # 添加到主索引
            novels_index.append({
                "id": book_id,
                "title": book_config.get('title', book_id),
                "chapters": chapters_info
            })
        
        # 保存主索引文件
        index_file = self.data_dir / "novels.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(novels_index, f, ensure_ascii=False, indent=2)
        print(f"✅ 保存主索引: {index_file}")
        
        print(f"\n🎉 数据构建完成! 共处理 {len(novels_index)} 本书")
        
        # 统计信息
        total_chapters = sum(len(book["chapters"]) for book in novels_index)
        print(f"📊 统计信息:")
        print(f"   - 书籍数量: {len(novels_index)}")
        print(f"   - 章节总数: {total_chapters}")
        print(f"   - 生成文件: {len(os.listdir(self.data_dir))} 个")
    
    def run(self):
        """运行构建过程"""
        start_time = time.time()
        
        print("=" * 50)
        print("📖 小说数据构建工具")
        print("=" * 50)
        
        # 加载配置
        self.load_config()
        
        # 构建数据
        self.build_all_data()
        
        end_time = time.time()
        print(f"\n⏱️  总耗时: {end_time - start_time:.2f} 秒")
        print("=" * 50)


def main():
    """主函数"""
    builder = NovelDataBuilder()
    builder.run()


if __name__ == "__main__":
    # 运行主函数
    main() 