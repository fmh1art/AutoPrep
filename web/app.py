from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import time

app = Flask(__name__)
uploaded_data = None
user_question = None
logical_operators = []
physical_operators = []
physical_operator_status = []
current_operator_index = 0

def truncate_content(content, max_words=3):
    if isinstance(content, str):  # Check if content is a string
        words = content.split()
        if len(words) > max_words:
            return ' '.join(words[:max_words]) + '...'
        return content
    return str(content)  # Convert non-string types to string

def set_max_row_col(df, max_row=5, max_col=5):
    # set the maximum number of rows and columns to display
    # use ... to indicate that there are more rows and columns
    truncated_df = df.iloc[:max_row, :max_col]
    if len(df) > max_row:
        truncated_df = truncated_df.append(pd.Series(['...'] * len(truncated_df.columns), index=truncated_df.columns), ignore_index=True)
    if len(df.columns) > max_col:
        # add an additional column to indicate that there are more columns
        truncated_df['...'] = ['...'] * len(truncated_df)
    return truncated_df

def return_display_df(df):
    # Apply truncation to each cell
    truncated_data = df.applymap(truncate_content)
    truncated_data = set_max_row_col(truncated_data)
    return truncated_data

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global uploaded_data, user_question
    if request.method == 'POST':
        
        file = request.files['file']
        user_question = request.form['question']
        
        uploaded_data = pd.read_csv(file)

        # Apply truncation to each cell
        truncated_data = return_display_df(uploaded_data)
        
        return render_template('display.html', data=truncated_data, question=user_question)
    
    return render_template('upload.html')

def generate_logical_operators():
    time.sleep(0.2)
    return ['Remove duplicates', 'Fill missing values', 'Standardize columns']

@app.route('/examine', methods=['POST'])
def examine_data():
    global logical_operators
    logical_operators = generate_logical_operators()
    # Apply truncation to each cell
    truncated_data = return_display_df(uploaded_data)
    return render_template('display.html', data=truncated_data, question=user_question, logical_operators=logical_operators)

def generate_physical_operators():
    time.sleep(0.2)
    return ['SQL: DELETE duplicates', 'SQL: UPDATE missing values', 'SQL: ALTER TABLE for standardization']

@app.route('/implement', methods=['POST'])
def implement_operators():
    global physical_operators, physical_operator_status, logical_operators
    # Here you would implement the logical operators into physical ones
    physical_operators = generate_physical_operators()
    physical_operator_status = [False] * len(physical_operators)  # Initialize checkboxes as unchecked
    return render_template('display.html', data=return_display_df(uploaded_data), question=user_question, 
                           physical_operators=physical_operators, physical_operator_status=physical_operator_status, logical_operators=logical_operators)

# @app.route('/execute', methods=['POST'])
# def execute_operator():
#     global current_operator_index, uploaded_data, physical_operators, physical_operator_status, logical_operators

#     all_executed = all(physical_operator_status)
#     if all_executed:
#         return redirect(url_for('table_analyzing'))

#     # Execute the current physical operator
#     operator = physical_operators[current_operator_index]
#     if operator == 'SQL: DELETE duplicates':
#         uploaded_data = uploaded_data
#     elif operator == 'SQL: UPDATE missing values':
#         uploaded_data = uploaded_data
#     elif operator == 'SQL: ALTER TABLE for standardization':
#         uploaded_data = uploaded_data
#     physical_operator_status[current_operator_index] = True  # Mark the operator as executed
#     current_operator_index += 1
    
    
#     return render_template('display.html', data=return_display_df(uploaded_data), 
#                            question=user_question, 
#                            physical_operators=physical_operators, 
#                            physical_operator_status=physical_operator_status, 
#                            current_operator_index=current_operator_index, logical_operators=logical_operators)

@app.route('/execute', methods=['POST'])
def execute_operator():
    global current_operator_index, uploaded_data, physical_operators, physical_operator_status, logical_operators
    all_executed = all(physical_operator_status)
    if all_executed:
        return redirect(url_for('table_analyzing'))
    
    # Execute the current physical operator
    operator = physical_operators[current_operator_index]
    if operator == 'SQL: DELETE duplicates':
        uploaded_data = uploaded_data[list(uploaded_data.columns)[:-1]]
    elif operator == 'SQL: UPDATE missing values':
        uploaded_data = uploaded_data[list(uploaded_data.columns)[:-1]]
    elif operator == 'SQL: ALTER TABLE for standardization':
        uploaded_data = uploaded_data[list(uploaded_data.columns)[:-1]]
    
    physical_operator_status[current_operator_index] = True  # Mark the operator as executed
    current_operator_index += 1
    
    # Return the updated table data along with other information
    return render_template('display.html', 
                           data=return_display_df(uploaded_data), 
                           question=user_question, 
                           physical_operators=physical_operators, 
                           physical_operator_status=physical_operator_status, 
                           current_operator_index=current_operator_index, 
                           logical_operators=logical_operators)


@app.route('/reset', methods=['POST'])
def reset():
    global current_operator_index, uploaded_data, physical_operator_status, logical_operators
    current_operator_index = 0
    physical_operator_status = [False] * len(physical_operators)  # Reset checkboxes
    return render_template('display.html', data=return_display_df(uploaded_data), question=user_question, 
                           physical_operators=physical_operators, physical_operator_status=physical_operator_status, 
                           current_operator_index=current_operator_index, logical_operators=logical_operators)

@app.route('/table_analyzing', methods=['GET', 'POST'])
def table_analyzing():
    global uploaded_data, user_question, final_answer
    return render_template('final_display.html', data=return_display_df(uploaded_data), question=user_question,)


def when_generate_code():
    time.sleep(0.2)
    return "SELECT * FROM uploaded_data WHERE condition_based_on('user_question')"

@app.route('/generate_code', methods=['POST'])
def generate_code():
    global uploaded_data, user_question, final_answer
    extraction_code =  when_generate_code()
    final_answer = "final_answer"
    
    return render_template('final_display.html', data=return_display_df(uploaded_data), question=user_question, 
                           extraction_code=extraction_code, final_answer=final_answer)


# @app.route('/generate_code', methods=['POST'])
# def generate_code():
#     global uploaded_data, user_question, final_answer
#     extraction_code = f"SELECT * FROM uploaded_data WHERE condition_based_on('{user_question}')"
#     final_answer = "final_answer"
#     return render_template('final_display.html', data=return_display_df(uploaded_data), question=user_question, 
#                            extraction_code=extraction_code, final_answer=final_answer)

if __name__ == '__main__':
    app.run(debug=True)
