# -*- coding:utf-8 -*-

from pymongo import MongoClient
from imgurpython import ImgurClient
from config import client_id, client_secret, access_token, refresh_token
from linebot.models import *

mongo_client = MongoClient('mongodb+srv://test:123@cluster0-lefn4.mongodb.net/test?retryWrites=true&w=majority')
client = ImgurClient(client_id, client_secret, access_token, refresh_token)


def get_pttinfo():
    db = mongo_client.get_database('PTT')
    record = db.beauty_data
    q = record.aggregate([{'$sample': {'size': 1}}])
    for x in q:
        url = x['url']
        rd_img = x['img']
        title = x['title']
    return url, rd_img, title