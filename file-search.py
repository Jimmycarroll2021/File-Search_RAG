from google import genai
from google.genai import types
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = genai.Client()

# Create the file search store with an optional display name
file_search_store = client.file_search_stores.create(config={'display_name': 'your-fileSearchStore-name'})

# Upload and import a file into the file search store, supply a file name which will be visible in citations
operation = client.file_search_stores.upload_to_file_search_store(
  file='sample.txt',
  file_search_store_name=file_search_store.name,
  config={
      'display_name' : 'display-file-name',
  }
)

# Wait until import is complete
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

# Ask a question about the file
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""Can you tell me about Robert Graves""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)