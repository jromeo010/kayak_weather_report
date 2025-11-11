import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
# Make sure you have OPENAI_API_KEY in your .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read the prompt from prompt.md
with open('prompt.md', 'r', encoding="utf8") as file:
    prompt_content = file.read()

print(prompt_content)

# Call OpenAI ChatGPT API
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": prompt_content
        }
    ],
    temperature=0.7,
    max_tokens=2000
)

# Extract and display the response
gpt_response = response.choices[0].message.content

print("Response from ChatGPT:")
print("-" * 80)
print(gpt_response)
print("-" * 80)

# Try to parse as JSON if possible
try:
    json_output = json.loads(gpt_response)
    print("\nParsed JSON output:")
    print(json.dumps(json_output, indent=2))
    
    # Save the response to a file
    with open('kayak_forecast.json', 'w') as output_file:
        json.dump(json_output, output_file, indent=2)
    print("\nJSON response saved to kayak_forecast.json")
except json.JSONDecodeError:
    print("\nNote: Response was not valid JSON")
