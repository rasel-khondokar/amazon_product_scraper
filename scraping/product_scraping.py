import os
import time
import uuid
from datetime import datetime

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from get_chrome_driver import GetChromeDriver
from settings import CHROMEDRIVER_PATH, TIME_ZONE, TABLE_NAME_PRODUCT

from settings import MAIN_SITE_AMAZON, IMG_DIR, BASE_DIR
from utils import image_downloader, make_dir_if_not_exists, process_keyword


class Scraper():
    def __init__(self, db_connector=None):
        self.db_connector = db_connector

    def get_driver(self, url, headless=True):
        option = Options()
        option.add_argument("--disable-notifications")
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')

        if headless:
            option.add_argument("--headless")

        chrome_dir = os.path.dirname(os.path.realpath(__file__)) + '/' + CHROMEDRIVER_PATH
        # make_dir_if_not_exists(chrome_dir)
        chrome_file_path = chrome_dir + '/chromedriver'

        try:
            driver = webdriver.Chrome(chrome_file_path, chrome_options=option)
            driver.get(url)
        except Exception as e:
            print('Selenium session is not Created !')

            if os.path.exists(chrome_file_path):
                os.remove(chrome_file_path)
                print(f'Removed {chrome_file_path} file!')

            download_driver = GetChromeDriver()
            download_driver.auto_download(extract=True, output_path=chrome_dir)
            print(f'Downloaded chrome driver for the chrome version {download_driver.matching_version()}!')
            driver = webdriver.Chrome(chrome_file_path, chrome_options=option)
            driver.get(url)

        driver.maximize_window()
        return driver

    def get_text_from_multiple_elements(self, driver, selectors, attribute=None, multiple=False):
        for selector in selectors:
            try:
                if attribute == 'element':
                    if multiple:
                        target_element = driver.find_elements(By.CSS_SELECTOR, selector)
                    else:
                        target_element = driver.find_element(By.CSS_SELECTOR, selector)
                elif attribute == 'html':
                    if multiple:
                        target_element = driver.find_elements(By.CSS_SELECTOR, selector).get_attribute('innerHTML')
                    else:
                        target_element = driver.find_element(By.CSS_SELECTOR, selector).get_attribute('innerHTML')
                else:
                    if multiple:
                        target_element = driver.find_elements(By.CSS_SELECTOR, selector).text
                    else:
                        target_element = driver.find_element(By.CSS_SELECTOR, selector).text

                if target_element:
                    return target_element
            except:
                continue

    def extract_price(self, text):
        text = text.split('$')
        for i in text:
            try:
                return float(i)
            except ValueError:
                continue

    def get_product_details(self,driver):

        # get details
        details = {'product_id':uuid.uuid4().hex}

        try:
            details['title'] = driver.find_element(By.CSS_SELECTOR, '#productTitle').text
        except Exception as e:
            print(e)

        try:
            price_selectors = ['.apexPriceToPay', '#olp_feature_div .a-color-price',
                               '.a-button-selected span']
            price = self.get_text_from_multiple_elements(driver, price_selectors)
            if price:
                details['price'] = self.extract_price(price)
            else:
                try:
                    prices_elements = driver.find_elements(By.CSS_SELECTOR, 'span.olpWrapper')
                    prices = []
                    for ele in prices_elements:
                        prices.append(self.extract_price(ele.text))
                    details['price'] = min(prices)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)

        try:
            desc_selectors = ['#feature-bullets ul']
            details['product_desc'] = self.get_text_from_multiple_elements(driver, desc_selectors)
        except Exception as e:
            print(e)

        # Download product image
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#imgTagWrapperId img')))
            img_url = driver.find_element(By.CSS_SELECTOR, '#imgTagWrapperId img').get_attribute('src')
            details['image_url'] = img_url
            # image_path = f"{BASE_DIR}/{IMG_DIR}/"
            # image_downloader(img_url, details['product_id'], image_path)
        except Exception as e:
            print(e)
            print('error during image!')

        return details

    def search_by_keyword(self, keyword, driver):
        search_box = driver.find_element(By.CSS_SELECTOR, '#twotabsearchtextbox')
        search_box.send_keys(keyword)
        search_btn = driver.find_element(By.CSS_SELECTOR, '#nav-search-submit-button')
        search_btn.click()


    def scrape_products(self, keyword, no_products, driver):

        keyword_processed = process_keyword(keyword)
        keyword_search = f'{MAIN_SITE_AMAZON}s?k={keyword_processed}'
        # self.search_by_keyword(keyword, driver)
        driver.get(keyword_search)

        # products = driver.find_elements(By.CSS_SELECTOR, '.s-line-clamp-4 a')
        products_selectors = ['.s-line-clamp-4 a', '.s-line-clamp-2 a']
        products = self.get_text_from_multiple_elements(driver, products_selectors, 'element', multiple=True)

        products_urls = list(set([product.get_attribute('href') for product in products]))

        if len(products_urls)>no_products:
            products_urls = products_urls[:no_products]

        for product_url in products_urls:
            try:
                driver.get(product_url)
                details = self.get_product_details(driver)
                details['url'] = driver.current_url.split('/ref=')[0]
                details['created_at'] = datetime.now().astimezone(TIME_ZONE)
                details['keyword'] = keyword
                saved_count, result = self.db_connector.save_to_table(TABLE_NAME_PRODUCT, details)
                print(saved_count)
            except Exception as e:
                print(e)