from decouple import Config, RepositoryEnv
import pathlib
from functools import lru_cache

BASE_DIR = pathlib.Path(__file__).resolve().parent
print(BASE_DIR)
ENV_PATH = BASE_DIR / ".env" # /Users/adarsh/completeAI/cortexAI/backend/gateway/.env
print(ENV_PATH)

@lru_cache()
def get_config():
    if ENV_PATH.exists():
        print("path exists") 
        return Config(RepositoryEnv(str(ENV_PATH)))
    from decouple import config
    print("path does not exists") 
    return config

config = get_config()