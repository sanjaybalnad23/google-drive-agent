import dotenv
import os

dotenv.load_dotenv()

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
MODEL: str = os.getenv("MODEL","")