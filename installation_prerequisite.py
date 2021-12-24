from accessing_db.db import DBConnector
from settings import CREDENTIAL_MYSQL, LOCAL_DB_HOST, LOCAL_DB_PORT, LOCAL_DBNAME, TABLE_NAME_PRODUCT, \
    LOCAL_DB_COLUMNS_PR_DE, TABLE_CHARSET

db_connector = DBConnector(CREDENTIAL_MYSQL, LOCAL_DB_HOST, LOCAL_DB_PORT)
db_connector.connect()
db_connector.create_database(LOCAL_DBNAME)
db_connector.create_table(TABLE_NAME_PRODUCT, LOCAL_DB_COLUMNS_PR_DE, TABLE_CHARSET)
db_connector.close()
