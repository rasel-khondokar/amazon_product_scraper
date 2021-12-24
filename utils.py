import logging
import os
import requests

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