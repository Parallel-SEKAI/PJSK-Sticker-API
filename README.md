<img src="assets/icon.png" alt="Wonderhoy!" align=right />
<div align="center">

# Project Sekai Sticker API

<!-- ![Wonderhoy!](assets/icon.png) -->

_一个PJSK表情包生成API服务_

![stars](https://img.shields.io/github/stars/Parallel-SEKAI/PJSK-Sticker-API?style=flat)
![downloads](https://img.shields.io/github/downloads/Parallel-SEKAI/PJSK-Sticker-API/total)
![Github repo size](https://img.shields.io/github/repo-size/Parallel-SEKAI/PJSK-Sticker-API)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Parallel-SEKAI/PJSK-Sticker-API)](https://github.com/Parallel-SEKAI/PJSK-Sticker-API/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/Parallel-SEKAI/PJSK-Sticker-API)](https://github.com/Parallel-SEKAI/PJSK-Sticker-API/releases)
![last commit](https://img.shields.io/github/last-commit/Parallel-SEKAI/PJSK-Sticker-API?style=flat)
![language](https://img.shields.io/badge/language-Python-blue)

</div>

> 资源来源于网络，仅供学习和交流使用，请在下载后 24 小时内删除。

> [!NOTE]
> 这是一个面向开发者的项目，如果您不想自己搭建服务，可以使用另一个项目 [PJSK-Sticker](https://github.com/Parallel-SEKAI/PJSK-Sticker)

## 项目概述

Project Sekai Sticker API 是一个基于 FastAPI 构建的 HTTP 服务，用于生成 Project Sekai（世界计划彩色舞台）风格的表情包图片。通过简单的 API 调用，您可以自定义角色、文本内容、字体样式等参数，快速生成个性化的表情包。

## 功能特点

- **多种角色支持**：支持 Project Sekai 中的各个角色和团队
- **自定义文本**：可自由设置表情包上的文本内容
- **丰富的样式选项**：可调整文本颜色、字体大小、描边样式和旋转角度
- **自动适配**：根据文本内容自动选择合适的字体
- **随机选择**：可随机选择角色贴纸，增加多样性
- **交互式 API 文档**：提供 Swagger UI 和 ReDoc 两种风格的 API 文档

## 安装与配置

本项目支持两种部署方式：本地 Python 环境和 Docker 容器。

### 系统要求

**本地部署要求：**
- Python 3.8 或更高版本
- 推荐使用 `uv` 作为包管理工具

**Docker 部署要求：**
- Docker 20.10 或更高版本
- Docker Compose 2.0 或更高版本

### 本地安装步骤

1. 克隆代码仓库

```bash
git clone https://github.com/Parallel-SEKAI/PJSK-Sticker-API.git
cd PJSK-Sticker-API
```

2. 安装依赖

```bash
# 使用 uv 安装（推荐）
uv venv
uv sync

# 或使用 pip
python -m venv venv
venv\Scripts\activate  # Windows 环境
source venv/bin/activate  # Linux/Mac 环境
pip install -r requirements.txt
```

3. 下载资源文件

确保 `assets` 目录中包含必要的资源文件：
- 角色贴纸图片
- 字体文件
- 角色数据 JSON 文件

### Docker 部署步骤

1. 克隆代码仓库（如果尚未克隆）

```bash
git clone https://github.com/Parallel-SEKAI/PJSK-Sticker-API.git
cd PJSK-Sticker-API
```

2. 确保资源文件存在

确保 `assets` 目录中包含必要的资源文件，与本地部署相同。

3. 使用 Docker Compose 启动服务

```bash
docker-compose up -d
```

这将构建镜像并启动容器。服务将在 `http://localhost:8000` 上运行。

4. 查看日志（可选）

```bash
docker-compose logs -f
```

5. 停止服务

```bash
docker-compose down
```

### Docker 配置说明

项目包含两个主要的 Docker 配置文件：

- **Dockerfile**：定义了容器镜像的构建过程，包括 Python 环境、依赖安装和应用配置
- **docker-compose.yml**：定义了服务配置，包括端口映射、卷挂载和健康检查

生成的图片默认存储在 Docker 卷中，可以通过调整 `docker-compose.yml` 中的卷配置来修改存储位置。

## 使用方法

### 启动服务器

```bash
# 使用 Python 直接运行
python api.py

# 或使用 uvicorn
uvicorn api:app --host 127.0.0.1 --port 8000
```

启动后，服务器将在 `http://127.0.0.1:8000` 上运行。

### 访问 API 文档

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### API 调用示例

**POST 请求示例**

```bash
curl -X POST "http://127.0.0.1:8000/pjsk-sticker" \
  -H "Content-Type: application/json" \
  -d '{"character": "miku", "text": "你好！", "font_size": 60}'
```

**GET 请求示例**

```bash
curl "http://127.0.0.1:8000/pjsk-sticker?character=miku&text=你好！&font_size=60"
```

**Python 代码示例**

```python
import requests

# POST 请求示例
url = "http://127.0.0.1:8000/pjsk-sticker"
payload = {
    "character": "miku",
    "text": "你好！",
    "font_size": 60,
    "rotation_angle": -10
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    with open("output.png", "wb") as f:
        f.write(response.content)
    print("图片已保存为 output.png")
else:
    print(f"错误: {response.status_code} - {response.text}")

# GET 请求示例
url = "http://127.0.0.1:8000/pjsk-sticker?character=miku&text=你好！&font_size=60"
response = requests.get(url)
if response.status_code == 200:
    with open("output_get.png", "wb") as f:
        f.write(response.content)
    print("图片已保存为 output_get.png")
else:
    print(f"错误: {response.status_code} - {response.text}")
```

## API 文档

### 生成表情包接口

#### POST 方法

**路径**: `/pjsk-sticker`
**方法**: `POST`
**请求体**:

```json
{
  "character": "miku",
  "text": "你好！",
  "character_index": null,
  "position": [20, 10],
  "text_color": null,
  "font_size": 50,
  "stroke_color": [255, 255, 255],
  "stroke_width": 4,
  "font_path": null,
  "rotation_angle": 15
}
```

**参数说明**:
- `character`: 角色名称或团队名称（必需）
- `text`: 要显示的文本内容（必需）
- `character_index`: 角色贴纸索引，未提供时随机选择
- `position`: 文本左下角坐标，默认为 [20, 10]
- `text_color`: 文本颜色RGB值，未提供时根据角色自动设置
- `font_size`: 字体大小，默认为 50
- `stroke_color`: 文本描边颜色RGB值，默认为 [255, 255, 255]
- `stroke_width`: 文本描边宽度，默认为 4
- `font_path`: 字体文件路径，未提供时自动选择
- `rotation_angle`: 文本旋转角度，默认为 15

**响应**:
- `200 OK`: 返回生成的 PNG 图片文件
- `404 Not Found`: 找不到指定的角色或团队
- `500 Internal Server Error`: 服务器内部错误

#### GET 方法

**路径**: `/pjsk-sticker`
**方法**: `GET`

**查询参数**:
- `character`: 角色名称或团队名称（必需）
- `text`: 要显示的文本内容（必需）
- `character_index`: 角色贴纸索引，未提供时随机选择
- `position`: 文本左下角坐标，使用重复参数如 `&position=20&position=10`
- `text_color`: 文本颜色RGB值，使用重复参数如 `&text_color=255&text_color=0&text_color=0`
- `font_size`: 字体大小，默认为 50
- `stroke_color`: 文本描边颜色RGB值，默认使用重复参数
- `stroke_width`: 文本描边宽度，默认为 4
- `font_path`: 字体文件路径，未提供时自动选择
- `rotation_angle`: 文本旋转角度，默认为 15

**响应**:
- `200 OK`: 返回生成的 PNG 图片文件
- `404 Not Found`: 找不到指定的角色或团队
- `500 Internal Server Error`: 服务器内部错误

## 开发指南

### 项目结构

```
PJSK-Sticker-API/
├── api.py              # FastAPI 应用主文件
├── pjsk_sticker/       # 核心模块
│   ├── __init__.py
│   ├── generator.py    # 表情包生成逻辑
│   └── utils.py        # 工具函数
├── assets/             # 资源文件
│   ├── fonts/          # 字体文件
│   ├── pjsk_sticker/   # 角色贴纸图片
│   ├── characters.json     # 角色数据
│   ├── character_stickers.json  # 贴纸索引数据
│   ├── character_colors.json    # 角色配色数据
│   └── icon.png        # 项目图标
├── temp/               # 临时文件输出目录
├── requirements.txt    # 依赖列表
├── ci.py               # CI 检查脚本
└── README.md           # 项目文档
```

### 代码风格

项目使用以下工具确保代码质量：
- `isort`: 代码导入排序
- `Black`: 代码格式化
- `Flake8`: 代码质量检查

运行 CI 检查：

```bash
python ci.py
```

## 贡献指南

欢迎提交 Issues 和 Pull Requests 来改进这个项目！

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请见 LICENSE 文件。

## 致谢

- [SEGA/プロセカ](https://pjsekai.sega.jp/) - Project Sekai 官方
- [xiaocaoooo/pjsk-sticker](https://github.com/xiaocaoooo/pjsk-sticker) - 灵感来源
- [sszzz830/Project_Sekai_Stickers_QQBot](https://github.com/sszzz830/Project_Sekai_Stickers_QQBot)
- [TheOriginalAyaka/sekai-stickers](https://github.com/TheOriginalAyaka/sekai-stickers)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Parallel-SEKAI/PJSK-Sticker-API&type=Date)](https://www.star-history.com/#Parallel-SEKAI/PJSK-Sticker-API&Date)
