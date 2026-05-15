import dotenv
import os

dotenv.load_dotenv()

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
MODEL: str = os.getenv("MODEL","")