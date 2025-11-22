import difflib
from pathlib import Path
from typing import Dict, Optional, Tuple

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

# 假设你的生成器模块在一个名为 pjsk_sticker 的包里
from pjsk_sticker import generator

# 项目说明：
# 此模块提供了基于FastAPI框架的HTTP API服务
# 允许客户端通过HTTP请求生成PJSK风格的表情包图片
# 主要功能包括：接收生成参数、调用生成器模块、返回生成的图片

# 1. 创建 FastAPI 应用实例
app = FastAPI(
    title="Meme Generator API",
    description="一个用于生成 PJSK 风格表情包图片的 API，支持 GET 和 POST 请求。",
    version="1.1.0",
)


FONTS: Dict[str, str] = {
    font.stem.lower(): str(font) for font in Path("assets/fonts").glob("*")
}


# 2. 定义 POST 请求体的数据模型
class GenerateRequest(BaseModel):
    """
    生成表情包请求数据模型 (用于 POST 请求)
    用于接收和验证客户端发送的生成表情包参数
    """

    character: str  # 角色名称或团队名称（例如 'miku', 'l/n', 'ichika'）
    text: str  # 要显示在图片上的文本内容
    character_index: Optional[int] = None  # 角色贴纸的索引，未提供时随机选择
    position: Tuple[int, int] = (20, 10)  # 文本左下角的坐标(x, y)
    text_color: Optional[Tuple[int, int, int]] = (
        None  # 文本颜色RGB元组，未提供时根据角色自动设置
    )
    font_size: int = 50  # 字体大小
    stroke_color: Tuple[int, int, int] = (255, 255, 255)  # 文本描边颜色RGB元组
    stroke_width: int = 4  # 文本描边宽度
    font_path: Optional[str] = None  # 字体文件路径，未提供时自动选择
    rotation_angle: int = 15  # 文本旋转角度（度）

    class Config:
        json_schema_extra = {
            "example": {
                "character": "miku",
                "text": "你好！",
                "font_size": 60,
                "rotation_angle": -10,
            }
        }


# 3. 核心逻辑函数 (供 GET 和 POST 端点共用)
async def _generate_and_respond(params: dict) -> FileResponse:
    """
    内部函数：调用生成器并处理响应和异常。
    """
    try:
        params["character"] = params["character"].lower()
        if "font_path" in params and params["font_path"] is not None:
            params["font_path"] = FONTS.get(
                difflib.get_close_matches(
                    params["font_path"].lower(), FONTS.keys(), n=1
                )[0],
                None,
            )
        # 调用generator.py中的generate函数
        image_path = generator.generate(**params)
        # 使用FileResponse将生成的图片文件作为响应返回
        return FileResponse(image_path, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"服务器资源文件丢失: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发生未知错误: {e}")


# 4. 创建 API 端点 (Endpoints)


@app.get("/", include_in_schema=False)
async def root():
    """根路径，重定向到 API 文档。"""
    return RedirectResponse(url="/docs")


@app.get(
    "/pjsk-sticker",
    response_class=FileResponse,
    tags=["Image Generation"],
    summary="通过GET请求生成表情包图片",
    description=(
        "通过URL查询参数传递所有选项来生成图片。对于元组参数（如 `position`），请重复该参数，"
        "例如 `&position=20&position=10`。"
    ),
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "成功返回生成的图片文件。",
        },
        400: {"description": "请求参数格式错误。"},
        404: {"description": "找不到指定的角色或团队。"},
        500: {"description": "服务器内部错误。"},
    },
)
async def create_meme_get(
    character: str = Query(
        ..., description="角色或团队名称 (例如: 'miku', 'l/n')"
    ),
    text: str = Query(..., description="要显示在图片上的文本"),
    character_index: Optional[int] = Query(
        None, description="角色贴纸的索引 (例如: 1, 2, 3)"
    ),
    position: Optional[Tuple[int, int]] = Query(
        (20, 10),
        description="文本左下角坐标 (x, y)。示例: &position=20&position=10",
    ),
    text_color: Optional[Tuple[int, int, int]] = Query(
        None,
        description=(
            "文本颜色 (R, G, B)。"
            "示例: &text_color=255&text_color=0&text_color=0"
        ),
    ),
    font_size: int = Query(50, description="字体大小"),
    stroke_color: Optional[Tuple[int, int, int]] = Query(
        (255, 255, 255), description="文本描边颜色 (R, G, B)。"
    ),
    stroke_width: int = Query(4, description="文本描边宽度"),
    font_path: Optional[str] = Query(None, description="自定义字体文件的路径"),
    rotation_angle: int = Query(15, description="文本旋转角度"),
) -> FileResponse:
    """
    **通过 GET 请求生成表情包**

    直接在浏览器地址栏或通过简单的脚本即可调用。
    - **必填参数**: `character`, `text`
    - **可选参数**: 其他所有参数都有默认值。
    """
    params = {
        "character": character,
        "text": text,
        "character_index": character_index,
        "position": position,
        "text_color": text_color,
        "font_size": font_size,
        "stroke_color": stroke_color,
        "stroke_width": stroke_width,
        "font_path": font_path,
        "rotation_angle": rotation_angle,
    }
    return await _generate_and_respond(params)


@app.post(
    "/pjsk-sticker",
    response_class=FileResponse,
    tags=["Image Generation"],
    summary="通过POST请求生成表情包图片",
    description="通过JSON请求体传递所有选项来生成图片，适合在应用程序中使用。",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "成功返回生成的图片文件。",
        },
        404: {"description": "找不到指定的角色或团队。"},
        500: {"description": "服务器内部错误。"},
    },
)
async def create_meme_post(request: GenerateRequest) -> FileResponse:
    """
    **通过 POST 请求生成表情包**

    接收包含所有生成参数的 JSON 对象。
    """
    params = request.model_dump()
    return await _generate_and_respond(params)


# 5. 设置服务器启动入口
if __name__ == "__main__":
    print("启动 API 服务器...")
    print("请在浏览器中访问 http://127.0.0.1:8000/docs 查看交互式API文档")
    uvicorn.run(app, host="127.0.0.1", port=8000)
