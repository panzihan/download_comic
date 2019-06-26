#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os
import urllib

import urllib3
from tqdm import tqdm

urllib3.disable_warnings()
http = urllib3.PoolManager()

headers = {
    'Referer': 'https://images.dmzj.com/',
    'Host': 'imgzip.dmzj.com',
    'Connection': 'Keep-Alive',
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.0.0; zh-cn; MI 6 Build/OPR1.170623.027) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    'Accept-Encoding': 'gzip',
}


def get_comic(id):
    url = 'v3api.dmzj.com/comic/%s.json?channel=Android&version=2.7.009' % id
    headers = {
        'Connection': 'Keep-Alive',
        'User-Agent': 'Version/103   Dalvik/2.1.0 (Linux; U; Android 8.0.0; MI 6 MIUI/8.10.11)',
        'Accept-Encoding': 'gzip',
    }
    req = http.request('GET', url, headers=headers, timeout=4.0)
    if req.status == 200:
        json_data = json.loads(req.data.decode('utf-8'))

        first_letter = json_data['first_letter']
        comic_name = json_data['title']
        comic_id = json_data['id']
        str_tip = ""
        chapters = json_data['chapters']
        for index, type in enumerate(chapters):
            str_tip += ' %s、%s \n' % (index, type["title"])
        if len(chapters) > 1:
            key = int(input(str_tip + "有多个类型，请选择：\n"))
            select_chapter(comic_name, comic_id, first_letter, chapters[key]['title'], chapters[key]['data'])
        elif len(chapters) == 0:
            print('无数据')
        else:
            select_chapter(comic_name, comic_id, first_letter, chapters[0]['title'], chapters[0]['data'])


def select_chapter(comic_name, comic_id, first_letter, type_name, chapters):
    str = ""
    for index, chapter in enumerate(chapters):
        str+='%s、%s\t' % (index, chapter['chapter_title'])
    print(str)
    key = input("默认下载全部;单话直接输入序号;多话 起始序号-结束序号(如:0-14):\n")
    if key:
        if key.isdigit():
            download_pic(comic_name, comic_id, type_name, chapters[int(key):int(key)+1], first_letter)
        else:
            a = key.split("-")
            download_pic(comic_name, comic_id, type_name, chapters[int(a[0]):int(a[1]) + 1], first_letter)
    else:
        download_pic(comic_name, comic_id, type_name, chapters, first_letter)


def download_pic(comic_name, comic_id, type_name, chapters, first_letter):
    path = './%s/%s' % (comic_name, type_name)
    pbar = tqdm(chapters)
    for chapter in pbar:
        file_path = '%s/%s.zip' % (path, chapter['chapter_title'])
        zip_file = os.path.exists(file_path)
        pbar.set_description(" %s %s 下载中" % (comic_name, chapter['chapter_title']))
        if zip_file:
            print("zip file is exists")
        else:
            url = 'https://imgzip.dmzj.com/%s/%s/%s.zip' % (first_letter, comic_id, chapter['chapter_id'])
            r = http.request('GET', url, headers=headers, timeout=5.0)
            mkdir(path)
            with open(file_path, "wb") as f:
                f.write(r.data)


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def search(key):
    url = 'https://sacg.dmzj.com/comicsum/search.php?s=' + urllib.parse.quote(key)
    req = http.request('GET', url, timeout=4.0)
    if req.status == 200:
        json_datas = json.loads(req.data.decode('utf-8').replace("var g_search_data = ", "").replace("];", "]"))
        str = ""
        for index, comic in enumerate(json_datas):
            str += ' %s、%s \n' % (index, comic["name"])
        if len(json_datas) > 1:
            key = int(input(str + "有多个搜索结果,请选择:\n"))
            get_comic(json_datas[key]['id'])
        elif len(json_datas) == 0:
            print('无搜索结果')
        else:
            get_comic(json_datas[0]['id'])


if __name__ == '__main__':
    search(input("请输入漫画名:\n"))
