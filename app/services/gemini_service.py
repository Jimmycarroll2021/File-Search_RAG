"""
Gemini API service wrapper
Handles all interactions with Google Gemini API
"""
from google import genai
from google.genai import types
import time


class GeminiService:
    """Service class for interacting with Gemini API"""

    def __init__(self):
        """Initialize Gemini client"""
        self.client = genai.Client()

    def create_file_search_store(self, store_name: str):
        """
        Create a new file search store

        Args:
            store_name: Display name for the store

        Returns:
            File search store object
        """
        file_search_store = self.client.file_search_stores.create(
            config={'display_name': store_name}
        )
        return file_search_store

    def upload_file_to_store(
        self,
        file_path: str,
        store_id: str,
        display_name: str,
        max_wait: int = 30
    ):
        """
        Upload a file to a file search store

        Args:
            file_path: Path to the file to upload
            store_id: ID of the file search store
            display_name: Display name for the file
            max_wait: Maximum time to wait for upload completion (seconds)

        Returns:
            Operation object
        """
        operation = self.client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=store_id,
            config={'display_name': display_name}
        )

        # Wait for import to complete
        waited = 0
        while not operation.done and waited < max_wait:
            time.sleep(2)
            operation = self.client.operations.get(operation)
            waited += 2

        return operation

    def query_with_file_search(
        self,
        question: str,
        store_id: str,
        model: str = "gemini-2.5-flash",
        system_prompt: str = None,
        temperature: float = None
    ) -> str:
        """
        Query the file search store with a question

        Args:
            question: Question to ask
            store_id: ID of the file search store
            model: Gemini model to use
            system_prompt: Optional system prompt to guide the model's behavior
            temperature: Optional temperature for response creativity (0.0-1.0)

        Returns:
            Answer text from the model
        """
        # Build config with file search tool
        config_params = {
            'tools': [
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_id]
                    )
                )
            ]
        }

        # Add system instruction if provided
        if system_prompt:
            config_params['system_instruction'] = system_prompt

        # Add temperature if provided
        if temperature is not None:
            config_params['temperature'] = temperature

        response = self.client.models.generate_content(
            model=model,
            contents=question,
            config=types.GenerateContentConfig(**config_params)
        )
        return response.text
