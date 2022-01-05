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
from settings import CHROMEDRIVER_PATH, TIME_ZONE, TABLE_NAME_PRODUCT, TABLE_NAME_PRODUCT_HTML

from settings import MAIN_SITE_AMAZON, IMG_DIR, BASE_DIR
from utils import image_downloader, make_dir_if_not_exists, process_keyword


class Scraper():
    def __init__(self, db_connector=None):
        self.db_connector = db_connector

    def set_logger(self, logger):
        self.logger = logger

    def set_location(self, driver):
        try:
            time.sleep(2)
            loc_btn = driver.find_element(By.CSS_SELECTOR, '#nav-global-location-popover-link')
            loc_btn.click()
            time.sleep(2)
            loc_btn_inp = driver.find_element(By.CSS_SELECTOR, '.GLUX_Full_Width.a-declarative')
            loc_btn_inp.send_keys('10001')
            time.sleep(2)
            loc_btn_apply = driver.find_element(By.CSS_SELECTOR, '#GLUXZipUpdate input')
            loc_btn_apply.click()
            time.sleep(2)
            reaction_btn_js = "document.querySelector('#GLUXConfirmClose').click();"
            driver.execute_script(reaction_btn_js)
        except Exception as e:
            self.logger.exception(e)

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
    def get_price_from_multiple_elements(self, driver):
        prices_elements = driver.find_elements(By.CSS_SELECTOR, 'span.olpWrapper')
        prices = []
        for ele in prices_elements:
            prices.append(self.extract_price(ele.text))

        if not prices:
            ul_class ='ul.a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare imageSwatches'\
                .replace(' ', '.')
            selectors = [f'{ul_class} li']
            p = self.get_text_from_multiple_elements(driver, selectors)
            prices.append(self.extract_price(p))

        if prices:
            return min(prices)

    def get_product_details(self,driver):

        # get details
        details = {'product_id':uuid.uuid4().hex}

        try:
            details['title'] = driver.find_element(By.CSS_SELECTOR, '#productTitle').text
        except Exception as e:
            self.logger.exception(e)

        try:
            price_selectors = ['.apexPriceToPay', '#olp_feature_div .a-color-price',
                               '.a-button-selected span', '.priceToPay']
            price = self.get_text_from_multiple_elements(driver, price_selectors)
            if price:
                details['price'] = self.extract_price(price)
            else:
                try:
                    details['price'] = self.get_price_from_multiple_elements(driver)
                except Exception as e:
                    self.logger.exception(e)
        except Exception as e:
            self.logger.exception(e)

        try:
            features = driver.find_elements(By.CSS_SELECTOR, '#feature-bullets ul li')
            details['features'] = [feature.text for feature in features]
        except Exception as e:
            self.logger.exception(e)

        # Download product image
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#imgTagWrapperId img')))
            img_url = driver.find_element(By.CSS_SELECTOR, '#imgTagWrapperId img').get_attribute('src')
            details['image_url'] = img_url
            # image_path = f"{BASE_DIR}/{IMG_DIR}/"
            # image_downloader(img_url, details['product_id'], image_path)
        except Exception as e:
            self.logger.exception(e)
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

        try:
            products = self.get_text_from_multiple_elements(driver, products_selectors, 'element', multiple=True)

            products_urls = list(set([product.get_attribute('href') for product in products]))

            if len(products_urls) > no_products:
                products_urls = products_urls[:no_products]

            products_details = []
            for product_url in products_urls:
                try:
                    driver.get(product_url)
                    details = self.get_product_details(driver)
                    details['url'] = driver.current_url.split('/ref=')[0]
                    products_details.append(details)
                except Exception as e:
                    self.logger.exception(e)

            keyword_data = {
                'keyword_id':uuid.uuid4().hex,
                'keyword':keyword,
                'created_at':datetime.now().astimezone(TIME_ZONE)
            }

            saved_count, result = self.db_connector.save_to_table(TABLE_NAME_PRODUCT, keyword_data)

            html = self.make_html_page({
                'keyword':keyword,
                'products':products_details
            })

            saved_count, result_html = self.db_connector.save_to_table(TABLE_NAME_PRODUCT_HTML, {
                'page_id':uuid.uuid4().hex,
                'keyword_id':keyword_data['keyword_id'],
                'html':html,
                'created_at':keyword_data['created_at']
            })

        except Exception as e:
            self.logger.exception(e)

    def set_value_if_exists(self, dictionary, key):
        text = ''
        if key in dictionary:
            if dictionary[key]:
                text = dictionary[key]
        return text

    def make_products_table(self, products):
        html = ''
        for product in products:
            title = self.set_value_if_exists(product, 'title')
            price = self.set_value_if_exists(product, 'price')
            url = self.set_value_if_exists(product, 'url')
            image_url = self.set_value_if_exists(product, 'image_url')

            html += f'''\n<div class="row-products">
                <div class="col-md-2 col-sm-2 col-xs-12 cegg-image-cell">
                   <a rel="nofollow sponsored external noopener" target="_blank" href="{url}" data-wpel-link="external">
                      <img src="{image_url}" alt="{title}" width="350" height="350" data-lazy-src="{image_url}" />
                      <noscript><img src="{image_url}" alt="{title}" width="100" height="100" /></noscript>
                   </a>
                </div>
                <div class="col-md-5 col-sm-5 col-xs-12 cegg-desc-cell hidden-xs">
                   <div class="cegg-no-top-margin cegg-list-logo-title">
                      <a rel="nofollow sponsored external noopener" target="_blank" href="{url}" data-wpel-link="external">{title}</a>
                   </div>
                </div>
                <div class="col-md-3 col-sm-3 col-xs-12 cegg-price-cell text-center">
                   <div class="cegg-price-row">
                      <div class="cegg-price cegg-price-color cegg-price-instock">${price}</div>
                   </div>
                </div>
                <div class="col-md-2 col-sm-2 col-xs-12 cegg-btn-cell">
                   <div class="cegg-btn-row">
                      <a rel="nofollow sponsored external noopener" target="_blank" href="{url}" class="btn btn-danger btn-block" data-wpel-link="external"><span>BUY NOW</span></a> 
                   </div>
                </div>
             </div>
             \n'''

        return html

    def make_desc_list(self, features):
        html = ''
        for feature in features:
            html += f'''<li>{feature}</li>\n'''
        return html

    def make_products_desc(self, products):
        html = ''
        for product in products:

            title = self.set_value_if_exists(product, 'title')
            price = self.set_value_if_exists(product, 'price')
            url = self.set_value_if_exists(product, 'url')
            image_url = self.set_value_if_exists(product, 'image_url')
            features = self.make_desc_list(product['features'])

            html += f'''\n<div class="egg-container egg-item">
                              <div class="products">
                              <div class="row">
                    <div class="col-md-6 text-center cegg-image-container cegg-mb20">
                       <a rel="nofollow sponsored external noopener" target="_blank" href="{url}" data-wpel-link="external">
                          <img src="{image_url}" alt="{title}" width="350" height="350" data-lazy-src="{image_url}" />
                          <noscript><img src="{image_url}" alt="{title}" width="350" height="350" /></noscript>
                       </a>
                    </div>
                    <div class="col-md-6">
                       <h3 class="cegg-item-title">{title}</h3>
                       <div class="cegg-price-row">
                          <span class="cegg-price cegg-price-color">            
                          <span class="cegg-currency">$</span>{price}</span>
                       </div>
                       <div class="cegg-btn-row cegg-mb5">
                          <div><a rel="nofollow sponsored external noopener" target="_blank" href="{url}" class="btn btn-danger cegg-btn-big" data-wpel-link="external">BUY NOW</a></div>
                       </div>
                    </div>
                 </div>
                 <div class="row">
                    <div class="col-md-12">
                       <div class="cegg-mb25">
                          <div class="cegg-features-box">
                             <h4 class="cegg-no-top-margin">Features</h4>
                             <ul class="cegg-feature-list">
                                {features}
                                \n
                                             </ul>
                                          </div>
                                       </div>
                                    </div>
                                 </div>
                              </div>
                           </div>'''

        return html

    def get_header(self, keyword):
        affected = '''
        <style id="rocket-critical-css">.crp_related{clear:both;margin:10px 0}.crp_related h3{margin:0!important}.crp_related ul{list-style:none;float:left;margin:0!important;padding:0!important}.crp_related li,.crp_related a{float:left;overflow:hidden;position:relative;text-align:center}.crp_related li{margin:5px!important;border:1px solid #ddd;padding:6px}.crp_related a{-webkit-box-shadow:none!important;-moz-box-shadow:none!important;box-shadow:none!important;text-decoration:none!important}.crp_related .crp_title{color:#fff!important;position:absolute;display:block;bottom:0;padding:3px;font-size:.9em;text-shadow:.1em .1em .2em #000;background-color:rgba(0,0,0,0.5);-webkit-border-radius:7px;-moz-border-radius:7px;border-radius:7px}.crp_related li{vertical-align:bottom;-webkit-box-shadow:0 1px 2px rgba(0,0,0,.4);-moz-box-shadow:0 1px 2px rgba(0,0,0,.4);box-shadow:0 1px 2px rgba(0,0,0,.4);-webkit-border-radius:7px;-moz-border-radius:7px;border-radius:7px;list-style-type:none}.crp_clear{clear:both}.crp_title:visited{color:#fff!important}#wpfront-scroll-top-container{display:none;position:fixed;z-index:9999}body,h1,h2,h3,html,li,p,ul{margin:0;padding:0;border:0}html{font-family:sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}main{display:block}html{box-sizing:border-box}*,::after,::before{box-sizing:inherit}button,input{font-family:inherit;font-size:100%;margin:0}[type=search]{-webkit-appearance:textfield;outline-offset:-2px}[type=search]::-webkit-search-decoration{-webkit-appearance:none}::-moz-focus-inner{border-style:none;padding:0}:-moz-focusring{outline:1px dotted ButtonText}body,button,input{font-family:-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";font-weight:400;text-transform:none;font-size:17px;line-height:1.5}p{margin-bottom:1.5em}h1,h2,h3{font-family:inherit;font-size:100%;font-style:inherit;font-weight:inherit}h1{font-size:42px;margin-bottom:20px;line-height:1.2em;font-weight:400;text-transform:none}h2{font-size:35px;margin-bottom:20px;line-height:1.2em;font-weight:400;text-transform:none}h3{font-size:29px;margin-bottom:20px;line-height:1.2em;font-weight:400;text-transform:none}ul{margin:0 0 1.5em 3em}ul{list-style:disc}img{height:auto;max-width:100%}button{background:#55555e;color:#fff;border:1px solid transparent;-webkit-appearance:button;padding:10px 20px}input[type=search]{border:1px solid;border-radius:0;padding:10px 15px;max-width:100%}a,a:visited{text-decoration:none}.screen-reader-text{border:0;clip:rect(1px,1px,1px,1px);-webkit-clip-path:inset(50%);clip-path:inset(50%);height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute!important;width:1px;word-wrap:normal!important}.main-navigation{z-index:100;padding:0;clear:both;display:block}.main-navigation a{display:block;text-decoration:none;font-weight:400;text-transform:none;font-size:15px}.main-navigation ul{list-style:none;margin:0;padding-left:0}.main-navigation .main-nav ul li a{padding-left:20px;padding-right:20px;line-height:60px}.inside-navigation{position:relative}.main-navigation .inside-navigation{display:flex;align-items:center;flex-wrap:wrap;justify-content:space-between}.main-navigation .main-nav>ul{display:flex;flex-wrap:wrap;align-items:center}.main-navigation li{position:relative}.site-header{position:relative}.inside-header{padding:20px 40px}.main-title{margin:0;font-size:25px;line-height:1.2em;word-wrap:break-word;font-weight:700;text-transform:none}.inside-header{display:flex;align-items:center}.nav-float-right #site-navigation{margin-left:auto}.entry-content:not(:first-child){margin-top:2em}.entry-header,.site-content{word-wrap:break-word}.entry-title{margin-bottom:0}.widget-area .widget{padding:40px}.sidebar .widget :last-child{margin-bottom:0}.widget-title{margin-bottom:30px;font-size:20px;line-height:1.5;font-weight:400;text-transform:none}.widget ul{margin:0}.widget .search-field{width:100%}.widget .search-form{display:flex}.widget .search-form button.search-submit{font-size:15px}.sidebar .widget:last-child{margin-bottom:0}.widget ul li{list-style-type:none;position:relative;margin-bottom:.5em}.site-content{display:flex}.grid-container{margin-left:auto;margin-right:auto;max-width:1200px}.sidebar .widget,.site-main>*{margin-bottom:20px}.separate-containers .inside-article{padding:40px}.separate-containers .site-main{margin:20px}.separate-containers.right-sidebar .site-main{margin-left:0}.separate-containers .inside-right-sidebar{margin-top:20px;margin-bottom:20px}.separate-containers .site-main>:last-child{margin-bottom:0}.gp-icon{display:inline-flex;align-self:center}.gp-icon svg{height:1em;width:1em;top:.125em;position:relative;fill:currentColor}.icon-menu-bars svg:nth-child(2){display:none}.container.grid-container{width:auto}.menu-toggle{display:none}.menu-toggle{padding:0 20px;line-height:60px;margin:0;font-weight:400;text-transform:none;font-size:15px}.menu-toggle .mobile-menu{padding-left:3px}.menu-toggle .gp-icon+.mobile-menu{padding-left:9px}button.menu-toggle{background-color:transparent;flex-grow:1;border:0;text-align:center}.mobile-menu-control-wrapper{display:none;margin-left:auto;align-items:center}@media (max-width:768px){.inside-header{flex-direction:column;text-align:center}.site-content{flex-direction:column}.container .site-content .content-area{width:auto}.is-right-sidebar.sidebar{width:auto;order:initial}#main{margin-left:0;margin-right:0}body:not(.no-sidebar) #main{margin-bottom:0}}</style>
                  <link rel="preload" as="style" href="https://fonts.googleapis.com/css?family=Open%20Sans%3A300%2C300italic%2Cregular%2Citalic%2C600%2C600italic%2C700%2C700italic%2C800%2C800italic&#038;display=swap" />
                  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open%20Sans%3A300%2C300italic%2Cregular%2Citalic%2C600%2C600italic%2C700%2C700italic%2C800%2C800italic&#038;display=swap" media="print" onload="this.media='all'" />
            
            
                  <style>@charset "UTF-8";body{font-family:-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";font-weight:400;text-transform:none;font-size:17px;line-height:1.5}p{margin-bottom:1.5em}h1{font-size:42px;margin-bottom:20px;line-height:1.2em;font-weight:400;text-transform:none}h2{font-size:35px;margin-bottom:20px;line-height:1.2em;font-weight:400;text-transform:none}h3{font-size:29px;margin-bottom:20px;line-height:1.2em;font-weight:400;text-transform:none}h4{font-size:24px}h4 ol,ul{margin:0 0 1.5em 3em}ul{list-style:disc}ol{list-style:decimal}li>ol,li>ul{margin-bottom:0;margin-left:1.5em}b,strong{font-weight:700}img{height:auto;max-width:100%}.egg-container{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}.egg-container{margin:0}.egg-container .img-responsive,.egg-container .thumbnail a>img,.egg-container .thumbnail>img{display:block;max-width:100%;height:auto}.egg-container body{margin:0}.egg-container [hidden],.egg-container template{display:none}.egg-container a{background-color:transparent}.egg-container a:active,.egg-container a:hover{outline:0}.egg-container b,.egg-container strong{font-weight:700}.egg-container h1{margin:.67em 0;font-size:2em}.egg-container img{border:0}.egg-container *{-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}.egg-container :after,.egg-container :before{-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box}.egg-container a{text-decoration:none}.egg-container a:focus{outline:thin dotted;outline:5px auto -webkit-focus-ring-color;outline-offset:-2px}.egg-container img{vertical-align:middle}.egg-container .img-rounded{border-radius:6px}.egg-container .img-thumbnail{display:inline-block;max-width:100%;height:auto;padding:4px;line-height:1.42857143;background-color:#fff;border:1px solid #ddd;border-radius:4px;-webkit-transition:all .2s ease-in-out;-o-transition:all .2s ease-in-out;transition:all .2s ease-in-out}.egg-container .img-circle{border-radius:50%}@media (min-width:768px){.egg-container .container{width:750px}}@media (min-width:992px){.egg-container .container{width:970px}}@media (min-width:1200px){.egg-container .container{width:1170px}}.egg-container .container-fluid{padding-right:15px;padding-left:15px;margin-right:auto;margin-left:auto}.egg-container .row{margin-right:-15px;margin-left:-15px;margin-bottom:30px}@media (min-width:992px){.col-md-10,.col-md-11,.col-md-12,.col-md-2,.col-md-3,.col-md-4,.col-md-5,.col-md-6,.col-md-7,.col-md-8,.col-md-9,.egg-container .col-md-1{float:left}.egg-container .col-md-12{width:100%}.egg-container .col-md-11{width:91.66666667%}.egg-container .col-md-10{width:83.33333333%}.egg-container .col-md-9{width:75%}.egg-container .col-md-8{width:66.66666667%}.egg-container .col-md-7{width:58.33333333%}.egg-container .col-md-6{width:50%}.egg-container .col-md-5{width:41.66666667%}.egg-container .col-md-4{width:33.33333333%}.egg-container .col-md-3{width:25%}.egg-container .col-md-2{width:16.66666667%}.egg-container .col-md-1{width:8.33333333%}}.egg-container .btn-danger.active,.egg-container .btn-danger.focus,.egg-container .btn-danger:active,.egg-container .btn-danger:focus,.egg-container .btn-danger:hover,.open>.dropdown-toggle.egg-container .btn-danger{color:#fff;background-color:#c9302c;border-color:#ac2925}.egg-container .btn-danger.active,.egg-container .btn-danger:active,.open>.dropdown-toggle.egg-container .btn-danger{background-image:none}.egg-container .btn-danger .badge{color:#d9534f;background-color:#fff}.egg-container .btn-danger{color:#fff;background-color:#d9534f;border-color:#d43f3a}.egg-container .btn-danger.active,.egg-container .btn-danger.focus,.egg-container .btn-danger:active,.egg-container .btn-danger:focus,.egg-container .btn-danger:hover,.open>.dropdown-toggle.egg-container .btn-danger{color:#fff;background-color:#c9302c;border-color:#ac2925}.egg-container .btn{display:inline-block;padding:7px 14px;margin-bottom:0;font-size:14px;font-weight:700;line-height:1.42857143;text-align:center;white-space:nowrap;vertical-align:middle;-ms-touch-action:manipulation;touch-action:manipulation;cursor:pointer;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;background-image:none;border:1px solid transparent;border-radius:4px}.egg-container img{max-width:100%;height:auto}.egg-container .egg-item .cegg-price small{font-size:22px}.egg-grid,.egg-item,.egg-list{margin-bottom:25px}.egg-container .cegg-price{font-weight:700;white-space:nowrap}.egg-container .cegg-gridbox{background-color:#fff;margin-bottom:10px;padding-bottom:10px;border:1px solid #fff;transition:all .3s ease}.egg-container .cegg-gridbox:hover{box-shadow:0 8px 16px -6px #eee;border:1px solid #ddd}.cegg-gridbox .producttitle,.cegg-gridbox .producttitle a{line-height:20px;margin-bottom:10px;font-weight:400;color:#333}.cegg-gridbox .productprice{color:#000;font-weight:700;line-height:20px;margin-bottom:10px;font-size:1.1em}.cegg-gridbox .productprice strike{color:grey;font-weight:400;font-size:.85em}.cegg-gridbox .productprice .text-success{font-weight:400;font-size:.85em}.cegg-thumb{text-align:center}.cegg-gridbox .cegg-thumb{text-align:center;padding:15px}.cegg-price-tracker-item .cegg-thumb{text-align:center}.cegg-gridbox .cegg-thumb img,.cegg-price-tracker-item .cegg-thumb img{border:0 none;box-shadow:none;max-height:170px}.cegg-item-title{font-size:24px;margin:0 0 5px 0}.egg-grid-wdgt .cegg-thumb img{max-height:150px}.egg-list-coupons .cegg-thumb{text-align:center;margin-bottom:10px}.egg-list-coupons .cegg-thumb img{max-height:30px}.egg-container .cegg-discount{background:none repeat scroll 0 0 #dc3545;border-radius:0 4px 4px 0;color:#fff;display:inline-block;float:left;font-size:16px;font-weight:lighter;height:100%;padding:3px 5px}.egg-container .egg-padding-top{padding-top:22px}.egg-container .h4,.egg-container h4{font-size:18px}.egg-container .row-products{display:table-row}.egg-container .row-products>div{display:table-cell;float:none;vertical-align:middle;border-bottom:1px solid #eee;padding:18px 10px}.egg-container .row-products:last-child>div{border:none}.egg-container .row-products>div:first-child{padding-left:0}.egg-container .row-products>div:last-child{padding-right:0}.egg-container .row-products:hover{background-color:#f9f9f9}.egg-container .row-products span.no-bold{font-size:14px;font-weight:400}.cegg-list-no-prices .cegg-desc-cell{vertical-align:top!important}.egg-container{clear:both}.egg-list .row-products{clear:both}.egg-list .row-products{margin-bottom:15px;margin-top:0}.egg-container .cegg-image-cell img{max-height:100px;max-width:100%}.egg-container .cegg-image-cell{text-align:center}.cegg-image-container img{vertical-align:top;max-width:100%;height:auto;display:inline-block;max-height:350px}.egg-container .cegg-no-top-margin{margin-top:0}.egg-container .cegg-no-bottom-margin{margin-bottom:0}.egg-container .cegg-no-margin{margin-top:0}.egg-container .cegg-mb5{margin-bottom:5px}.egg-container .cegg-mb10{margin-bottom:10px}.egg-container .cegg-mb15{margin-bottom:15px}.egg-container .cegg-mb20{margin-bottom:20px}.egg-container .cegg-mb25{margin-bottom:25px}.egg-container .cegg-mb30{margin-bottom:30px}.egg-container .cegg-mb35{margin-bottom:35px}.egg-container .cegg-lineh-20{line-height:20px}.egg-container .cegg-mr10{margin-right:10px}.egg-container .cegg-mr5{margin-right:5px}.egg-container .cegg-mt5{margin-top:5px}.egg-container .cegg-mt10{margin-top:10px}.egg-container .cegg-mt30{margin-top:30px}.egg-container .cegg-pl5{padding-left:5px}.egg-container .btn.cegg-btn-big{padding:13px 80px;line-height:1;font-size:20px;font-weight:700}.egg-container .title-case:first-letter{text-transform:capitalize}.egg-list-coupons .btn{font-size:16px;font-weight:700;display:block}.cegg-list-withlogos .cegg-price,.egg-listcontainer .cegg-price{font-weight:700;font-size:1.1em}.egg-container .cegg-list-withlogos .btn{font-weight:700;font-size:15px;padding:8px 16px}.cegg-list-no-prices .cegg-no-prices-desc{font-size:.9em;color:#656565}.cegg-lineheight15{line-height:15px}.cegg-price-tracker-item .price-alert-title{color:#111;font-weight:700;line-height:20px}.egg-text-bold{font-weight:700}.egg-grid-wdgt .product-discount-value{font-size:20px;margin-right:1px;font-weight:700;white-space:nowrap}.egg-grid-wdgt .product-name,.product-meta,.product-price{font-size:14px;color:#212121;font-weight:400}.egg-grid-wdgt .product-price-old{font-size:14px;line-height:1em;min-height:1em;color:#757575;text-decoration:line-through}.egg-grid-wdgt .product-price-new{font-size:18px;font-weight:700}.egg-grid-wdgt .product-price-new{font-size:18px;font-weight:700}.egg-grid-wdgt-row .cegg-wdgt-gridbox{border-bottom:1px solid #eee;margin-bottom:0;margin-top:15px}.egg-grid-wdgt .cegg-wdgt-gridbox:hover a{text-decoration:underline}.egg-list-wdgt .cegg-discount-off{font-size:18px}.egg-grid-wdgt-row .cegg-wdgt-gridbox:last-child{border-bottom:none}.widget .egg-grid-wdgt{margin-bottom:0}.egg-list-wdgt .product-discount-off{color:#d9534f;font-size:16px;font-weight:700}.egg-grid-wdgt .cegg-gridbox-border{box-shadow:0 8px 16px -6px #eee;border:1px solid #ddd}.egg-list-wdgt .row-products:hover{background-color:inherit}.cegg-price-comparison{margin-bottom:0}.cegg-price-comparison td a{display:block}.cegg-price-comparison .cegg-buttons_col{text-align:center;vertical-align:middle!important}.cegg-price-comparison .cegg-buttons_col a{color:#fff!important}.cegg-price-comparison .cegg-price_col a{text-decoration:none;box-shadow:none;color:#111;font-weight:700}.cegg-price-comparison .cegg-merhant_col{vertical-align:middle!important}.cegg-price-comparison .cegg-merhant_col a{text-decoration:none;box-shadow:none;color:#111;vertical-align:middle!important}.cegg-price-comparison.table{font-size:13px}.egg-container .stock-status{font-size:80%;cursor:help;font-weight:400}.egg-container .status-instock{color:#7ad03a}.egg-container .status-outofstock{color:#777}.egg-container .cegg-disclaimer .cegg-disclaimer-title{padding:5px;cursor:default}.egg-container .cegg-disclaimer{cursor:pointer}.egg-container .cegg-cashback{color:#199402}.cegg-features-table{word-wrap:break-word}.cegg-btn-row{padding-right:10px}.cegg-price-outofstock{color:#777!important}.cegg-font60{font-size:60%}.egg-container .text-center{text-align:center}.egg-ico-info-circle::before{display:inline-block;flex-shrink:0;width:1em;height:1em;margin-left:.1rem;content:"";vertical-align:-.125em;background-repeat:no-repeat;background-size:1rem 1rem;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23777' viewBox='0 0 16 16'%3E%3Cpath d='M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z'/%3E%3Cpath d='m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z'/%3E%3C/svg%3E") no-repeat center center/100% auto;cursor:pointer;color:#777}
                  </style>
        '''
        html = f'''<!DOCTYPE html>
                    <html lang="en-US">
                       <head>
                          <meta charset="UTF-8">
                          <link rel="profile" href="https://gmpg.org/xfn/11">
                          <meta name='robots' content='index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1' />
                          <!-- This site is optimized with the Yoast SEO plugin v17.3 - https://yoast.com/wordpress/plugins/seo/ -->
                          <title>{keyword}</title>
                
                        {affected}      
                    
                       </head>
                       <body class="home page-template-default page page-id-58973 wp-custom-logo wp-embed-responsive aawp-custom post-image-above-header post-image-aligned-center slideout-enabled slideout-mobile sticky-menu-fade no-sidebar nav-float-right separate-containers header-aligned-left dropdown-hover" itemtype="https://schema.org/WebPage" itemscope>
                          <div id="page" class="site grid-container container hfeed">
                             <div id="content" class="site-content">
                                <div id="primary" class="content-area">
                                   <main id="main" class="site-main">
                                      <article id="post-58973" class="post-58973 page type-page status-publish no-featured-image-padding" itemtype="https://schema.org/CreativeWork" itemscope>
                                         <div class="inside-article">
                                            <header class="entry-header">
        '''
        return html

    def get_footer(self, keyword):
        keyword = keyword.lower().replace(' best ', '').replace('best ', '').replace(' best', '')
        static = f'''
        Do you need {keyword}? Many experts found a lots of feedback online for "<!--KEYWORD-->" and made a shortlist on them. This article where we suggest top 12 products for your ideal {keyword} to choose the overall finest one on online. On selected products where {keyword} you will see ratings. The rating matrix we have generated is based on user ratings found online. Take a look -<br/>
        <h2>Buyer Guide: What you Should know Before Buying {keyword} </h2><br/>
        <br/>You may be wondering, "What do I need to know when shopping for a {keyword}?" Here are some tips that will help you make a good choice.
        <br/><br/>When you want to buy {keyword} for yourself or someone else, you can get confused because there are so many choices. You want the very best for your needs. You also want the best value. You want something you can use over and over. You want it to last a long time. You want it to be easy to use. You want it to be economical. You want it to be comfortable. You want it to be lightweight yet strong. You want it to be a perfect fit. You want it to be easy to maintain. You want it to have a pleasant scent. You want it to be attractive. You want it to be stylish. You want it to be unique. All these are important factors to consider when you are looking to purchase a product.<br/><br/>You should know that the main thing to remember when you are buying anything is that you should never compromise on quality. Make sure that whatever you buy, you can use over and over and it will give you great satisfaction. You should also remember that you don’t necessarily have to spend a lot of money to get high-quality. If you do a little research, you will find that many times, you can get high-quality at a very low price. What you should look for is the best value. You should always check the reviews and testimonials from other customers. You should also make sure the source is reputable.<br/><br/>The products aren’t chosen randomly. We consider several criteria before assembling a list. Some of the criteria are discussed below-<br/><br/><ol><br/><li><strong><u> Brand Value:</u></strong> If you are a buyer, you should always buy from reputable brands. The companies that sell you products will have to work hard to earn their reputation. This means that the company will spend a lot of money to ensure that they produce quality products and services. They also have to invest a lot of money in advertising their products and services so that more people know about them. A brand name is something that is associated with a certain quality. It will have a positive or negative image in the minds of people. If you are a seller, then you should choose well-known brands to get good sales. This is because people would want to buy from brands that have a reputation for delivering quality products and services.</li></ol><br/><br/>We've put together a guide to help you when buying for <!--KEYWORD2-->. Hopefully, it will be useful to you. If you have any questions, let us know. We are here to help you.<br/><br/>The first thing that you should check out is what kind of <!--KEYWORD-->you need. The type of <!--KEYWORD-->you choose should depend on the size and purpose of your event.<br/><br/>Another important factor to consider is the durability of the <!--KEYWORD2-->. You should make sure that it is strong and can withstand any weather condition.<br/><br/>This technology we use to assemble our list depends on a variety of factors, including but not limited to the following:<br/><br/>Gadgetssai has done the best we can with our thoughts and recommendations, but it’s still crucial that you do thorough research on your own for {keyword} that you consider buying. Your questions might include the following:<br/><ul> 	<li>Is it worth buying a {keyword}?</li> 	<li>What benefits are there with buying a it?</li> 	<li>What factors deserve consideration when shopping for an it?</li> 	<li>Why is it crucial to invest in any {keyword}, much less the best one?</li> 	<li>Which {keyword} is good in the current market?</li> 	<li>Where can you find information like this about {keyword}?</li>
        </ul>You should do thorough and mindful research when you are looking for anything. Whether it is a product, service or just about anything else. The more you know about what you are buying, the better off you will be. Always do your own research and don't rely on other people to do it for you. It is your money and your effort and your time. Don't buy anything unless you make sure you really need to. If there is a choice between doing your own research and waiting for someone else to do it for you, always take the time to do the research yourself. This way, you will have complete control over your own destiny.We created the 12-best list. Here is how we did it: Using the data from all of our previous buyers of it, we came up with a list of words and phrases that indicate that a person is most likely to have an positive or negative experience when they use a particular package. Then, using those same lists, we came up with another set of lists that rank the likelihood that a certain product will meet or exceed a customer's expectations.After that, we compared the two sets of lists and identified the products that scored highest in both lists. This gave us a short list of the top 12 products that are, by far, the best overall choices for anyone who is looking for it.<br/><br/>This technology we use to assemble our list depends on a variety of factors, including but not limited to the following:<strong>Brand Value:</strong> Every brand of <!--KEYWORD2--> has a value all its own. Most brands offer some sort of unique selling proposition that’s supposed to bring something different to the table than their competitors.<br/><br/><strong>Features:</strong> What bells and whistles matter for {keyword}?<br/><br/><strong>Specifications:</strong> How powerful they are can be measured.<br/><br/><strong>Product Value:</strong> This simply is how much bang for the buck you get from it.<br/><br/><strong>Customer Ratings:</strong> Number rating grade of it objectively.<br/><br/><strong>Customer Reviews:</strong> Closely related to ratings, these paragraphs give you first-hand and detailed information from real-world users about their products.<br/><br/><strong>Product Quality:</strong> You don’t always get what you pay for, sometimes less, and sometimes more.<br/><br/>Product Reliability: How sturdy and durable it should be an indication of how long it will work out for you.
        '''
        html = f'''</div>
                             </div>
                          </article>
                       </main>
                    </div>
                 </div>
                 {static}
              </div>
           </body>
        </html>'''
        return html

    def make_html_page(self, details):

        static_desc = '''Disclaimer: We are using Amazon affiliate Product Advertising API to fetch products from amazon, include: price, content, image, logo, brand, feature of products which are trademarks of Amazon.com. So, when you buy through links on our site, we may earn an affiliate commission. '''

        html = f'''<h1 class="entry-title" itemprop="headline">{details['keyword']}</h1>
                        </header>
                        <div class="entry-content" itemprop="text">
                           <p><em>{static_desc}<a href="https://www.botticellissouthcongress.com/disclaimer/" target="_blank" rel="noopener noreferrer" data-wpel-link="internal">Read more</a>. </em></p>
                           <h2><span style="color: #3366ff;"><strong>Top 10 Best Products (Key Word)</strong></span></h2>
                           <div class="egg-container cegg-list-withlogos">
                              <div class="egg-listcontainer">
							  
                                <!--Just start the copy point-->
                                 {self.make_products_table(details['products'])}
                              </div>
                           </div>
						   
                           <h2><span style="color: #3366ff;"><strong>Feature of Products</strong></span></h2>
						   
						   <!--Start copy-->
                           
                              {self.make_products_desc(details['products'])}
                                 '''

        header = self.get_header(details['keyword'])

        # with open(f'{BASE_DIR}/html/footer') as footer_file:
        footer = self.get_footer(details['keyword'])

        return f'{header} {html} {footer}'
