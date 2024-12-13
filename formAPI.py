from flask import Flask, request, jsonify
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
from sqlalchemy import text
import random
import string
from flask_cors import CORS, cross_origin
import google.generativeai as genai

app = Flask(__name__)

cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

# Initialize Flask app


# Hardcoded values
INSTANCE_CONNECTION_NAME = "<fillin>"  # Replace with your instance connection name
DB_USER = "<fillin>"  # Replace with your database username
DB_PASS = "<fillin>"  # Replace with your database password
DB_NAME = "<fillin>"  # Replace with your database name
USE_PRIVATE_IP = False  # Set to True if using private IP

def connect_with_connector():
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.
    Uses the Cloud SQL Python Connector package.
    """
    ip_type = IPTypes.PRIVATE if USE_PRIVATE_IP else IPTypes.PUBLIC

    # Initialize the Cloud SQL connector
    connector = Connector(ip_type)
    
    # Connection function
    def getconn():
        conn = connector.connect(
            INSTANCE_CONNECTION_NAME,
            "pymysql",
            user=DB_USER,
            password=DB_PASS,
            db=DB_NAME,
        )
        return conn

    # Create SQLAlchemy connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return pool

# Utility function to generate random alphanumeric string for form_mapping_id
def generate_form_id(length=7):
    # return 'pushpamovie2'
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Endpoint to create a new form
@app.route('/createForm', methods=['POST'])
def create_form():
    data = request.get_json()  # Get JSON data from the request

    print('create form called')
    print('data')
    print(data)

    if not isinstance(data, list) or not data:
        return jsonify({'error': 'Input should be a non-empty list of JSON objects'}), 400
    
    # form_id = data[0].get('form_id')
    
    # # Ensure the form_id is consistent across all entries
    # if not form_id:
    #     return jsonify({'error': 'Missing form_id'}), 400

    print('form id being created')
    
    form_id = generate_form_id()

    print(form_id)


    # Generate form_mapping_id
    # form_mapping_id = generate_form_mapping_id()

    try:
        # Connect to the database
        engine = connect_with_connector()
        with engine.connect() as conn:
            # Insert data into formdata table
            print('inserting data')
            
            insert_formdata_query = """
            INSERT INTO formdata (form_id, questiontype, question, options, ratings) VALUES
            (:form_id, :questiontype, :question, :options, :ratings)
            """

            # Loop over each entry and insert them into formdata
            for entry in data:
                print(entry)
                questiontype = entry.get('questiontype')
                question = entry.get('question')
                options = entry.get('options')
                ratings = entry.get('ratings')

                if not questiontype or not question or not options or not ratings:
                    return jsonify({'error': 'Missing required fields for one of the entries'}), 400

                # Insert each entry into formdata
                conn.execute(text(insert_formdata_query), {
                    'form_id': form_id,
                    'questiontype': questiontype,
                    'question': question,
                    'options': options,
                    'ratings': ratings
                })
                print('done')

            # Insert form_id and form_mapping_id into formmappings table
            # insert_mapping_query = """
            # INSERT INTO formmappings (form_id, form_mapping_id) VALUES
            # (:form_id, :form_mapping_id)
            # """
            # conn.execute(text(insert_mapping_query), {'form_id': form_id, 'form_mapping_id': form_mapping_id})
            
            # Commit the transaction
            print('before commit')
            conn.commit()
            
            return jsonify({
                'message': 'Form created successfully.',
                'form_mapping_id': form_id
            }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to use a form
@app.route('/useForm/<form_id>', methods=['GET'])
def use_form(form_id):
    print('use form called')
    try:
        # Connect to database
        engine = connect_with_connector()
        with engine.connect() as conn:
            print('getting data')
            # Fetch form_id using form_mapping_id
            # select_mapping_query = """
            # SELECT form_id FROM formmappings WHERE form_mapping_id = :form_mapping_id
            # """
            # result = conn.execute(text(select_mapping_query), {'form_mapping_id': form_mapping_id})
            # mapping_row = result.fetchone()
            
            # if not mapping_row:
            #     return jsonify({'error': 'Form mapping not found'}), 404

            # form_id = mapping_row[0]
            
            # Fetch all rows from formdata for the form_id
            select_formdata_query = """
            SELECT * FROM formdata WHERE form_id = :form_id
            """
            result = conn.execute(text(select_formdata_query), {'form_id': form_id})
            rows = result.fetchall()

            # Format the data as a list of dictionaries
            formdata = []
            for row in rows:
                formdata.append({
                    'id': row[0],
                    'form_id': row[1],
                    'questiontype': row[2],
                    'question': row[3],
                    'options': row[4],
                    'ratings': row[5]
                })

            return jsonify(formdata), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submitForm', methods=['POST'])
def submit_form():
    print('submit form called')
    data = request.get_json()  # Get the JSON data from the request

    print('data')
    print(data)
    
    # Validate input structure
    if not isinstance(data, dict):
        return jsonify({'error': 'Input should be a dictionary'}), 400
    
    form_id = data.get('form_id')
    responses = data.get('responses')
    
    if not form_id or not responses:
        return jsonify({'error': 'form_id and responses are required'}), 400

    try:
        # Connect to the database
        engine = connect_with_connector()
        with engine.connect() as conn:
            
            # Process each response
            for response in responses:
                question_id = response.get('question_id')
                answer = response.get('answer')
                
                if not question_id or answer is None:
                    return jsonify({'error': 'Missing question_id or answer for one of the responses'}), 400
                
                # Select the question from formdata using question_id
                select_question_query = """
                SELECT question FROM formdata WHERE form_id = :form_id AND id = :question_id
                """
                result = conn.execute(text(select_question_query), {'form_id': form_id, 'question_id': question_id})
                question_row = result.fetchone()

                if not question_row:
                    return jsonify({'error': f'Question with id {question_id} not found for the form_id {form_id}'}), 404
                
                question = question_row[0]  # Extract the actual question
                
                # Insert the response into the formresponses table
                insert_response_query = """
                INSERT INTO formresponses (form_id, question_id, actual_question, answer) 
                VALUES (:form_id, :question_id, :actual_question, :answer)
                """
                conn.execute(text(insert_response_query), {
                    'form_id': form_id,
                    'question_id': question_id,
                    'actual_question': question,
                    'answer': answer
                })

            # Commit the transaction
            conn.commit()
            
            return jsonify({'message': 'Form responses submitted successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get the summary of all responses for a given form
@app.route('/showsummary/<form_id>', methods=['GET'])
def show_summary(form_id):
    print(f"Fetching summary for form_id: {form_id}")
    try:
        # Connect to the database
        engine = connect_with_connector()
        with engine.connect() as conn:
            # Fetch all responses for the given form_id from formresponses table
            select_responses_query = """
            SELECT question_id, actual_question, answer FROM formresponses WHERE form_id = :form_id
            """
            result = conn.execute(text(select_responses_query), {'form_id': form_id})
            rows = result.fetchall()

            # Format the data as a list of dictionaries
            responses_summary = []
            for row in rows:
                responses_summary.append({
                    'question_id': row[0],
                    'question': row[1],
                    'answer': row[2]
                })

            if not responses_summary:
                return jsonify({'message': 'No responses found for this form_id'}), 404

            return jsonify(responses_summary), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get the summary of all responses for a given form
@app.route('/showgensummary/<form_id>', methods=['GET'])
def showgensummary(form_id):
    print(f"Fetching summary for form_id: {form_id}")
    try:
        # Connect to the database
        engine = connect_with_connector()
        with engine.connect() as conn:
            # Fetch all responses for the given form_id from formresponses table
            select_responses_query = """
            SELECT question_id, actual_question, answer FROM formresponses WHERE form_id = :form_id
            """
            result = conn.execute(text(select_responses_query), {'form_id': form_id})
            rows = result.fetchall()

            # Format the data as a list of dictionaries
            responses_summary = []
            for row in rows:
                responses_summary.append({
                    'question_id': row[0],
                    'question': row[1],
                    'answer': row[2]
                })

            if not responses_summary:
                return jsonify({'message': 'No responses found for this form_id'}), 404
            
            gemini_prompt = "You are a wonderful person who can summarise anything so easily. Now we have form data submitted by different users and you've to summarise everything to me in such a way that it doesn't miss out any information. I don't want to go through each and every response and I'm relying on you assuming you'd summarise everything for me. Here's the data that is there for you. Make sure you don't reveal any PII data like persons emails, persons names and just show igt as it is a overall summary of all the responses. Please give output just as a text without any special characters or anything. Do remember not summarise on question by question level instead aggregate all the responses and generate a summarised output about how the responses went in precise and compact way. Also it's okay if you can include some numbers in the output which can indicate quantitative responses such as 18 people out of 40 people are interested in XYZ etc:\n\n"
            for response in responses_summary:
                gemini_prompt += f"Question: {response['question']}\nAnswer: {response['answer']}\n\n"

            # Configure Gemini API
            genai.configure(api_key="<fillIn>")
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            # Generate content using Gemini
            gemini_payload = {"text": gemini_prompt}
            gemini_response = model.generate_content(gemini_payload)

            # Return the Gemini-generated summary
            return jsonify({
                'summary': gemini_response.text
            }), 200

            # return jsonify(responses_summary), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get all questions for a given form
@app.route('/showQuestions/<form_id>', methods=['GET'])
def show_questions(form_id):
    print(f"Fetching questions for form_id: {form_id}")
    try:
        # Connect to the database
        engine = connect_with_connector()
        with engine.connect() as conn:
            # Fetch all questions for the given form_id from formdata table
            select_questions_query = """
            SELECT id, questiontype, question, options, ratings FROM formdata WHERE form_id = :form_id
            """
            result = conn.execute(text(select_questions_query), {'form_id': form_id})
            rows = result.fetchall()

            # Format the data as a list of dictionaries
            questions = []
            for row in rows:
                questions.append({
                    'id': row[0],
                    'questiontype': row[1],
                    'question': row[2],
                    'options': row[3],
                    'ratings': row[4]
                })

            if not questions:
                return jsonify({'message': 'No questions found for this form_id'}), 404

            return jsonify(questions), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Run the app
if __name__ == "__main__":
    app.run(debug=True)
