import os
import json
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

with open("secrets.json", "r") as f:
    secrets = json.load(f)

api_keys_with_proxies = secrets["api_keys_with_proxies"]
llm_models = models = [
    "deepseek/deepseek-prover-v2:free",
    "nousresearch/deephermes-3-mistral-24b-preview:free",
    "qwen/qwen3-0.6b-04-28:free"
]