import time
import datetime

from urllib import request
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from sa_package.my_selenium.webdriver import MyChromeDriver


TIMEOUT = 30

def get_video_tag(video_id, driver=None):

    # video id를 받아서 해당 영상의 게임 태그를 돌려주는 함수

    need_to_close_driver = False

    if driver is None:
        driver = MyChromeDriver()
        need_to_close_driver = True

    try:
        driver.get("https://www.youtube.com/watch?v="+video_id)
        WebDriverWait(driver, timeout=10).until(lambda x: x.find_element(By.CSS_SELECTOR, 'div#text-container > div#title'))
        
        tag_title = driver.find_element(By.CSS_SELECTOR, 'div#text-container > div#title').text

        if "댓글이 사용 중지되었습니다" in tag_title:
            raise
        if "YouTube Kids 사용해 보기" in tag_title:
            raise
        if "인터넷" in tag_title:
            raise

    except Exception as e:
        tag_title = ""

    if need_to_close_driver:
        driver.close()

    return tag_title


def get_video_info(video_id):

    video_info = {}

    req = request.Request(f"https://www.youtube.com/watch?v={video_id}")
    data = request.urlopen(req).read()
    soup = BeautifulSoup(data, "html.parser")

    main_data = soup.find(class_="watch-main-col")
    
    # 비디오 제목
    video_title = main_data.find("meta", itemprop="name")["content"]
    video_info["title"] = video_title
    
    # 업로드 날짜
    upload_date = main_data.find("meta", itemprop="uploadDate")["content"]
    upload_datetime = datetime.datetime.strptime(upload_date, "%Y-%m-%d")
    video_info['upload_date'] = datetime.date(upload_datetime.year, upload_datetime.month, upload_datetime.day)

    # 채널 ID
    channel_id = main_data.find("meta", itemprop="channelId")["content"]
    video_info["channel_id"] = channel_id
    
    return video_info


def get_channel_id_from_yt_link(url, link_type="video"):

    channel_id = None


    if link_type == "video":

        req = request.Request(url)
        data = request.urlopen(req).read()

        soup = BeautifulSoup(data, "html.parser")

        main_data = soup.find(class_="watch-main-col")
        channel_id = main_data.find("meta", itemprop="channelId")["content"]

    elif link_type == "channel":
        req = request.Request(link)
        data = request.urlopen(req).read()

        soup = BeautifulSoup(data, "html.parser")

        if soup.find(rel="canonical") is not None:
            channel_id = soup.find(rel="canonical")["href"].split("/")[-1]

    return channel_id


def get_video_id_from_yt_link(url):

    req = request.Request(url)
    data = request.urlopen(req).read()

    soup = BeautifulSoup(data, "html.parser")

    main_data = soup.find(class_="watch-main-col")
    video_id = main_data.find("meta", itemprop="videoId")["content"]

    return video_id


def get_recent_vod_list(channel_id, start_date=None, need_to_be_certain=False, driver=None):
    
    keep_crawling = True
    page_index = 0
    
    video_id_list = []

    need_to_close = False
    if driver is None:
        driver = MyChromeDriver()
        need_to_close = True

    driver.get(f"https://www.youtube.com/channel/{channel_id}/videos") 
    WebDriverWait(driver, timeout=10).until(lambda x: x.find_elements(By.CSS_SELECTOR, 'a#thumbnail'))

    # 동영상 탭이 있는지 확인하기
    tab_list = []
    for tab in driver.find_elements(By.CSS_SELECTOR, "#tabsContent > tp-yt-paper-tab"):
        tab_list.append(tab.text)
    if "동영상" not in tab_list:
        return []

    while keep_crawling:
        WebDriverWait(driver, timeout=10).until(lambda x: x.find_elements(By.CSS_SELECTOR, 'a#thumbnail'))
        tmp_video_list = driver.find_elements(By.CSS_SELECTOR, 'a#thumbnail')

        for video in tmp_video_list:
            link = video.get_attribute("href")
            if link is not None:
                video_id = link.split("&")[0].split("watch?v=")[1]

                if video_id not in video_id_list:
                    video_id_list.append(video_id)

        if start_date is None:
            return video_id_list

        if len(video_id_list) == 0:
            return video_id_list
        
        upload_date = get_video_info(video_id=video_id_list[-1])["upload_date"]


        if upload_date is None or upload_date > start_date:
            keep_crawling = True
            driver.execute_script(f"window.scrollTo({10000*page_index}, {10000*(page_index+1)});")
            page_index += 1
        else:
            keep_crawling = False


    if need_to_be_certain:
        for idx, vod_id in enumerate(video_id_list[::-1]):
            if get_video_info(video_id=vod_id)["upload_date"] >= start_date:
                break
    
        if need_to_close:
            driver.close()

        return video_id_list[:-(idx)]

    else:
        return video_id_list


def get_recent_shorts_list(channel_id, scroll_num=1, driver=None):
    
    video_id_list = []

    need_to_close = False
    if driver is None:
        driver = MyChromeDriver()
        need_to_close = True

    driver.get(f"https://www.youtube.com/channel/{channel_id}/shorts") 
    WebDriverWait(driver, timeout=10).until(lambda x: x.find_elements(By.CSS_SELECTOR, 'a#thumbnail'))

    # Shorts 탭이 있는지 확인하기
    tab_list = []
    for tab in driver.find_elements(By.CSS_SELECTOR, "#tabsContent > tp-yt-paper-tab"):
        tab_list.append(tab.text)
    if "SHORTS" not in tab_list:
        return []

    # 스크롤 내려서 더 많은 영상 로딩하기
    for _ in range(scroll_num):
        driver.execute_script(f"window.scrollTo(0, 10000);")
        time.sleep(3)

    tmp_video_list = driver.find_elements(By.CSS_SELECTOR, 'a#thumbnail')

    for video in tmp_video_list:
        link = video.get_attribute("href")
        # print(link)
        if link is not None:
            video_id = link.split("&")[0].split("shorts/")[1]

            if video_id not in video_id_list:
                video_id_list.append(video_id)

    if need_to_close:
        driver.close()

    return video_id_list