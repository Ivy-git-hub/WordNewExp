import os
from abc import ABC, abstractmethod
from typing import Optional
import openai
from zhipuai import ZhipuAI
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from functools import partial
import aiohttp
import json

load_dotenv()

class LLMAdapter(ABC):
    @abstractmethod
    async def generate_interpretation(self, word: str) -> str:
        pass

class OpenAIAdapter(LLMAdapter):
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.AsyncOpenAI()
        
    async def generate_interpretation(self, word: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。"},
                    {"role": "user", "content": f"请用一句话解释'{word}'这个词，要求：\n1. 批判性地解读这个词背后的社会现象\n2. 使用机智幽默的语言\n3. 可以使用隐喻和讽刺\n4. 长度在50字以内"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"抱歉，生成解释时出现错误：{str(e)}"

class ZhiPuAdapter(LLMAdapter):
    def __init__(self):
        api_key = os.getenv('ZHIPUAI_API_KEY')
        self.client = ZhipuAI(api_key=api_key)
        
    async def generate_interpretation(self, word: str) -> str:
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="glm-4",
                    messages=[
                        {"role": "system", "content": "你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。"},
                        {"role": "user", "content": f"请用一句话解释'{word}'这个词，要求：\n1. 批判性地解读这个词背后的社会现象\n2. 使用机智幽默的语言\n3. 可以使用隐喻和讽刺\n4. 长度在50字以内"}
                    ]
                )
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"抱歉，生成解释时出现错误：{str(e)}"

class QwenAdapter(LLMAdapter):
    def __init__(self):
        self.api_key = os.getenv('QWEN_API_KEY')
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
    async def generate_interpretation(self, word: str) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-SSE": "disable"
            }
            
            data = {
                "model": "qwen-max",
                "input": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。"
                        },
                        {
                            "role": "user",
                            "content": f"请用一句话解释'{word}'这个词，要求：\n1. 批判性地解读这个词背后的社会现象\n2. 使用机智幽默的语言\n3. 可以使用隐喻和讽刺\n4. 长度在50字以内"
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message",
                    "top_p": 0.8,
                    "seed": 1234,
                    "max_tokens": 100,
                    "temperature": 0.8
                }
            }
            
            print(f"Qwen request URL: {self.url}")
            print(f"Qwen request headers: {headers}")
            print(f"Qwen request data: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, headers=headers, json=data) as response:
                    result = await response.json()
                    print(f"Qwen response: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    if response.status != 200:
                        return f"抱歉，API 调用失败：HTTP {response.status} - {result.get('message', '未知错误')}"
                    
                    if "output" in result:
                        if "text" in result["output"]:
                            return result["output"]["text"]
                        elif "choices" in result["output"] and len(result["output"]["choices"]) > 0:
                            return result["output"]["choices"][0]["message"]["content"]
                    return f"抱歉，返回格式异常：{json.dumps(result, ensure_ascii=False)}"
        except Exception as e:
            import traceback
            print(f"Qwen error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return f"抱歉，生成解释时出现错误：{str(e)}"

class GeminiAdapter(LLMAdapter):
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_interpretation(self, word: str) -> str:
        try:
            loop = asyncio.get_running_loop()
            chat = self.model.start_chat(history=[])
            response = await loop.run_in_executor(
                None,
                lambda: chat.send_message(
                    f"""你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。
                    请用一句话解释'{word}'这个词，要求：
                    1. 批判性地解读这个词背后的社会现象
                    2. 使用机智幽默的语言
                    3. 可以使用隐喻和讽刺
                    4. 长度在50字以内"""
                )
            )
            return response.text
        except Exception as e:
            return f"抱歉，生成解释时出现错误：{str(e)}"

def get_llm_adapter(model_name: str) -> Optional[LLMAdapter]:
    adapters = {
        'openai': OpenAIAdapter,
        'zhipuai': ZhiPuAdapter,
        'qwen': QwenAdapter,
        'gemini': GeminiAdapter,
    }
    
    adapter_class = adapters.get(model_name.lower())
    if adapter_class:
        return adapter_class()
    return None
