from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'

# 自动创建上传目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def data_analyze(df):
    return ["A demo for data quality issues"]

def function_pool(issue_id):
    return ["A demo for function options"]

def exe_function(df):
    return df

def gen_code(quality_issues):
    return "A demo for code generation"

def exe_code(code):
    return "A demo for code execution"

@app.route('/')
def upload():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('upload'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('upload'))
    
    question = request.form.get('question')
    session['question'] = question
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # 使用pandas读取文件
    df = pd.read_csv(file_path)  # 假设是CSV格式，支持其他格式的话可以调整
    session['dataframe'] = df.to_dict()  # 转换为dict并存入session
    
    # 分析数据质量问题
    quality_issues = data_analyze(df)
    session['quality_issues'] = quality_issues  # 存储分析结果
    
    # 显示原始表格和问题
    return render_template('original_table_and_question.html', data=df.to_html(classes="table table-striped"), question=question)

@app.route('/quality_issues')
def quality_issues():
    quality_issues = session.get('quality_issues', [])
    return render_template('quality_issues.html', issues=quality_issues)

@app.route('/function_options/<issue_id>')
def function_options(issue_id):
    # 获取对应数据质量问题的解决方案
    options = function_pool(issue_id)
    return render_template('function_options.html', options=options, issue_id=issue_id)

@app.route('/apply_function/<issue_id>/<function_id>')
def apply_function(issue_id, function_id):
    # 使用选定的函数处理数据质量问题
    df = pd.DataFrame(session.get('dataframe'))
    df_clean = exe_function(df)
    session['dataframe'] = df_clean.to_dict()  # 更新干净数据
    
    return redirect(url_for('clean_data'))

@app.route('/clean_data')
def clean_data():
    df_clean = pd.DataFrame(session.get('dataframe'))
    return render_template('clean_data.html', data=df_clean.to_html(classes="table table-striped"))

@app.route('/code_result')
def code_result():
    code = gen_code(session.get('quality_issues'))
    answer = exe_code(code)
    return render_template('code_result.html', code=code, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
