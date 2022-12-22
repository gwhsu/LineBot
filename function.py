import random
from mongodb import *
from linebot.models import *
from extEnv import *
from imgurpython import ImgurClient
from pymongo import MongoClient
import pandas as pd
from selenium import webdriver
from linebot import LineBotApi
import cv2
import os
import time
import json

# get mongoDB database
mongo_client = MongoClient(mongo_client)

# Channel Access Token
line_bot_api = LineBotApi(line_channel_access_token)


def meme(event, msg):
    driverPath = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--start-maximized")  
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome = webdriver.Chrome(executable_path=driverPath, chrome_options=chrome_options)

    chrome.get("https://memes.tw/wtf/api")

    content = chrome.find_element_by_tag_name('pre').text
    parsed_json = json.loads(content)
    print(parsed_json[0]['src'])


def sendTo(event, msg):
    name = msg.split(' ')[1]
    text = msg.split(' ')[2]
    userID = nameMapID(name)
    
    if userID:
        line_bot_api.push_message(userID, TextSendMessage(text=text))
    else:    
        message = TextSendMessage(text="The name was not found")
        line_bot_api.reply_message(event.reply_token, message)


def broadcast(msg):
    text = msg.split(' ')[1]
    line_bot_api.broadcast(TextSendMessage(text=text))


def operationList(event, msg):
    txt = '🔥 ' + 'Hello' + ' 🔥\n'
    txt += '🔥 ' + '抽卡' + ' 🔥\n'
    txt += '🔥 ' + '幹你娘' + ' 🔥\n'
    txt += '🔥 ' + 'CC' + ' 🔥\n'
    txt += '🔥 ' + '占卜 @[str]' + ' 🔥\n'
    txt += '🔥 ' + 'Tofu' + ' 🔥\n'
    txt += '🔥 ' + '!Hulan [str] [int]' + ' 🔥\n'
    txt += '🔥 ' + '!sendTo [name] [str]' + ' 🔥\n'
    txt += '🔥 ' + '!broadcast [str]' + ' 🔥\n'

    message = TextSendMessage(text=txt)
    line_bot_api.reply_message(event.reply_token, message)

def get_pttinfo():
    db = mongo_client.get_database('PTT')
    record = db.beauty_data
    q = record.aggregate([{'$sample': {'size': 1}}])
    for x in q:
        url = x['url']
        rd_img = x['img']
        title = x['title']
    return url, rd_img, title

# return beauty_pttcard
def ptt_drawcard(event, msg):
    url, rd_img, title = get_pttinfo()
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
    line_bot_api.reply_message(event.reply_token, message)

def procast(event, msg):
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

        line_bot_api.reply_message(event.reply_token, message)

    else:
        for x in records.find(myquery):
            message = TextSendMessage(text=x['txt'])
        line_bot_api.reply_message(event.reply_token, message)


def Hulan(event, msg):
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
    line_bot_api.reply_message(event.reply_token, message)

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