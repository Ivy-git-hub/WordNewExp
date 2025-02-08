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
                    {"role": "system", "content": "你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。请直接给出解释，不要加任何引号。"},
                    {"role": "user", "content": f"请用一句话解释{word}这个词，要求：\n1. 批判性地解读这个词背后的社会现象\n2. 使用机智幽默的语言\n3. 可以使用隐喻和讽刺\n4. 长度在50字以内\n5. 直接给出解释，不要加任何引号"}
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
                        {"role": "system", "content": "你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。请直接给出解释，不要加任何引号。"},
                        {"role": "user", "content": f"请用一句话解释{word}这个词，要求：\n1. 批判性地解读这个词背后的社会现象\n2. 使用机智幽默的语言\n3. 可以使用隐喻和讽刺\n4. 长度在50字以内\n5. 直接给出解释，不要加任何引号"}
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
                            "content": "你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。请直接给出解释，不要加任何引号。"
                        },
                        {
                            "role": "user",
                            "content": f"请用一句话解释{word}这个词，要求：\n1. 批判性地解读这个词背后的社会现象\n2. 使用机智幽默的语言\n3. 可以使用隐喻和讽刺\n4. 长度在50字以内\n5. 直接给出解释，不要加任何引号"
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
                    f"""你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。请直接给出解释，不要加任何引号。
                    
                    请用一句话解释{word}这个词，要求：
                    1. 批判性地解读这个词背后的社会现象
                    2. 使用机智幽默的语言
                    3. 可以使用隐喻和讽刺
                    4. 长度在50字以内
                    5. 直接给出解释，不要加任何引号"""
                )
            )
            return response.text
        except Exception as e:
            return f"抱歉，生成解释时出现错误：{str(e)}"

class DeepSeekAdapter(LLMAdapter):
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            print("警告: 未找到 DEEPSEEK_API_KEY 环境变量")
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        print(f"\nDeepSeek 初始化:")
        print(f"API Key 前8位: {self.api_key[:8] if self.api_key else 'None'}")
        print(f"API URL: {self.base_url}")
        
    async def generate_interpretation(self, word: str) -> str:
        try:
            print(f"\nDeepSeek 开始处理词语: {word}")
            
            # 检查 API Key
            if not self.api_key:
                raise ValueError("未设置 DEEPSEEK_API_KEY 环境变量")
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            print("请求头:", {k: v if k != 'Authorization' else v[:20] + '...' for k, v in headers.items()})

            data = {
                "model": "deepseek-chat",  # 使用基础模型
                "messages": [
                    {"role": "system", "content": "你是一个擅长用批判性、机智幽默的方式解读中文词语的AI。你的风格类似于王尔德、鲁迅和骆永华的结合，善于使用隐喻和讽刺。请直接给出解释，不要加任何引号。"},
                    {"role": "user", "content": f"请用一句话解释{word}这个词，要求：\n1. 批判性地解读这个词背后的社会现象\n2. 使用机智幽默的语言\n3. 可以使用隐喻和讽刺\n4. 长度在50字以内\n5. 直接给出解释，不要加任何引号"}
                ],
                "temperature": 0.7,  # 降低温度
                "max_tokens": 100,
                "stream": False
            }
            
            print("请求数据:", json.dumps(data, ensure_ascii=False, indent=2))
            
            print("\n开始发送请求...")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=data) as response:
                    status = response.status
                    print(f"响应状态码: {status}")
                    
                    response_text = await response.text()
                    print(f"原始响应: {response_text}")
                    
                    if status == 402:
                        print("API 调用失败: 付费相关错误，请检查 API Key 的额度和状态")
                        return "抱歉，API 额度不足或未授权，请联系管理员处理"
                    elif status != 200:
                        print(f"API 调用失败: HTTP {status}")
                        try:
                            error_json = json.loads(response_text)
                            error_msg = error_json.get('error_msg', '未知错误')
                            print(f"错误信息: {error_msg}")
                            return f"抱歉，API调用失败：{error_msg}"
                        except:
                            return f"抱歉，API调用失败：HTTP {status}"
                    
                    try:
                        result = json.loads(response_text)
                        print("解析后的响应:", json.dumps(result, ensure_ascii=False, indent=2))
                        
                        if "choices" in result and len(result["choices"]) > 0:
                            content = result["choices"][0]["message"]["content"].strip()
                            print(f"生成的内容: {content}")
                            return content
                        else:
                            print("响应格式异常")
                            return f"抱歉，API返回格式异常：{result.get('message', '未知错误')}"
                    except json.JSONDecodeError as e:
                        print(f"JSON 解析错误: {e}")
                        return f"API返回数据解析失败：{response_text[:100]}"
                        
        except Exception as e:
            import traceback
            print(f"\nDeepSeek 错误详情:")
            print(f"错误类型: {type(e)}")
            print(f"错误信息: {str(e)}")
            print(f"错误堆栈:\n{traceback.format_exc()}")
            return f"抱歉，生成解释时出现错误：{str(e)}"

def get_llm_adapter(model_name: str) -> Optional[LLMAdapter]:
    adapters = {
        'openai': OpenAIAdapter,
        'zhipuai': ZhiPuAdapter,
        'qwen': QwenAdapter,
        'gemini': GeminiAdapter,
        'deepseek': DeepSeekAdapter,
    }
    
    adapter_class = adapters.get(model_name.lower())
    if adapter_class:
        return adapter_class()
    return None
