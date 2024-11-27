# import libraries

import time
import openai
import yaml
#from openai.error_classes import RateLimitError, APIError
from openai import OpenAIError, RateLimitError
import json
from flask import Flask, render_template

app = Flask(__name__)

# Define retry parameters
MAX_RETRIES = 3
RETRY_DELAY = 10  # in seconds

@app.route('/ats')
def ats():
    # Simulate data returned from the ats_extractor function
    data = ats_extractor("Sample resume data")  # Replace with actual function call
    
    if data is None:
        return render_template('index.html', error="Failed to parse resume data. Please try again.")
    
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError:
        return render_template('index.html', error="Invalid JSON format in response.")
    
    return render_template('index.html', data=parsed_data)


def ats_extractor(resume_data):
    prompt = '''
    You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
    1. full name
    2. email id
    3. github portfolio
    4. linkedin id
    5. employment details
    6. technical skills
    7. soft skills
    Give the extracted information in json format only
    '''
    # Load YAML file
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
        openai.api_key = config.get("OPENAI_API_KEY")
        #Confirm API key load (Optional: Only for debugging, remove later for security)
        if openai.api_key:
            print("API Key loaded successfully.")
        else:
            print("Failed to load API Key. Please check your config.yaml file.")

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": resume_data}
    ]

    # # Retry logic for OpenAI API call
    # for attempt in range(MAX_RETRIES):

    for attempt in range(MAX_RETRIES):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return response.choices[0].message['content']
        except RateLimitError as e:
            print(f"Rate limit exceeded. Retrying in {RETRY_DELAY} seconds... (Attempt {attempt + 1})")
            time.sleep(RETRY_DELAY)
        except OpenAIError as e:
            print(f"OpenAI error occurred: {e}")
            break
    return json.dumps(resume_data)

if __name__ == '__main__':
    app.run(debug=True)


