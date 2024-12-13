from flask import Flask, request, jsonify, render_template
import requests
import google.generativeai as genai
import json

app = Flask(__name__)

# Gemini API details
GEMINI_API_KEY = '<FillIN>'
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'

# createForm API endpoint
CREATE_FORM_API_URL = 'http://127.0.0.1:5000/createForm'

@app.route('/')
def index():
    return render_template('index.html')

def convert_to_strings(data):
    if isinstance(data, dict):
        # For each key-value pair, recursively convert
        return {str(key): convert_to_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        # For each item in the list, recursively convert
        return [convert_to_strings(item) for item in data]
    else:
        # Convert the value to a string
        return str(data)

@app.route('/generate_form', methods=['POST'])
def generate_form():
    print("inside generate form")
    user_input = request.json.get('event_description')
    print("got event desc")
    print(user_input)
    if not user_input:
        return jsonify({"error": "Event description is required."}), 400

    # Prepare the Gemini API payload
    gemini_payload = '''I need you to be a best feedback collector from the users and I need your help in creating great feedback questions from the users. basically I'll give you the context of what is something that I'm looking forward to getting feedback for in the triple  ticks and you need to generate feedback questions in such a way that given those questions it should give out the right questions, thoughts in users mind while filling the feedback form. Make sure you respond to me only in the json format for the questions generated. I need you to come up with shortanswer, longanswer, dropdown, multichoice, ratings questions(rating should be for 5) along with what you feel are the questions that should be associated with them and options if any incase of dropdown or multichoice questions.

Additionally let's make name, email as the mandatory questions for every output you generate and these should be the top questions

make sure you're not assuming anything for any questions, only ask open ended questions if you're not sure on the options to be provided

make sure you give options as a comma separated string

here's a sample format for the json I want in the response

[
    {
      "questiontype": "",
      "question": "",
      "options": "option1, option2, option3", // only in case of multichoice or dropdown questiontypes else fill in NA, make sure it is always comma separated string with spaces in between
      "ratings": "5" //only in case of ratings(it should be always 5) questiontype else fill in NA
    },
    {
      "questiontype": "",
      "question": "",
      "options": "",
      "ratings": ""
    },
    {
      "questiontype": "",
      "question": "",
      "options": "",
      "ratings": ""
    }
]

Here's the context for which you've to generate the questions for. Please restrict yourself only to generate the json and no additional information or text along with that and don't ask any follow up questions.

``` ''' + str(user_input) + "````"

    print("after this")

    # try:
    # Make the API call to Gemini
    print("going for gemini")
    # gemini_response = requests.post(
    #     GEMINI_API_URL,
    #     headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
    #     json=gemini_payload
    # )

    genai.configure(api_key="<fillIn>")
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    gemini_response = model.generate_content(gemini_payload)

    print("gemini response now")

    print(gemini_response.text)

    # if gemini_response.status_code != 200:
    #     return jsonify({"error": "Failed to get a response from Gemini API."}), 500

    # gemini_data = gemini_response.json()

    # Extract JSON questions from Gemini's response
    feedback_questions = gemini_response.text

    feedback_questions = feedback_questions.replace("```json", "")  # Remove backticks
    feedback_questions = feedback_questions.replace("```", "")  # Remove backticks
    feedback_questions = feedback_questions.replace("```json", "")  # Remove backticks
    # feedback_questions = feedback_questions.replace("name json", "")  # Remove "name json"
    feedback_questions.strip()
    feedback_questions_list = json.loads(feedback_questions)



    # Step 3: Convert all keys and values to strings
    feedback_questions_str = convert_to_strings(feedback_questions_list)

    # Parse the cleaned JSON
    # feedback_questions = json.loads(feedback_questions)

    # Make the API call to createForm
    print("going for create form")

    print(type(feedback_questions))

    create_form_response = requests.post(
        CREATE_FORM_API_URL,
        json=feedback_questions_str,
        headers={"Content-Type": "application/json"}
    )

    print(create_form_response)

    if create_form_response.status_code != 201:
        return jsonify({"error": "Failed to create form."}), 500

    # Return the response from createForm API
    return jsonify(create_form_response.json())

    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

@app.route('/summary/<form_id>', methods=['GET'])
def show_summary(form_id):
    try:
        # Make the API call to fetch the summary
        summary_response = requests.get(f'http://127.0.0.1:5000/showgensummary/{form_id}')
        
        if summary_response.status_code != 200:
            return jsonify({"error": "Failed to fetch the summary."}), 500
        
        # Extract the summary from the response
        summary_data = summary_response.json()
        summary = summary_data.get('summary', 'No summary available.')

        # Render the summary in a new HTML page
        return render_template('summary.html', form_id=form_id, summary=summary)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,port=5050)
