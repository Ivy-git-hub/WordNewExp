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

app = Quart(__name__)
interpreter = ChineseWordReinterpreter()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/interpret', methods=['POST'])
async def interpret():
    data = await request.get_json()
    word = data.get('word', '')
    model = data.get('model', 'default')
    
    if not word:
        return jsonify({'error': '请输入词语'}), 400
    
    try:
        # 获取选择的LLM适配器
        llm_adapter = None if model == 'default' else get_llm_adapter(model)
        
        # 生成解释
        interpretation = await interpreter.interpret_word(word, llm_adapter)
        
        # 生成SVG
        svg_content = interpreter._create_svg_card(word, interpretation)
        
        return jsonify({
            'svg': svg_content
        })
    except Exception as e:
        return jsonify({'error': f'生成失败：{str(e)}'}), 500

if __name__ == '__main__':
    asyncio.run(app.run(debug=True))
