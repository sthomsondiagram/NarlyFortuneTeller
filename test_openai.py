from openai import OpenAI
from dotenv import load_dotenv
import os
import json
load_dotenv()


# Initialize client with API key directly
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Send a prompt
response = client.responses.create(
    model="gpt-4.1-mini",   # use an available model
    input="tell me about Umbraco CMS in 100 words"
)

# Print the response text
print(response.output_text)