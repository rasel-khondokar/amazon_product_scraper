import json
import os
from pathlib import Path
import pytz

APP_NAME = 'amazon_crawler'
ROOT_DIR = Path(__file__).parent.parent
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
IMG_DIR = 'IMAGES'
DIRNAME_ERROR_LOG = 'ERROR/'
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
LOCAL_DB_COLUMNS_PR_DE = """keyword_id VARCHAR(255) PRIMARY KEY,
  keyword VARCHAR(255),
  created_at DATETIME
"""

TABLE_NAME_PRODUCT_HTML = 'amazon_products_html'
LOCAL_DB_COLUMNS_PR_DE_HTML = """page_id VARCHAR(255) PRIMARY KEY,
  keyword_id VARCHAR(255), 
  html LONGTEXT,
  created_at DATETIME
"""
TABLE_RELATIONSHIP_PRODUCT_HTML = f""", FOREIGN KEY (keyword_id) REFERENCES {TABLE_NAME_PRODUCT} (keyword_id)
"""

