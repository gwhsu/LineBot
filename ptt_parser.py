import ptt
import random
from bs4 import BeautifulSoup
import re
import requests


def get_metadata(candidate, title):
    # 取得文章列表基本資訊
    # 'beauty'
    board = ptt.Board('beauty')
    meta = board.get_meta(num=20)

    assert len(meta) == 20
    # print(meta)
    for m in meta:
        '''
        print(f'推文數: {m.push} ',
            f'標記: {m.mark} ',
            f'標題: {m.title} ',
            f'日期: {m.date} ',
            f'作者: {m.author} ',
            f'連結: {m.link} ',
            f'文章檔案編號: {m.filename} ',
            )
        '''
        try:
            push = int(m.push)
            print(push, m.link)
            if push > 10:
                candidate.append(m.link)
                title.append(m.title)
        except :
            print("error")


def get_after_metadata():
    # 取得特定文章後的幾篇資訊
    board = ptt.Board('beauty')
    meta = board.get_meta(num=20)
    meta = board.get_meta(num=5, after_filename='M.1536559731.A.AE2')

    assert len(meta) == 5


def get_post_content():
    # 取得完整文章資訊
    board = ptt.Board('beauty')
    meta = board.get_meta(num=1)

    post = board.get_post(link=meta[0].link)
    print(dir(post))
    print(post)


def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}  # ptt18歲的認證
    )
    if resp.status_code != 200:  # 回傳200代表正常
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls


'''
def get_pttinfo():
    candidate = []
    title = []
    get_metadata(candidate, title)
    candidate = candidate[2:]
    rd_candidate = random.choice(candidate)
    # print(candidate)
    # print(title)
    title = title[2:]
    # print(rd_candidate)
    index = candidate.index(rd_candidate)
    # print(index)
    # print (title[index])
    url = 'https://www.ptt.cc' + rd_candidate
    response = requests.get(url)
    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    rd_img = random.choice(parse(get_web_page(url)))
    print(rd_img)
    if '.jpg' not in rd_img:
        rd_img = rd_img + '.jpg'

    return url, rd_img, title[index]
'''