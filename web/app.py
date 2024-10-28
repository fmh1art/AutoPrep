from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)
uploaded_data = None
user_question = None
logical_operators = []
physical_operators = []
physical_operator_status = []
current_operator_index = 0

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global uploaded_data, user_question
    if request.method == 'POST':
        # Get file and question
        file = request.files['file']
        user_question = request.form['question']
        
        # Read the uploaded file into a DataFrame
        uploaded_data = pd.read_csv(file)
        return render_template('display.html', data=uploaded_data.to_html(), question=user_question)
    
    return render_template('upload.html')

@app.route('/examine', methods=['POST'])
def examine_data():
    global logical_operators
    # Here you would examine data quality and generate logical operators
    logical_operators = ['Remove duplicates', 'Fill missing values', 'Standardize columns']
    return render_template('display.html', data=uploaded_data.to_html(), question=user_question, logical_operators=logical_operators)

@app.route('/implement', methods=['POST'])
def implement_operators():
    global physical_operators, physical_operator_status, logical_operators
    # Here you would implement the logical operators into physical ones
    physical_operators = ['SQL: DELETE duplicates', 'SQL: UPDATE missing values', 'SQL: ALTER TABLE for standardization']
    physical_operator_status = [False] * len(physical_operators)  # Initialize checkboxes as unchecked
    return render_template('display.html', data=uploaded_data.to_html(), question=user_question, 
                           physical_operators=physical_operators, physical_operator_status=physical_operator_status, logical_operators=logical_operators)

@app.route('/execute', methods=['POST'])
def execute_operator():
    global current_operator_index, uploaded_data, physical_operators, physical_operator_status, logical_operators

    all_executed = all(physical_operator_status)
    if all_executed:
        return redirect(url_for('generate_code'))

    # Execute the current physical operator
    operator = physical_operators[current_operator_index]
    if operator == 'SQL: DELETE duplicates':
        uploaded_data = uploaded_data
    elif operator == 'SQL: UPDATE missing values':
        uploaded_data = uploaded_data
    elif operator == 'SQL: ALTER TABLE for standardization':
        uploaded_data = uploaded_data
    physical_operator_status[current_operator_index] = True  # Mark the operator as executed
    current_operator_index += 1
    
    
    return render_template('display.html', data=uploaded_data.to_html(), 
                           question=user_question, 
                           physical_operators=physical_operators, 
                           physical_operator_status=physical_operator_status, 
                           current_operator_index=current_operator_index, logical_operators=logical_operators)

@app.route('/reset', methods=['POST'])
def reset():
    global current_operator_index, uploaded_data, physical_operator_status, logical_operators
    current_operator_index = 0
    physical_operator_status = [False] * len(physical_operators)  # Reset checkboxes
    return render_template('display.html', data=uploaded_data.to_html(), question=user_question, 
                           physical_operators=physical_operators, physical_operator_status=physical_operator_status, 
                           current_operator_index=current_operator_index, logical_operators=logical_operators)

@app.route('/generate_code', methods=['GET', 'POST'])
def generate_code():
    global uploaded_data, user_question, final_answer
    extraction_code = f"SELECT * FROM uploaded_data WHERE condition_based_on('{user_question}')"
    final_answer = "final_answer"
    return render_template('final_display.html', data=uploaded_data.to_html(), question=user_question, 
                           extraction_code=extraction_code, final_answer=final_answer)

if __name__ == '__main__':
    app.run(debug=True)
