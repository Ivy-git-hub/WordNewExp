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

    def _wrap_text(self, text: str, max_chars_per_line: int) -> List[str]:
        """
        将文本按照最大字符数换行，确保不会超出SVG范围
        """
        # 移除多余的空格
        text = ' '.join(text.split())
        
        # 标点符号列表（在这些符号后优先换行）
        punctuations = '。，；！？、'
        
        lines = []
        current_line = ''
        
        for char in text:
            current_line += char
            
            # 如果当前行达到最大长度或遇到标点符号
            if len(current_line) >= max_chars_per_line or char in punctuations:
                lines.append(current_line)
                current_line = ''
        
        # 添加最后一行（如果有）
        if current_line:
            lines.append(current_line)
        
        return lines

    def _create_svg_card(self, word: str, interpretation: str) -> str:
        # 创建SVG画布，固定尺寸 200x240
        width = 200
        height = 240
        dwg = svgwrite.Drawing(size=('100%', '100%'), viewBox=f'0 0 {width} {height}')
        
        # 设置背景为米色
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#FAF6F1'))
        
        # 添加标题
        dwg.add(dwg.text('汉语新解', insert=(width/2, 20), font_size=8, font_family='Noto Sans SC', 
                        text_anchor='middle', fill='#333333'))
        
        # 添加分隔线
        dwg.add(dwg.line(start=(width*0.15, 28), end=(width*0.85, 28), 
                        stroke='#333333', stroke_width=0.5))
        
        # 添加汉字
        dwg.add(dwg.text(word, insert=(width/2, 65), font_size=20, font_family='Noto Sans SC', 
                        text_anchor='middle', fill='#333333'))
        
        # 添加拼音
        pinyin = self._get_pinyin(word)
        dwg.add(dwg.text(pinyin, insert=(width/2, 85), font_size=8, font_family='Noto Sans SC', 
                        text_anchor='middle', fill='#666666'))
        
        # 添加解释文字
        interpretation = interpretation.strip('"')  # 去掉可能存在的双引号
        
        # 计算每行最大字符数（根据字体大小和SVG宽度）
        max_chars = int((width * 0.7) / 8)  # 8px 是字体大小，留出 30% 边距
        lines = self._wrap_text(interpretation, max_chars)
        
        # 计算文本总高度和行间距
        available_height = height - 110  # 110 是文本开始的y坐标
        total_lines = len(lines)
        line_height = min(16, available_height / (total_lines + 1))  # 确保至少留出一行的空间
        
        # 添加文字
        y = 110
        for i, line in enumerate(lines):
            if y + line_height > height - 10:  # 留出底部 10px 的边距
                break
            dwg.add(dwg.text(line, insert=(width/2, y), font_size=8, font_family='Noto Sans SC', 
                            text_anchor='middle', fill='#333333'))
            y += line_height
        
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
