from dotenv import load_dotenv
import os


# get environment variable
load_dotenv('/etc/secrets/config.env')
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
access_token = os.getenv('access_token')
refresh_token = os.getenv('refresh_token')
album_id = os.getenv('album_id')
line_channel_access_token = os.getenv('line_channel_access_token')
line_channel_secret = os.getenv('line_channel_secret')
mongo_client = os.getenv('mongo_client')
mongo_client_ccsue = os.getenv('mongo_client_ccsue')