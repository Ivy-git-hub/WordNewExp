import os
import asyncio
from quart import Quart, render_template, request, jsonify
from chinese_word_reinterpreter import ChineseWordReinterpreter
from llm_adapter import get_llm_adapter
from dotenv import load_dotenv

# 设置环境变量
os.environ['ZHIPUAI_API_KEY'] = 'fa0f70b4ac5a4a3faaf252cf59830d5e.i1mnIJvhIBI3mDix'
os.environ['QWEN_API_KEY'] = 'sk-3461792543254e99828cf0c1e6e00006'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCsHiT4dkYnWwg0B8Lgdq8SguR0mze_UnQ'

load_dotenv()

# Vercel 处理函数
app = Quart(__name__)
interpreter = ChineseWordReinterpreter()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/interpret', methods=['POST'])
async def interpret():
    data = await request.get_json()
    word = data.get('word', '')
    model = data.get('model', 'zhipuai')
    
    try:
        llm = get_llm_adapter(model)
        interpretation = await interpreter.interpret_word(word, llm)
        return jsonify({'svg': interpretation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel 需要的入口函数
def handler(request):
    return app(request)

if __name__ == '__main__':
    app.run(debug=True)
