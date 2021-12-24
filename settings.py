import json
import os
from pathlib import Path
import pytz

ROOT_DIR = Path(__file__).parent.parent
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
IMG_DIR = 'IMAGES'
CHROMEDRIVER_PATH = 'chromedriver_linux64'
MAIN_SITE_AMAZON = 'https://www.amazon.com/'
DEFAULT_NO_PRODUCTS = 10
TIME_ZONE = pytz.timezone('Asia/Dhaka')

with open(f'{BASE_DIR}/credentials.json') as credentials_file:
    credentials = json.load(credentials_file)
CREDENTIAL_MYSQL = credentials['mysql']
LOCAL_DBNAME = 'amazon_data'
LOCAL_DB_HOST = 'localhost'
LOCAL_DB_PORT = 3306
TABLE_CHARSET = 'utf8mb4 COLLATE utf8mb4_unicode_ci'
TABLE_NAME_KEYWORDS = 'product_keywords'
TABLE_NAME_PRODUCT = 'amazon_products'
LOCAL_DB_COLUMNS_PR_DE = """product_id VARCHAR(255) PRIMARY KEY,
  keyword VARCHAR(255),
  url VARCHAR(500),
  title VARCHAR(500),
  image_url VARCHAR(500),
  product_desc LONGTEXT,
  price FLOAT,
  created_at DATETIME
"""
