import os
from dotenv import load_dotenv
import logging
import openai

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MILVUS_HOST = os.getenv("MILVUS_HOST", "127.0.0.1")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in the environment variables.")
    raise EnvironmentError("OPENAI_API_KEY is not set.")

openai.api_key = OPENAI_API_KEY
