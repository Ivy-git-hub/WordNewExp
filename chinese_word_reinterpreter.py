#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svgwrite
from dataclasses import dataclass
from typing import List, Tuple
import random
from pathlib import Path

@dataclass
class Style:
    background_color: str
    text_color: str
    accent_color: str
    
class ChineseWordReinterpreter:
    def __init__(self):
        self.styles = ["Oscar Wilde", "Lu Xun", "Luo Yonghua"]
        self.mondrian_colors = ['#FF0000', '#0000FF', '#FFFF00', '#FFFFFF', '#000000']
        try:
            from pypinyin import pinyin, Style
            self.pinyin_converter = pinyin
        except ImportError:
            self.pinyin_converter = None
            
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
        if self.pinyin_converter:
            try:
                py_list = self.pinyin_converter(word, style=Style.TONE)
                return ' '.join([p[0] for p in py_list])
            except:
                return word
        return word
        
    def _translate_word(self, word: str) -> Tuple[str, str]:
        """翻译词语到英文和日文"""
        if word in self.translations:
            return self.translations[word]["en"], self.translations[word]["ja"]
        return word, word
        
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
        width, height = 400, 600
        margin = 40
        
        dwg = svgwrite.Drawing(size=(width, height))
        
        # 背景色
        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(width, height),
            fill='#F5F1EA'  # 米色背景
        ))
        
        # 标题
        title_group = dwg.g()
        # 标题文字
        title_group.add(dwg.text(
            "汉语新解",
            insert=(width/2, margin*1.5),
            text_anchor="middle",
            font_size=28,
            fill='#2C2C2C',
            style="font-family: KaiTi;"
        ))
        
        # 分隔线
        title_group.add(dwg.line(
            start=(margin, margin*2),
            end=(width-margin, margin*2),
            stroke='#2C2C2C',
            stroke_width=0.5
        ))
        dwg.add(title_group)
        
        # 词语展示区
        text_group = dwg.g()
        y_pos = margin*3.5
        
        # 主词
        text_group.add(dwg.text(
            word,
            insert=(width/2, y_pos),
            text_anchor="middle",
            font_size=32,
            fill='#2C2C2C',
            style="font-family: SimSun;"
        ))
        
        # 拼音
        pinyin = self._get_pinyin(word)
        text_group.add(dwg.text(
            pinyin,
            insert=(width/2, y_pos + 30),
            text_anchor="middle",
            font_size=16,
            fill='#666666',
            style="font-family: 'Times New Roman';"
        ))
        
        # 英文翻译
        en_text, jp_text = self._translate_word(word)
        text_group.add(dwg.text(
            en_text,
            insert=(width/2, y_pos + 60),
            text_anchor="middle",
            font_size=16,
            fill='#666666',
            style="font-family: 'Times New Roman';"
        ))
        
        # 日文翻译
        text_group.add(dwg.text(
            jp_text,
            insert=(width/2, y_pos + 90),
            text_anchor="middle",
            font_size=16,
            fill='#666666',
            style="font-family: 'MS Mincho';"
        ))
        
        dwg.add(text_group)
        
        # 解释文本
        interpretation_group = dwg.g()
        y_pos = height/2
        line_height = 35
        
        # 将解释文字按句号和破折号分段
        segments = []
        parts = interpretation.split('，')
        for part in parts:
            if '——' in part:
                before, after = part.split('——')
                if before.strip():
                    segments.append(before.strip() + '，')
                segments.append('——' + after.strip())
            else:
                segments.append(part.strip() + ('，' if part != parts[-1] else ''))
        
        for segment in segments:
            if segment:
                interpretation_group.add(dwg.text(
                    segment,
                    insert=(width/2, y_pos),
                    text_anchor="middle",
                    font_size=18,
                    fill='#2C2C2C',
                    style="font-family: SimSun;"
                ))
                y_pos += line_height
        
        dwg.add(interpretation_group)
        
        return dwg.tostring()
        
    def _wrap_text(self, text: str, chars_per_line: int) -> List[str]:
        """将文本按指定长度换行"""
        lines = []
        # 按逗号分割
        segments = text.split('，')
        current_line = ""
        
        for i, segment in enumerate(segments):
            if len(current_line) + len(segment) <= chars_per_line:
                current_line += segment + ('，' if i < len(segments)-1 else '')
            else:
                if current_line:
                    lines.append(current_line)
                current_line = segment + ('，' if i < len(segments)-1 else '')
        
        if current_line:
            lines.append(current_line)
            
        return lines
        
    def _add_mondrian_background(self, dwg, width, height):
        """Add Mondrian-style background"""
        sections = self._generate_mondrian_sections(width, height)
        for section in sections:
            color = random.choice(self.mondrian_colors)
            dwg.add(dwg.rect(insert=(section[0], section[1]),
                           size=(section[2], section[3]),
                           fill=color,
                           stroke="#000000",
                           stroke_width=2))
                           
    def _generate_mondrian_sections(self, width, height) -> List[Tuple[float, float, float, float]]:
        """Generate Mondrian-style rectangular sections"""
        # Simplified version - just creates a few basic rectangles
        sections = [
            (0, 0, width/2, height/3),
            (width/2, 0, width/2, height/2),
            (0, height/3, width/3, height/3),
            (width/3, height/3, width*2/3, height/3),
            (0, height*2/3, width, height/3)
        ]
        return sections
        
    def interpret(self, word: str) -> str:
        """Main interpretation function"""
        interpretation = self._generate_critical_interpretation(word)
        svg = self._create_svg_card(word, interpretation)
        
        # Save SVG to file
        output_path = Path("output.svg")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg)
            
        return interpretation

def start():
    print("说吧, 他们又用哪个词来忽悠你了?")
    return ChineseWordReinterpreter()

if __name__ == "__main__":
    interpreter = start()
    while True:
        word = input("> ")
        if word.lower() in ["exit", "quit", "退出"]:
            break
        result = interpreter.interpret(word)
        print(f"\n{result}\n")
