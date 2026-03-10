import os

from dotenv import load_dotenv

load_dotenv()

IBGE_BASE_URL: str = os.environ["IBGE_BASE_URL"]
