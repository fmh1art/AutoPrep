from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from utils import return_display_df
from model import generate_logical_operators, generate_physical_operators, generate_final_code

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置一个安全的密钥

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        user_question = request.form.get('question') or request.form.get('question_datalake')
        
        if 'data_source' in request.form:  # Data Lake option
            data_lake_url = request.form.get('data_lake_url')
            top_k = int(request.form.get('top_k'))
            # Add your data lake retrieval logic here
            # For now, we'll just create a sample DataFrame
            uploaded_data = pd.DataFrame({'sample': [data_lake_url, top_k]})
        else:  # File upload option
            file = request.files['file']
            uploaded_data = pd.read_csv(file)
        
        truncated_data = return_display_df(uploaded_data)
        session['uploaded_data'] = uploaded_data.to_json()
        session['user_question'] = user_question
        
        return render_template('display.html', data=truncated_data, question=user_question)
    
    return render_template('upload.html')


@app.route('/examine', methods=['POST'])
def examine_data():
    logical_operators = generate_logical_operators()
    session['logical_operators'] = logical_operators
    uploaded_data = pd.read_json(session['uploaded_data'])
    truncated_data = return_display_df(uploaded_data)
    return render_template('display.html', data=truncated_data, question=session['user_question'], logical_operators=logical_operators)

@app.route('/implement', methods=['POST'])
def implement_operators():
    # Get physical operators
    physical_operators = generate_physical_operators()
    physical_operator_status = [False] * len(physical_operators)
    
    # Get logical operators (add this line)
    logical_operators = session['logical_operators']
    
    # Store in session
    session['physical_operators'] = physical_operators
    session['physical_operator_status'] = physical_operator_status
    session['current_operator_index'] = 0 
    
    uploaded_data = pd.read_json(session['uploaded_data'])
    
    # Pass both logical_operators and physical_operators to template
    return render_template('display.html', 
                         data=return_display_df(uploaded_data), 
                         question=session['user_question'],
                         logical_operators=logical_operators,  # Add this line
                         physical_operators=physical_operators, 
                         physical_operator_status=physical_operator_status)

@app.route('/execute', methods=['POST'])
def execute_operator():
    try:
        # Get data from session
        uploaded_data = pd.read_json(session['uploaded_data'])
        physical_operators = session['physical_operators']
        physical_operator_status = session['physical_operator_status']
        current_operator_index = session.get('current_operator_index', 0)
        logical_operators = session['logical_operators']

        # Check if all operators are executed
        all_executed = all(physical_operator_status)
        if all_executed:
            return redirect(url_for('table_analyzing'))

        # Get current operator
        operator = physical_operators[current_operator_index]

        uploaded_data = uploaded_data[list(uploaded_data.columns)[:-1]]

        # Update status
        physical_operator_status[current_operator_index] = True
        current_operator_index += 1

        # Update session
        session['uploaded_data'] = uploaded_data.to_json()
        session['physical_operator_status'] = physical_operator_status
        session['current_operator_index'] = current_operator_index

        return render_template('display.html',
                            data=return_display_df(uploaded_data),
                            question=session['user_question'],
                            logical_operators=logical_operators,
                            physical_operators=physical_operators,
                            physical_operator_status=physical_operator_status,
                            current_operator_index=current_operator_index)

    except Exception as e:
        # Add error handling
        print(f"Error in execute_operator: {str(e)}, current_operator_index: {current_operator_index}")
        return str(e), 500


@app.route('/reset', methods=['POST'])
def reset():
    session['current_operator_index'] = 0
    session['physical_operator_status'] = [False] * len(session['physical_operators'])
    uploaded_data = pd.read_json(session['uploaded_data'])
    return render_template('display.html', data=return_display_df(uploaded_data), question=session['user_question'], 
                           physical_operators=session['physical_operators'], physical_operator_status=session['physical_operator_status'], 
                           current_operator_index=0)

@app.route('/table_analyzing', methods=['GET', 'POST'])
def table_analyzing():
    uploaded_data = pd.read_json(session['uploaded_data'])
    return render_template('final_display.html', data=return_display_df(uploaded_data), question=session['user_question'])

@app.route('/generate_code', methods=['POST'])
def generate_code():
    uploaded_data = pd.read_json(session['uploaded_data'])
    extraction_code = generate_final_code()
    final_answer = "final_answer"
    
    return render_template('final_display.html', data=return_display_df(uploaded_data), question=session['user_question'], 
                           extraction_code=extraction_code, final_answer=final_answer)

if __name__ == '__main__':
    app.run(debug=True)
