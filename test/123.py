# -*- coding:utf-8 -*-
import os
import tempfile
from imgurpython import ImgurClient
from config import client_id, client_secret, album_id, access_token, refresh_token
import requests

client = ImgurClient(client_id, client_secret, access_token, refresh_token)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
ext = 'jpg'
print(static_tmp_path)
r = requests.get('https://api.github.com/events', stream=True)

with tempfile.NamedTemporaryFile('w+b', delete=False) as tf:
    print('inin..........:')
    tempfile_path = tf.name
    print(tempfile_path)
    for chunk in r.iter_content():
        tf.write(chunk)
try:
    print('1..........:')
    dist_path = tempfile_path + '.' + ext
    print(dist_path)
    dist_name = os.path.basename(dist_path)
    print('dist_name:', dist_name)
    print('2..........:')
    os.rename(tempfile_path, dist_path)
    print('3..........:')
    print('tempfile_path:', tempfile_path)
    path = os.path.join(tempfile_path, dist_name)
    print(path)
    # path = ('C:\Users\USER\AppData\Local\Temp') + path
    print('path:', path)
    config = {
            'album': album_id,
            'name': 'test-name!',
            'title': 'test-linebot',
            'description': 'test-description'
        }
    print("Uploading image... ")
    image = client.upload_from_path(path, config=config, anon=False)
    print("Done")
except():
    print('fuck')


