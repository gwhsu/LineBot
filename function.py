import random
from linebot.models import *
from imgurpython import ImgurClient
from pymongo import MongoClient
import pandas as pd
from selenium import webdriver
import os
import time


from config import client_id, client_secret, access_token, refresh_token
mongo_client = MongoClient('mongodb+srv://test:123@cluster0-lefn4.mongodb.net/test?retryWrites=true&w=majority')
client = ImgurClient(client_id, client_secret, access_token, refresh_token)


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
    df = pd.read_csv("personality1.csv")
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

    print(chrome.page_source)
    message = TextSendMessage(text=content.text)

    return message