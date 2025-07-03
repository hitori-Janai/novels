# 小说数据构建工具

这个Python脚本用于根据 `config.toml` 配置文件生成网站所需的JSON数据文件。

## 📋 功能特性

- ✅ 解析 TOML 配置文件
- ✅ 批量处理英文章节文件（格式：`[[ID 说话者 情绪]]`）
- ✅ 解析中文对照文件（格式：`[[ID]]`）
- ✅ 本地音频文件检查（快速、可靠、无网络依赖）
- ✅ 生成结构化的JSON数据
- ✅ 详细的进度显示和统计信息

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install tomli  # 仅Python < 3.11需要
```

### 2. 准备配置文件

确保你的 `config.toml` 文件格式正确：

```toml
url = "https://hitori-janai.github.io/novels/"
title = "Novels"

[novels.oap_en]
title = "桃子和橙子 英文版"
audio = "books/oap_en/audio/"
cn = "books/oap_en/cn/cn.txt"

[novels.oap_en.chap]
1 = {en = "books/oap_en/0001.txt", title = "第1章 反派？但我是病娇"}
2 = {en = "books/oap_en/0002.txt", title = "第2章 喜欢你喜欢你喜欢你"}
```

### 3. 运行构建脚本

```bash
python build_data.py
```

## 📁 生成的文件

脚本会在 `data/` 目录下生成以下文件：

```
data/
├── novels.json           # 📚 主索引文件
├── oap_en.json          # 📖 书籍内容文件
└── oap_en_audio.json    # 🎵 音频可用性文件
```

### 文件结构说明

#### `novels.json` - 主索引
```json
[
  {
    "id": "oap_en",
    "title": "桃子和橙子 英文版",
    "chapters": [
      {
        "id": "0001",
        "title": "第1章 反派？但我是病娇"
      }
    ]
  }
]
```

#### `oap_en.json` - 书籍内容
```json
{
  "bookId": "oap_en",
  "bookTitle": "桃子和橙子 英文版",
  "chapters": {
    "0001": [
      {
        "id": 1,
        "en": "Chapter 1: Villain? But I'm a Yandere",
        "cn": "第1章 反派？但我是病娇",
        "speaker": "旁白",
        "emotion": "neutral"
      }
    ]
  }
}
```

#### `oap_en_audio.json` - 音频可用性
```json
{
  "bookId": "oap_en",
  "audioBaseUrl": "https://hitori-janai.github.io/novels/books/oap_en/audio/",
  "availability": {
    "0001": [1, 2, 3, 5, 6, 7]  // 有音频的语句ID列表
  }
}
```

## ⚡ 性能优化

- **本地文件检查**: 直接检查本地文件系统，无网络延迟
- **快速构建**: 跳过网络请求，构建速度提升数十倍
- **智能缓存**: 同一章节的语句共享中文内容映射
- **错误容忍**: 文件缺失不会中断整个流程

## 📊 预期输出

```
==================================================
📖 小说数据构建工具
==================================================
✅ 成功加载配置文件: config.toml
🚀 开始构建小说数据...

📚 处理书籍: oap_en - 桃子和橙子 英文版
✅ 解析中文内容: 49305 条语句
  📖 处理章节 0001: 第1章 反派？但我是病娇
✅ 解析英文章节 0001.txt: 100 条语句
  🔍 检查章节 0001 的本地音频文件...
  📻 章节 0001: 100/100 条语句有音频
  📖 处理章节 0002: 第2章 待定
✅ 解析英文章节 0002.txt: 90 条语句
  🔍 检查章节 0002 的本地音频文件...
  📻 章节 0002: 90/90 条语句有音频
✅ 保存书籍内容: data\oap_en.json
✅ 保存音频数据: data\oap_en_audio.json
✅ 保存主索引: data\novels.json

🎉 数据构建完成! 共处理 1 本书
📊 统计信息:
   - 书籍数量: 1
   - 章节总数: 2
   - 生成文件: 3 个

⏱️  总耗时: 0.08 秒
==================================================
```

## 🛠️ 故障排除

### 常见问题

1. **TOML解析错误**
   - 检查 `config.toml` 文件格式是否正确
   - 确保所有字符串都用引号包围

2. **文件不存在错误**
   - 检查英文章节文件路径是否正确
   - 确保中文对照文件存在

3. **音频文件缺失**
   - 检查本地音频目录是否存在
   - 确认音频文件命名格式是否正确

4. **权限错误**
   - 确保对当前目录有写入权限
   - 检查 `data/` 目录是否可以创建

### 调试技巧

- 脚本会输出详细的进度信息和错误提示
- 检查生成的JSON文件是否格式正确
- 使用 `python -c "import json; print(json.load(open('data/novels.json')))"` 验证JSON格式

## 🔄 工作流程

1. **更新内容** → 修改 `config.toml` 添加新章节
2. **运行构建** → `python build_data.py`
3. **部署文件** → 将 `data/` 目录上传到服务器
4. **更新网站** → 网站自动使用新的JSON数据

## 📝 注意事项

- 运行速度很快（本地文件检查）
- 确保本地音频文件目录结构正确
- 生成的JSON文件包含UTF-8字符，确保服务器正确设置编码
- 本地有的音频文件，推送到GitHub后网站一定可用
- 音频检查结果会影响网站的音频按钮显示 