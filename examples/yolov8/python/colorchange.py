#!/usr/bin/env python
# coding=utf-8
# vim:set fileencoding=utf-8:
"""
@Project ：ultralytics-main-yuv 
@File    ：colorchange.py
@IDE     ：PyCharm 
@Author  ：高筱六和栾昊六
@Date    ：2025/3/3 16:33 
"""
import math
import random
from typing import Tuple, Iterator


def gradient_text(
        text: str,
        start_color: Tuple[int, int, int] = (255, 0, 0),  # 默认红色
        end_color: Tuple[int, int, int] = (0, 0, 255),  # 默认蓝色
        frequency: float = 1.0,
        rainbow: bool = False,
        random_colors: bool = False
) -> str:
    def color_function(t: float) -> Tuple[int, int, int]:
        if rainbow:
            # 彩虹渐变: 使用 HSV 色彩空间
            hue = 360 * t  # Hue 角度范围 0-360
            return hsv_to_rgb(hue, 1, 1)
        elif random_colors:
            return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            # 线性插值 RGB
            def interpolate(start: float, end: float, t: float) -> float:
                return start + (end - start) * (math.sin(math.pi * t * frequency) + 1) / 2

            return tuple(
                round(interpolate(s, e, t)) for s, e in zip(start_color, end_color)
            )

    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return (round((r + m) * 255), round((g + m) * 255), round((b + m) * 255))

    def gradient_gen(length: int) -> Iterator[Tuple[int, int, int]]:
        return (color_function(i / (length - 1)) for i in range(length))

    gradient = gradient_gen(len(text))
    return "".join(
        f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        for char, (r, g, b) in zip(text, gradient)
    )


def colorstr(*input):
    """
    扩展 colorstr，支持 `rainbow` 和 `random` 参数，调用 `gradient_text`
    """
    *args, string = input if len(input) > 1 else ("blue", "bold", input[0])

    if "rainbow" in args:
        return gradient_text(string, rainbow=True)
    elif "random" in args:
        return gradient_text(string, random_colors=True)
    else:
        colors = {
            # 基本颜色
            "black": "\033[30m",  # 黑色
            "red": "\033[31m",  # 红色
            "green": "\033[32m",  # 绿色
            "yellow": "\033[33m",  # 黄色
            "blue": "\033[34m",  # 蓝色
            "magenta": "\033[35m",  # 品红色
            "cyan": "\033[36m",  # 青色
            "white": "\033[37m",  # 白色

            # 亮色
            "bright_black": "\033[90m",  # 亮黑色
            "bright_red": "\033[91m",  # 亮红色
            "bright_green": "\033[92m",  # 亮绿色
            "bright_yellow": "\033[93m",  # 亮黄色
            "bright_blue": "\033[94m",  # 亮蓝色
            "bright_magenta": "\033[95m",  # 亮品红色
            "bright_cyan": "\033[96m",  # 亮青色
            "bright_white": "\033[97m",  # 亮白色

            # 背景色
            "bg_black": "\033[40m",  # 背景黑色
            "bg_red": "\033[41m",  # 背景红色
            "bg_green": "\033[42m",  # 背景绿色
            "bg_yellow": "\033[43m",  # 背景黄色
            "bg_blue": "\033[44m",  # 背景蓝色
            "bg_magenta": "\033[45m",  # 背景品红色
            "bg_cyan": "\033[46m",  # 背景青色
            "bg_white": "\033[47m",  # 背景白色

            # 亮色背景色
            "bg_bright_black": "\033[100m",  # 亮黑色背景
            "bg_bright_red": "\033[101m",  # 亮红色背景
            "bg_bright_green": "\033[102m",  # 亮绿色背景
            "bg_bright_yellow": "\033[103m",  # 亮黄色背景
            "bg_bright_blue": "\033[104m",  # 亮蓝色背景
            "bg_bright_magenta": "\033[105m",  # 亮品红色背景
            "bg_bright_cyan": "\033[106m",  # 亮青色背景
            "bg_bright_white": "\033[107m",  # 亮白色背景

            # 其他样式
            "end": "\033[0m",  # 重置样式
            "bold": "\033[1m",  # 加粗
            "underline": "\033[4m",  # 下划线
            "inverse": "\033[7m",  # 反转前景和背景色
            "hidden": "\033[8m",  # 隐藏文本
            "strikethrough": "\033[9m",  # 删除线
        }
        color_style = "".join(colors[x] for x in args if x in colors)
        return f"{color_style}{string}{colors['end']}"


# # 示例调用
# print(colorstr("rainbow", "Hello, World!"))
# print(colorstr("random", "Hello, Random Colors!"))
