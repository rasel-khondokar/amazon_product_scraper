import logging
import os
import requests
from datetime import datetime

from settings import DIRNAME_ERROR_LOG, TIME_ZONE


def make_dir_if_not_exists(file_path):
    dirs = file_path.split('/')
    if dirs:
        path = ''
        for dir in dirs:
            if dir:
                path = path + dir + '/'
                if not os.path.exists(path):
                    os.mkdir(path)

def process_keyword(keyword):
    keyword = keyword.lower().replace(' best ', '').replace('best ', '').replace(' best', '').replace(' ', '+')
    return keyword

def image_downloader(img_url, img_name, img_path):
    try:
        jpg_ext = ['.jpg', 'jpeg']
        if img_url[-4:] == '.jpg':
            image_file_name = f"{img_path}{img_name.replace('/', '_')}{'.jpg'}"
        elif img_url[-4:] == 'jpeg':
            image_file_name = f"{img_path}{img_name.replace('/', '_')}{'.jpeg'}"
        else:
            image_file_name = f"{img_path}{img_name.replace('/', '_')}{'.png'}"
        # urllib.request.urlretrieve(img_url, image_file_name)
        f = open(image_file_name, 'wb')
        f.write(requests.get(img_url).content)
        f.close()
        print(f"Image downloaded to {img_path}!")
    except Exception as e:
        logging.exception(e)

def save_error_log(name):
    error_log = logging.getLogger(name)
    error_log_formatter = logging.Formatter('%(asctime)s : %(message)s')
    make_dir_if_not_exists(DIRNAME_ERROR_LOG)
    today = datetime.now().astimezone(TIME_ZONE).strftime('%Y-%m-%d')
    make_dir_if_not_exists(DIRNAME_ERROR_LOG + today + '/')
    error_log_file = logging.FileHandler(DIRNAME_ERROR_LOG + today + '/' + name + '.log', mode='a')
    error_log_file.setFormatter(error_log_formatter)
    error_log.setLevel(logging.ERROR)
    error_log.addHandler(error_log_file)
    return logging.getLogger(name)