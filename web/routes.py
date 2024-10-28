# web/routes.py

from flask import render_template, request, redirect, url_for, session
from web.forms import UploadForm
from web.utils import data_analyze, function_pool, exe_function, gen_code, exe_code, distribute_logical_operators, execute_physical_operator, handle_error
import pandas as pd
from werkzeug.utils import secure_filename
import os

def init_app(app):
    @app.route('/')
    def upload():
        form = UploadForm()
        return render_template('pages/upload.html', form=form)

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
        
        df = pd.read_csv(file_path) 
        session['dataframe'] = df.to_dict()  
        
        quality_issues = data_analyze(df)
        session['quality_issues'] = quality_issues  
        
        return redirect(url_for('display_question_and_table'))

    @app.route('/display_question_and_table')
    def display_question_and_table():
        df = pd.DataFrame(session.get('dataframe'))
        question = session.get('question')
        return render_template('pages/original_table_and_question.html', data=df.to_html(classes="table table-striped"), question=question)

    @app.route('/execute_physical_operators')
    def execute_physical_operators():
        df = pd.DataFrame(session.get('dataframe'))
        physical_operators = session.get('physical_operators', [])
        executed_operators = []
        
        for operator in physical_operators:
            try:
                df = execute_physical_operator(df, operator)
                executed_operators.append(operator)
            except Exception as e:
                error_message = handle_error(str(e))
                executed_operators.append(error_message)
        
        session['dataframe'] = df.to_dict()
        session['executed_operators'] = executed_operators
        
        return redirect(url_for('display_executed_operators'))

    @app.route('/display_executed_operators')
    def display_executed_operators():
        df = pd.DataFrame(session.get('dataframe'))
        executed_operators = session.get('executed_operators', [])
        return render_template('pages/executed_operators.html', data=df.to_html(classes="table table-striped"), executed_operators=executed_operators)

    @app.route('/planner_analysis')
    def planner_analysis():
        question = session.get('question')
        df = pd.DataFrame(session.get('dataframe'))
        
        # Simulate Planner's analysis and provide logical operation operators
        logical_operators = ["Augment", "Normalize", "Filter"]  # Example logical operators
        
        # Distribute logical operators to expert models and generate physical operators
        physical_operators = distribute_logical_operators(logical_operators)
        session['physical_operators'] = physical_operators
        
        return render_template('pages/planner_analysis.html', question=question, data=df.to_html(classes="table table-striped"), logical_operators=logical_operators, physical_operators=physical_operators)

    @app.route('/quality_issues')
    def quality_issues():
        quality_issues = session.get('quality_issues', [])
        return render_template('pages/quality_issues.html', issues=quality_issues)
    
    @app.route('/function_options/<issue_id>')
    def function_options(issue_id):
        options = function_pool(issue_id)
        return render_template('pages/function_options.html', options=options, issue_id=issue_id)
    
    @app.route('/apply_function/<issue_id>/<function_id>')
    def apply_function(issue_id, function_id):
        df = pd.DataFrame(session.get('dataframe'))
        df_clean = exe_function(df)
        session['dataframe'] = df_clean.to_dict()  
        
        return redirect(url_for('clean_data'))
    
    @app.route('/clean_data')
    def clean_data():
        df_clean = pd.DataFrame(session.get('dataframe'))
        return render_template('pages/clean_data.html', data=df_clean.to_html(classes="table table-striped"))
    
    @app.route('/code_result')
    def code_result():
        code = gen_code(session.get('quality_issues'))
        answer = exe_code(code)
        return render_template('pages/code_result.html', code=code, answer=answer)