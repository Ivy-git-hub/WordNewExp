#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svgwrite
from dataclasses import dataclass
from typing import List, Tuple, Optional
import random
from pathlib import Path
import asyncio
from pypinyin import pinyin, Style as PinyinStyle
from llm_adapter import LLMAdapter

@dataclass
class Style:
    background_color: str
    text_color: str
    accent_color: str
    
class ChineseWordReinterpreter:
    def __init__(self):
        self.styles = ["Oscar Wilde", "Lu Xun", "Luo Yonghua"]
        self.pinyin_converter = pinyin
            
        # 常用词翻译字典
        self.translations = {
            "出人头地": {
                "en": "stand out from the crowd",
                "ja": "頭角を現す"
            },
            "委婉": {
                "en": "tactful",
                "ja": "婉曲"
            },
            "效率": {
                "en": "efficiency",
                "ja": "効率"
            },
            "会议": {
                "en": "meeting",
                "ja": "会議"
            },
            "加班": {
                "en": "overtime",
                "ja": "残業"
            },
            "团建": {
                "en": "team building",
                "ja": "チームビルディング"
            }
        }
            
    def _get_pinyin(self, word: str) -> str:
        """获取拼音"""
        try:
            py_list = self.pinyin_converter(word, style=PinyinStyle.TONE)
            return ' '.join([p[0] for p in py_list])
        except:
            return word
        
    def _translate_word(self, word: str) -> Tuple[str, str]:
        """翻译词语到英文和日文"""
        if word in self.translations:
            return self.translations[word]["en"], self.translations[word]["ja"]
        return word, word
        
    async def interpret_word(self, word: str, llm_adapter: Optional[LLMAdapter] = None) -> str:
        """使用LLM生成解释"""
        if llm_adapter:
            try:
                interpretation = await llm_adapter.generate_interpretation(word)
                if interpretation and not interpretation.startswith("抱歉"):
                    return interpretation
            except Exception as e:
                print(f"Error generating interpretation: {e}")
        
        # 如果没有LLM或LLM失败，使用默认生成方法
        return self._generate_critical_interpretation(word)
        
    def _generate_critical_interpretation(self, word: str) -> str:
        """Generate a witty and critical interpretation"""
        interpretations = {
            "委婉": "刺向他人时, 决定在剑刃上撒上止痛药。",
            "效率": "用最快的速度完成错误的事情。",
            "会议": "一群人坐在一起，互相浪费时间的艺术。",
            "加班": "用生命为资本家的游艇添砖加瓦。",
            "团建": "强制性的快乐，预算内的友谊。",
            "出人头地": "在一个人人低头的时代，有人选择抬起头来 —— 然后发现自己成了靶子。"
        }
        
        if word in interpretations:
            return interpretations[word]
            
        # Generate a new interpretation based on word characteristics
        return f"在这个荒诞的世界里，'{word}'不过是一个美丽的谎言，" \
               f"我们都在用它来粉饰太平，掩盖真相。"

    def _create_svg_card(self, word: str, interpretation: str) -> str:
        """Generate SVG card with interpretation"""
        # 获取拼音和翻译
        pinyin = self._get_pinyin(word)
        en_trans, ja_trans = self._translate_word(word)
        
        # 创建SVG
        dwg = svgwrite.Drawing(size=("800px", "400px"))
        
        # 设置样式
        style = Style(
            background_color="#F5F1EA",
            text_color="#2C2C2C",
            accent_color="#4A4A4A"
        )
        
        # 背景
        dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"),
                        fill=style.background_color))
        
        # 标题
        dwg.add(dwg.text("汉语新解",
                        insert=("50%", "50px"),
                        text_anchor="middle",
                        fill=style.accent_color,
                        style="font-family: SimSun, serif; font-size: 24px;"))
        
        # 分隔线
        dwg.add(dwg.line(start=("20%", "70px"), end=("80%", "70px"),
                        stroke=style.accent_color,
                        stroke_width=1))
        
        # 词语
        dwg.add(dwg.text(word,
                        insert=("50%", "120px"),
                        text_anchor="middle",
                        fill=style.text_color,
                        style="font-family: SimSun, serif; font-size: 32px; font-weight: bold;"))
        
        # 拼音
        dwg.add(dwg.text(pinyin,
                        insert=("50%", "150px"),
                        text_anchor="middle",
                        fill=style.accent_color,
                        style="font-family: SimSun, serif; font-size: 16px;"))
        
        # 翻译
        dwg.add(dwg.text(en_trans,
                        insert=("50%", "180px"),
                        text_anchor="middle",
                        fill=style.accent_color,
                        style="font-family: SimSun, serif; font-size: 16px;"))
        
        dwg.add(dwg.text(ja_trans,
                        insert=("50%", "210px"),
                        text_anchor="middle",
                        fill=style.accent_color,
                        style="font-family: SimSun, serif; font-size: 16px;"))
        
        # 解释文本
        # 将文本分成多行
        max_chars_per_line = 25
        lines = []
        current_line = ""
        
        for char in interpretation:
            if len(current_line) >= max_chars_per_line and char in "，。！？":
                lines.append(current_line + char)
                current_line = ""
            else:
                current_line += char
                
        if current_line:
            lines.append(current_line)
            
        # 添加解释文本
        y_pos = 280
        for line in lines:
            dwg.add(dwg.text(line,
                            insert=("50%", f"{y_pos}px"),
                            text_anchor="middle",
                            fill=style.text_color,
                            style="font-family: SimSun, serif; font-size: 18px;"))
            y_pos += 30
            
        return dwg.tostring()
        
    async def interpret(self, word: str, llm_adapter: Optional[LLMAdapter] = None) -> str:
        """Main interpretation function"""
        interpretation = await self.interpret_word(word, llm_adapter)
        svg = self._create_svg_card(word, interpretation)
        
        # Save SVG to file
        output_path = Path("output.svg")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
            
        return svg

def start():
    print("说吧, 他们又用哪个词来忽悠你了?")
    return ChineseWordReinterpreter()

if __name__ == "__main__":
    interpreter = start()
    while True:
        word = input("> ")
        if word.lower() in ["exit", "quit", "退出"]:
            break
        result = asyncio.run(interpreter.interpret(word))
        print(f"\n{result}\n")
