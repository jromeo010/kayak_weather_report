import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini client
# Make sure you have GEMINI_API_KEY in your .env file
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def next_weekday(d: datetime.date, target_weekday: int) -> datetime.date:
    # target_weekday: Monday=0 ... Sunday=6
    days_ahead = (target_weekday - d.weekday()) % 7
    return d + datetime.timedelta(days=days_ahead)


# Read the prompt from prompt.md
with open('prompt.md', 'r', encoding="utf8") as file:
    prompt_content = file.read()

today = datetime.date.today()
current_date = today.strftime("%Y-%m-%d")

upcoming_saturday = next_weekday(today, 5).strftime("%Y-%m-%d")  # Saturday
upcoming_sunday = next_weekday(today, 6).strftime("%Y-%m-%d")    # Sunday

prompt_content = f"""## ⚠️ CURRENT DATE INJECTION: Today's date is strictly {current_date}.
All calculations and the 'report_generated_for' field MUST take into account todays date, upcoming saturday: {upcoming_saturday} and upcoming sunday: {upcoming_sunday}"""+ prompt_content 
# Call Google Gemini API
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(
    prompt_content,
    generation_config={
        'temperature': 0.7,
        'max_output_tokens': 20000,
    }
)

# Extract and display the response
gemini_response = response.text

print("Response from Gemini:")
print("-" * 80)
print(gemini_response)
print("-" * 80)


# Try to parse as JSON if possible
try:
    json_output = json.loads(gemini_response.replace("json","").replace("```",""))
    print("\nParsed JSON output:")
    print(json.dumps(json_output, indent=2))
    
    # Save the response to a file
    with open('kayak_forecast.json', 'w') as output_file:
        json.dump(json_output, output_file, indent=2)
    print("\nJSON response saved to kayak_forecast.json")
except json.JSONDecodeError:
    print("\nNote: Response was not valid JSON")
