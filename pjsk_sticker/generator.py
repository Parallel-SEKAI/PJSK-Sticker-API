import json
import os
import random
import re
import tempfile
from time import time
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# 项目说明：
# 此模块提供了生成PJSK风格表情包图片的核心功能
# 包含两个主要函数：_generate(内部核心实现)和generate(对外API接口)


def _generate(
    *,
    background_path: str,
    text: str,
    position: Tuple[int, int],
    text_color: Tuple[int, int, int],
    font_size: int,
    stroke_color: Tuple[int, int, int],
    stroke_width: int,
    font_path: str,
    rotation_angle: int,
    output_path: str,
):
    """
    功能描述：生成带有自定义文本和样式的表情包图片
    参数说明：
        background_path: str - 背景图片文件的路径
        text: str - 要添加到图片上的文本内容，支持多行（使用\n分隔）
        position: Tuple[int, int] - 文本左下角的起始坐标(x, y)
        text_color: Tuple[int, int, int] - 文本颜色的RGB元组
        font_size: int - 字体大小
        stroke_color: Tuple[int, int, int] - 文本描边颜色的RGB元组
        stroke_width: int - 文本描边的宽度
        font_path: str - 字体文件的路径
        rotation_angle: int - 文本的旋转角度（度）
        output_path: str - 输出图片的保存路径
    返回值：str - 生成的图片的绝对路径
    异常说明：
        FileNotFoundError - 当背景图片或字体文件不存在时抛出
        ValueError - 当字体加载失败时抛出
    """
    # print("\n".join([f"{k}: {v}" for k, v in locals().items()]))

    # Ensure the file paths exist
    if not os.path.exists(background_path):
        raise FileNotFoundError(
            f"Background image not found at {background_path}"
        )
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found at {font_path}")

    # 1. Open the background image and convert to RGBA
    base_image = Image.open(background_path).convert("RGBA")

    # 2. Load the font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise ValueError(
            f"Failed to load font from {font_path}. Please check the path."
        )

    # 3. Create a transparent layer to draw the text on
    text_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_layer)

    # 4. Draw the text with stroke
    lines = text.split("\n")
    line_y = position[1]

    for line in lines:
        draw.text(
            (position[0], line_y),
            line,
            font=font,
            fill=text_color,
            stroke_fill=stroke_color,
            stroke_width=stroke_width,
        )
        bbox = draw.textbbox((position[0], line_y), line, font=font)
        text_height = bbox[3] - bbox[1]
        line_y += text_height

    # 5. Rotate the text layer
    if rotation_angle != 0:
        rotated_text_layer = text_layer.rotate(
            rotation_angle, expand=True, resample=Image.BICUBIC  # type: ignore
        )
    else:
        rotated_text_layer = text_layer

    # 6. Paste the rotated text layer onto the background image
    rotated_width, rotated_height = rotated_text_layer.size
    paste_x = position[0] - (rotated_width - text_layer.width) // 2
    paste_y = position[1] - (rotated_height - text_layer.height) // 2

    if rotation_angle == 0:
        final_image = Image.alpha_composite(base_image, rotated_text_layer)
    else:
        temp_composite_layer = Image.new(
            "RGBA", base_image.size, (255, 255, 255, 0)
        )
        temp_composite_layer.paste(
            rotated_text_layer, (paste_x, paste_y), rotated_text_layer
        )
        final_image = Image.alpha_composite(base_image, temp_composite_layer)

    # 7. Save the final image
    final_image.save(output_path, "PNG")
    return os.path.abspath(output_path)


# 正则表达式模式：用于检测日文假名（平假名和片假名）
# 用于根据文本内容自动选择合适的字体
KANA_PATTERN = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]")


def generate(
    *,
    character: str,
    text: str,
    character_index: Optional[int] = None,
    position: Tuple[int, int] = (20, 10),
    text_color: Optional[Tuple[int, int, int]] = None,
    font_size: int = 50,
    stroke_color: Tuple[int, int, int] = (255, 255, 255),
    stroke_width: int = 4,
    font_path: Optional[str] = None,
    rotation_angle: int = 15,
    output_path: Optional[str] = None,
):
    """
    功能描述：通过角色名称生成表情包，并应用默认样式
    参数说明：
        character: str - 角色名称 (例如 "miku", "ichika") 或团队名称 (例如 "l/n", "vbs")
                     用于确定背景图片和默认文本颜色
        text: str - 要写在图片上的文本内容
        character_index: Optional[int] - 角色贴纸的索引，未提供时随机选择一个
        position: Tuple[int, int] - 文本左下角的坐标 (x, y)，默认为 (20, 10)
        text_color: Optional[Tuple[int, int, int]] - 文本颜色的RGB元组，未提供时根据角色自动设置
        font_size: int - 字体大小，默认为50
        stroke_color: Tuple[int, int, int] - 文本描边颜色的RGB元组，默认为(255, 255, 255)
        stroke_width: int - 文本描边的宽度，默认为4
        font_path: Optional[str] - 字体文件的路径，未提供时根据文本内容自动选择
        rotation_angle: int - 文本的旋转角度，默认为15
        output_path: Optional[str] - 输出图片的保存路径，未提供时自动生成
    返回值：str - 保存的输出图片的绝对路径
    异常说明：
        ValueError - 当找不到指定的角色或团队时抛出
        FileNotFoundError - 当必要的资源文件不存在时抛出
    """
    # 1. 加载角色相关的 JSON 数据
    # 这三个JSON文件包含了角色信息、贴纸索引范围和角色配色方案
    with open("assets/characters.json", "r", encoding="utf-8") as f:
        characters_data = json.load(f)
    with open("assets/character_stickers.json", "r", encoding="utf-8") as f:
        character_stickers_data = json.load(f)
    with open("assets/character_colors.json", "r", encoding="utf-8") as f:
        character_colors_data = json.load(f)

    # 2. 根据输入的 character 字符串查找角色信息
    # 先尝试精确匹配角色名称，如果找不到则检查是否为团队名称
    found_character_roma = None
    character_team = None
    input_char_lower = character.lower()

    # 首先，搜索精确的角色名称
    for team_info in characters_data.values():
        for char_data in team_info.get("characters", []):
            if input_char_lower in char_data.get("names", []):
                found_character_roma = char_data["roma"]
                character_team = team_info["shortname"]
                break
        if found_character_roma:
            break

    # 如果没找到，再检查是否为团队名称
    if not found_character_roma:
        for team_info in characters_data.values():
            if input_char_lower in team_info.get("names", []):
                # 从团队中随机选择一个角色
                if team_info.get("characters"):
                    char_data = random.choice(team_info["characters"])
                    found_character_roma = char_data["roma"]
                    character_team = team_info["shortname"]
                    break

    if not found_character_roma or not character_team:
        raise ValueError(f"Character or team '{character}' not found.")

    # 3. 确定贴纸索引
    final_character_index = character_index
    if final_character_index is None:
        max_index = character_stickers_data.get(found_character_roma, 1)
        final_character_index = random.randint(1, max_index)

    # 4. 构建背景图片路径
    background_path = (
        f"assets/pjsk_sticker/{character_team}/{found_character_roma}/"
        f"{found_character_roma}{final_character_index}.png"
    )

    # 5. 确定文本颜色（如果未提供）
    final_text_color = text_color
    if final_text_color is None:
        color_list = character_colors_data.get(found_character_roma, [0, 0, 0])
        final_text_color = tuple(color_list)

    # 6. 确定字体路径（如果未提供）
    final_font_path = font_path
    if final_font_path is None:
        fonts = [
            "assets/fonts/ShangShouFangTangTi.ttf",
            "assets/fonts/YurukaStd.ttf",
        ]
        if re.search(KANA_PATTERN, text):
            final_font_path = fonts[1]
        else:
            final_font_path = fonts[0]

    # 7. 确定输出路径（如果未提供）
    final_output_path = output_path
    if final_output_path is None:
        final_output_path = (
            f"{tempfile.gettempdir()}/pjsk_sticker/{time()}.png"
        )
        os.makedirs(os.path.dirname(final_output_path), exist_ok=True)

    # 8. 调用核心生成函数
    return _generate(
        background_path=background_path,
        text=text,
        position=position,
        text_color=final_text_color,
        font_size=font_size,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        font_path=final_font_path,
        rotation_angle=rotation_angle,
        output_path=final_output_path,
    )
