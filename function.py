from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import random
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from imgurpython import ImgurClient
from pymongo import MongoClient
import pandas as pd
from config import client_id, client_secret, access_token, refresh_token
mongo_client = MongoClient('mongodb+srv://test:123@cluster0-lefn4.mongodb.net/test?retryWrites=true&w=majority')
client = ImgurClient(client_id, client_secret, access_token, refresh_token)


def set_msg(msg):
    if 'CC' in msg:
        msg = '你在笑什麼'
        message = TextSendMessage(text=msg)

    return message


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
            'txt':txt
        }
        records.insert_one(new_msg)

        message = TextSendMessage(text=txt)
        return message

    else:
        for x in records.find(myquery):
            message = TextSendMessage(text=x['txt'])
        return message
