from accessing_db.db import DBConnector
from scraping.product_scraping import Scraper
from settings import DEFAULT_NO_PRODUCTS, CREDENTIAL_MYSQL, LOCAL_DB_PORT, LOCAL_DB_HOST, LOCAL_DBNAME, \
    MAIN_SITE_AMAZON, IMG_DIR, APP_NAME
from utils import process_keyword, make_dir_if_not_exists, save_error_log


def main():

    error_logger = save_error_log(APP_NAME)

    # Get keywords from db
    # make_dir_if_not_exists(IMG_DIR)

    db_connector = DBConnector(CREDENTIAL_MYSQL, LOCAL_DB_HOST, LOCAL_DB_PORT)
    db_connector.connect(LOCAL_DBNAME)
    keywords = db_connector.get_keywords()

    scraper = Scraper(db_connector)
    scraper.set_logger(error_logger)

    try:
        # Go to amazon
        amazon_driver = scraper.get_driver(MAIN_SITE_AMAZON, headless=False)

        # set location as New York
        scraper.set_location(amazon_driver)

        # search keywords on amazon & save products details to db
        for keyword_dict in keywords:
            if 'KWYWORD' in keyword_dict:

                if 'no_products' in keyword_dict:
                    no_products = keyword_dict['no_products']
                else:
                    no_products = DEFAULT_NO_PRODUCTS

                try:
                    scraper.scrape_products(keyword_dict['KWYWORD'], no_products, amazon_driver)
                except Exception as e:
                    scraper.logger(e)
    except Exception as e:
        scraper.logger(e)

    db_connector.close()

if __name__=='__main__':
    main()