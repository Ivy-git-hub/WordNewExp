#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chinese_word_reinterpreter import ChineseWordReinterpreter

interpreter = ChineseWordReinterpreter()
word = "出人头地"
result = interpreter.interpret(word)
print(f"\n词语：{word}")
print(f"解释：{result}")
