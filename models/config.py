import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini')

# Specify the full path to the config.ini file
config_file_path = os.path.join(os.path.dirname(__file__), 'config.ini')

# Read the config file
config.read(config_file_path)

stk_push_url = config.get('safaricom', 'stk_push_url')
stk_push_call_back_url = config.get('safaricom', 'stk_push_call_back_url')
mpesa_url_v1 = config.get('safaricom', 'mpesa_url_v1')
