import os
import asyncio
from quart import Quart, render_template, request, jsonify
from chinese_word_reinterpreter import ChineseWordReinterpreter
from llm_adapter import get_llm_adapter
from dotenv import load_dotenv

# 加载环境变量
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
    model = data.get('model', 'zhipuai')  # 默认使用智谱AI
    
    print(f"\n开始处理请求：词语 = {word}, 模型 = {model}")
    
    if not word:
        return jsonify({'error': '请输入词语'}), 400
    
    try:
        # 获取选择的LLM适配器
        print(f"正在初始化 {model} 适配器...")
        llm_adapter = get_llm_adapter(model)
        if not llm_adapter:
            return jsonify({'error': '不支持的模型类型'}), 400
        
        # 生成解释
        print("开始生成解释...")
        interpretation = await interpreter.interpret_word(word, llm_adapter)
        print(f"生成的解释: {interpretation}")
        
        # 生成SVG
        print("开始生成SVG...")
        svg_content = interpreter._create_svg_card(word, interpretation)
        print("SVG生成完成")
        
        return jsonify({
            'svg': svg_content
        })
    except Exception as e:
        import traceback
        print("\n发生错误:")
        print(f"错误类型: {type(e)}")
        print(f"错误信息: {str(e)}")
        print("错误堆栈:")
        print(traceback.format_exc())
        return jsonify({'error': f'生成失败：{str(e)}'}), 500

if __name__ == '__main__':
    import hypercorn.asyncio
    import hypercorn.config
    
    config = hypercorn.config.Config()
    config.bind = ["0.0.0.0:5000"]
    config.use_reloader = True
    
    asyncio.run(hypercorn.asyncio.serve(app, config))
