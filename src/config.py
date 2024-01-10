from environs import Env
import json

with open("network-config.json", "r") as network_config:
    network_config = json.loads(network_config.read())

env = Env()
env.read_env(".env")


BOT_TOKEN = env.str("BOT_TOKEN")
CONNECT_URL = env.str("CONNECT_URL")
WALLETS_LIST_URL = env.str("WALLETS_LIST_URL")
