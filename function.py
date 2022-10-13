import random
from linebot.models import *
from imgurpython import ImgurClient
from pip import main
from pymongo import MongoClient
import pandas as pd
from selenium import webdriver
import cv2
import os
import time
from selenium.webdriver.chrome.options import Options
from config import client_id, client_secret, access_token, refresh_token, album_id
mongo_client = MongoClient('mongodb+srv://test:123@cluster0-lefn4.mongodb.net/test?retryWrites=true&w=majority')


def set_msg(msg):
    if 'CC' in msg:
        msg = '你在笑什麼'
        message = TextSendMessage(text=msg)

    return message

def get_pttinfo():
    db = mongo_client.get_database('PTT')
    record = db.beauty_data
    q = record.aggregate([{'$sample': {'size': 1}}])
    for x in q:
        url = x['url']
        rd_img = x['img']
        title = x['title']
    return url, rd_img, title

#return beauty_pttcard
def ptt_drawcard(url, rd_img, title):
    title = title[0:12]
    print("urL::", url)
    message = TemplateSendMessage(
        alt_text='今日運勢',

        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url=rd_img,
                    action=URITemplateAction(
                        label=title,
                        uri=url
                    )
                )
            ]
        )
    )
    return message

def procast(msg):
    db = mongo_client.get_database('linebot')
    records = db.personality
    df = pd.read_csv("data/personality1.csv")
    rd = random.randint(0, 73)
    name = msg.split('@')[1]
    score = rd + 26
    myquery = {"Name": name}
    count_p = records.count_documents(myquery)
    if count_p == 0:
        txt = '🔥 ' + name + '的人品分數: '+ str(score)+' 🔥\n'
        txt = txt + str(df.iloc[rd, 0])
        new_msg = {
            'Name': name,
            'score': score,
            'txt': txt
        }
        records.insert_one(new_msg)
        message = TextSendMessage(text=txt)

        return message

    else:
        for x in records.find(myquery):
            message = TextSendMessage(text=x['txt'])
        return message

def Hulan(msg):
    print('Start REQUEST')
    msg_ = msg.split(' ')
    id_ = msg_[1]
    len_ = msg_[2]

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # chrome = webdriver.Chrome()
    chrome.get("https://howtobullshit.me/")

    topic = chrome.find_element_by_id("topic")
    minlen = chrome.find_element_by_id("minlen")

    topic.send_keys(id_)
    minlen.send_keys(len_)

    chrome.find_element_by_id("btn-get-bullshit").click()
    time.sleep(3)

    content = chrome.find_element_by_id("content")

    message = TextSendMessage(text=content.text)

    return message

def img2anime(img_path):
    static_tmp_path = os.path.join(os.path.dirname(__file__))
    print(static_tmp_path)
    img_path = static_tmp_path + '/' + img_path
    print(img_path)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--start-maximized")  
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    chrome.get("https://animefilter.com/")

    image = cv2.imread(img_path)

    height, width = image.shape[0], image.shape[1]
    width_new = 300
    height_new = 300

    if width / height >= width_new / height_new:
        img_new = cv2.resize(image, (width_new, int(height * width_new / width)))
    else:
        img_new = cv2.resize(image, (int(width * height_new / height), height_new))
    
    cv2.imwrite(img_path, img_new)

    chrome.find_element_by_xpath('//input[@type="file"]').send_keys(img_path)
    alert = chrome.switch_to.alert
    alert.accept()  # accept alert
    time.sleep(25)

    with open('output.png', 'wb') as file:
        image = chrome.find_element_by_xpath('//*[@id="outputEl"]/div/div/img')
        image = image.screenshot_as_png
        file.write(image)

    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    config = {
        'album': album_id,
        'name': 'Catastrophe!',
        'title': 'Catastrophe!',
        'description': 'Catastrophe '
    }
    client.upload_from_path('output.png', config=config, anon=False)

    for image in client.get_album_images(album_id):
        image_title = image.title if image.title else 'Untitled'
    print(image.link)

    return image.link