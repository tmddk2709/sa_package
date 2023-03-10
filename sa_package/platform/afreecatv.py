
import time
import datetime
import pandas as pd
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException

from sa_package.my_selenium.webdriver import MyChromeDriver
from sa_package.convert.time_format import convert_hhmmss_format_to_sec
from sa_package.convert.number_format import convert_hannum_to_num

import warnings
warnings.filterwarnings('ignore')

afreeca_home_url = "https://afreecatv.com/"

class AfreecaTVDriver(MyChromeDriver):

    def __init__(self, **kwargs):
        
        self.__kwargs = kwargs

        headless = self.__kwargs.get("headless", False)
        maximize = self.__kwargs.get("maximize", True)

        super().__init__(headless=headless, maximize=maximize)
        
        self.__login_id = self.__kwargs.get("login_id", None)
        self.__login_pwd = self.__kwargs.get("login_pwd", None)

        if self.__login_id is not None:
            self.login(self.__login_id, self.__login_pwd)

        self.setting()

        self.to_home()


    # 로그인
    def login(self, login_id, login_pwd):

        self.__login_id = login_id
        self.__login_pwd = login_pwd

        login_url = "https://login.afreecatv.com/afreeca/login.php?szFrom=full&request_uri=https%3A%2F%2Fwww.afreecatv.com%2F"
        self.get(login_url)

        WebDriverWait(self, timeout=30).until(lambda x: x.find_element(By.CSS_SELECTOR, '#uid'))

        # 로그인 ID 입력
        self.find_element(By.CSS_SELECTOR, '#uid').send_keys(self.__login_id)
        # 로그인 PWD 입력
        self.find_element(By.CSS_SELECTOR, '#password').send_keys(self.__login_pwd)
        # 로그인 버튼 클릭
        self.find_element(By.CSS_SELECTOR, 'body > form:nth-child(11) > div > fieldset > p.login_btn > button').click()

        time.sleep(1)


    # 홈화면으로 이동
    def to_home(self):
        self.get(afreeca_home_url)


    # 세팅
    def setting(self):

        sample_vod_url = "https://vod.afreecatv.com/player/93937795"
        self.get(sample_vod_url)
        time.sleep(3)

        print("--- 세팅 중 ---")
        
        #자동재생 설정
        try:
            if self.find_element(By.CSS_SELECTOR, '#autoplay').get_attribute("checked") == 'true':
                print("   자동재생 끄기")
                self.find_element(By.XPATH, '//*[@id="tabList"]/dl[1]/dt/label/span').click()
                time.sleep(0.5)
        except Exception as e:
            print(e)
            pass


        # 리스트 끄기
        try:
            self.find_element(By.CSS_SELECTOR, '.webplayer_vod.list_open')
            print("   list 끄기")
            
            self.find_element(By.CSS_SELECTOR, '#list_area > div.area_header > ul > li.close > a').click()
            time.sleep(0.5)

        except Exception as e:
            
            pass
        
        # 재생버튼 클릭
        try:
            time.sleep(3)
            self.find_element(By.CSS_SELECTOR, '#afreecatv_player > div.nextvideo > dl > dd.nextplay > a').click()
            time.sleep(1)
        except Exception as e:
            pass
        
        # 알림창 있는 경우 사라질 때까지 기다리기
        while len(self.find_elements(By.CSS_SELECTOR, '.alert_text')) > 0:
            time.sleep(1)
            

        # 채팅창 끄기
        try:        
            self.find_element(By.CSS_SELECTOR, '.webplayer_vod.chat_open')
            print("   채팅창 끄기")

            self.find_element(By.CSS_SELECTOR, '#chatting_area > div > div.area_header > ul > li.close > a').click()
            time.sleep(0.5)

        except Exception as e:
            pass

        # 애드벌룬 있는 경우 끄기
        try:
            if self.find_element(By.CSS_SELECTOR, '#player_area > div.htmlplayer_wrap > div > div.player_item_list.playbackrate.pip.statistics.smallest > ul > li.adballoon > div.speech_bubble').get_attribute("style") == 'display: block;':
                self.find_element(By.CSS_SELECTOR, '#player_area > div.htmlplayer_wrap > div > div.player_item_list.playbackrate.pip.statistics.smallest > ul > li.adballoon > div.speech_bubble > a').click()
                print("   애드벌룬 끄기")
                time.sleep(0.5)
        except Exception as e:
            pass



def get_vod_list_month_range(driver, bj_id, start_month, end_month):

    need_to_close = True
    
    if driver is None:
        driver = AfreecaTVDriver()
    else:
        need_to_close = False
    
    vod_df = pd.DataFrame(columns=['bj_id', 'vod_id', 'title', 'date', 'vod_time'])
    page = 1

    while True:
        driver.get(f"https://bj.afreecatv.com/{bj_id}/vods/review?page={page}&months={start_month}{end_month}&perPage=60")
        time.sleep(5)

        vod_list = driver.find_element(By.CSS_SELECTOR, 'section.vod-list').find_elements(By.CSS_SELECTOR, 'li')
        if len(vod_list) <= 1:
            break

        for vod in vod_list:
            vod_id = vod.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split("/")[-1]
            title = vod.find_element(By.CSS_SELECTOR, 'p.title').text
            vod_date = vod.find_element(By.CSS_SELECTOR, 'span.date').text
            vod_time = convert_hhmmss_format_to_sec(vod.find_element(By.CSS_SELECTOR, 'span.time').text)
            tmp_df = pd.DataFrame([{
                'bj_id':bj_id,
                'vod_id':vod_id, 
                'title':title,
                'date':vod_date,
                'vod_time':vod_time
                }])

            vod_df = pd.concat([vod_df, tmp_df], ignore_index=True)
    
        page += 1

    if need_to_close:
        driver.close()

    return vod_df



def get_vod_list(bj_id, perPage=20, driver=None):

    """
    start_month : yyyymm
    end_month : yyyymm
    """

    need_to_close = True
    
    if driver is None:
        driver = AfreecaTVDriver()
    else:
        need_to_close = False
    
    vod_df = pd.DataFrame(columns=['bj_id', 'vod_id', 'title', 'date', 'vod_time'])

    driver.get(f"https://bj.afreecatv.com/{bj_id}/vods/review?page=1&perPage={perPage}")
    time.sleep(5)

    vod_list = driver.find_element(By.CSS_SELECTOR, 'section.vod-list').find_elements(By.CSS_SELECTOR, 'li')
    if len(vod_list) <= 1:
        return None

    for vod in vod_list:
        vod_id = vod.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split("/")[-1]
        title = vod.find_element(By.CSS_SELECTOR, 'p.title').text
        vod_date = vod.find_element(By.CSS_SELECTOR, 'span.date').text
        vod_time = convert_hhmmss_format_to_sec(vod.find_element(By.CSS_SELECTOR, 'span.time').text)
        tmp_df = pd.DataFrame([{
            'bj_id':bj_id,
            'vod_id':vod_id, 
            'title':title,
            'date':vod_date,
            'vod_time':vod_time
            }])

        vod_df = pd.concat([vod_df, tmp_df], ignore_index=True)

    if need_to_close:
        driver.close()

    return vod_df



def get_bj_nick(bj_id, driver=None):
    
    need_to_close = True

    if driver is None:
        driver = AfreecaTVDriver()
        time.sleep(3)
    else:
        need_to_close = False
    
    driver.get(f"https://bj.afreecatv.com/{bj_id}")
    time.sleep(3)
    nick = driver.find_element(By.CSS_SELECTOR, 'div.nick').text.split("\n")[0]
    
    if need_to_close:
        driver.close()

    return nick



def get_favor_num(bj_id, driver=None):
    
    need_to_close = True

    if driver is None:
        driver = AfreecaTVDriver()
    else:
        need_to_close = False

    driver.get(f"https://bj.afreecatv.com/{bj_id}")
    time.sleep(3)

    favor_num = convert_hannum_to_num(driver.find_elements(By.CSS_SELECTOR, "button.favor")[1].text.split("즐겨찾기")[1], is_int=True)
    
    if need_to_close:
        driver.close()

    return favor_num



def get_vod_viewer_info(vod_id, vod_time, driver=None):

    vod_info_df = pd.DataFrame(columns=["accv", "pccv", "chat", "방송시간", "라이브 참여", "해상도", "카테고리", "보관기간"])

    if driver is None:
        driver = AfreecaTVDriver()

    link = f"https://vod.afreecatv.com/player/{vod_id}?change_second={vod_time-15}"
    link = f"https://vod.afreecatv.com/player/{vod_id}?change_second=1"
    driver.get(link)


    # 재생버튼 클릭
    try:
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, '#afreecatv_player > div.nextvideo > dl > dd.nextplay > a').click()
        time.sleep(1)
    except Exception as e:
        pass


    # 광고 나오고 있는 경우 skip 버튼 기다려서 skip 버튼 누르기
    # if driver.find_element(By.CSS_SELECTOR, '#da_area_id').get_attribute("style") == "":

    #     skip_button = driver.find_element(By.CSS_SELECTOR, '#afreecatv_player > button.da_area_right')
    #     skip_text = skip_button.text

    #     if "초 후" in skip_text:
    #         skip_sec = int(skip_text.split("초")[0])+2
    #     else:
    #         skip_sec = 2

    #     try:
    #         time.sleep(skip_sec)
    #         skip_button.click()
    #     except Exception as e:
    #         time.sleep(15)


    # 일시정지
    try:
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="videoLayerCover"]').click()
        time.sleep(0.5)

    except Exception as e:
        # 영상이 뒤에 끊겼는데도 영상이 계속 이어지는 경우는 일시정지 버튼 클릭 불가능
        pass


    # 알림창 있는 경우 사라질 때까지 기다리기
    while len(driver.find_elements(By.CSS_SELECTOR, '.alert_text')) > 0:
        time.sleep(1)

    # 애드벌룬 있는 경우 끄기
    try:
        if driver.find_element(By.CSS_SELECTOR, '#player_area > div.htmlplayer_wrap > div > div.player_item_list.playbackrate.pip.statistics.smallest > ul > li.adballoon > div.speech_bubble').get_attribute("style") == 'display: block;':
            driver.find_element(By.CSS_SELECTOR, '#player_area > div.htmlplayer_wrap > div > div.player_item_list.playbackrate.pip.statistics.smallest > ul > li.adballoon > div.speech_bubble > a').click()
            time.sleep(0.5)
    except Exception as e:
        pass
    

    # 스크린모드
    if len(driver.find_elements(By.CSS_SELECTOR, '.smode')) == 0:
        screenmode_button = driver.find_element(By.CSS_SELECTOR, '#btnSmode')
        a = ActionChains(driver)
        a.move_to_element(screenmode_button).perform()
        screenmode_button.click()


    # 방송 별별통계 클릭
    try:
        
        star_stat_button = driver.find_element(By.CSS_SELECTOR, '.btn_statistics')
        a = ActionChains(driver)
        a.move_to_element(star_stat_button).perform() # 아래 메뉴 나오도록 호버링
        star_stat_button.click()
        time.sleep(1)

    except ElementClickInterceptedException:
        time.sleep(3)
        star_stat_button = driver.find_element(By.CSS_SELECTOR, '.btn_statistics')
        a = ActionChains(driver)
        a.move_to_element(star_stat_button).perform() # 아래 메뉴 나오도록 호버링
        star_stat_button.click()

    except Exception as e:
        print(e)
        

    try:

        target_li = None
        for li_idx, li in enumerate(driver.find_elements(By.CSS_SELECTOR, '.statistics_list_contents > ul > li')):
            if li.find_element(By.CSS_SELECTOR, 'button').text == '유저 수 그래프':
                target_li = li
                break
            
        if target_li is None:
            vod_info_df.loc[0, "accv"] = "데이터 없음"
            vod_info_df.loc[0, "pccv"] = "데이터 없음"

        else:

            time.sleep(0.5)
            target_li.click()
            time.sleep(1)

            # 별별통계 데이터가 존재하지 않는 경우
            if len(driver.find_elements(By.CSS_SELECTOR, ".ui-pop.statistics_layer > div.pop-body")) > 0:
                if driver.find_element(By.CSS_SELECTOR, ".ui-pop.statistics_layer > div.pop-body").text == "해당 데이터가 존재하지 않습니다.":
                    print("별별통계 데이터 없음")
                
                    vod_info_df.loc[0, "accv"] = "데이터 없음"
                    vod_info_df.loc[0, "pccv"] = "데이터 없음"

                    driver.find_element(By.CSS_SELECTOR, "#star2statAlert > div.pop-btn.line > a").click()
                    time.sleep(0.5)

            else:
                
                WebDriverWait(driver, timeout=10).until(lambda x: x.find_element(By.CSS_SELECTOR, "g.highcharts-series-group > g.highcharts-series"))

                # PCCV
                a = ActionChains(driver)
                peak = driver.find_element(By.CSS_SELECTOR, 'g.highcharts-series-group > g.highcharts-markers.highcharts-tracker > path:nth-child(1)')

                a.move_to_element(peak).perform()
                time.sleep(0.5)
                a.move_to_element(peak).perform()
                tooltip = driver.find_element(By.CSS_SELECTOR, 'g.highcharts-tooltip')

                # PCCV가 0으로 나오는 경우
                if int(tooltip.text.split("명")[0].replace(",", "")) == 0:
                    raise ValueError
                
                vod_info_df.loc[0, "pccv"] = int(tooltip.text.split("명")[0].replace(",", ""))
                
                # ACCV
                data = driver.find_element(By.CSS_SELECTOR, 'svg > g.highcharts-series-group > g.highcharts-series > path:nth-child(1)').get_attribute("d")
                y_range = float(data.split(" L ")[0].split()[-1])
                cleansed_data = data.split(" L ")[1:-1]
                df = pd.DataFrame({'data':cleansed_data})
                df['x'] = df['data'].apply(lambda x: float(x.split()[0]))
                df['y'] = df['data'].apply(lambda x: y_range - float(x.split()[1]))
                y_max = max(df['y'])

                df['ccv'] = df['y'].apply(lambda x: int(x*vod_info_df.loc[0, "pccv"]/y_max))
                vod_info_df.loc[0, "accv"] = int(df['ccv'].mean())
                time.sleep(1)

    except Exception as e:
        adballoon_bubble = driver.find_elements(By.CSS_SELECTOR, '#player_area > div.htmlplayer_wrap > div > div.player_item_list.playbackrate.pip.statistics > ul > li.adballoon > div.speech_bubble')
        if len(adballoon_bubble) > 0 and adballoon_bubble[0].get_attribute("style") == 'display: block;':
            driver.find_element(By.CSS_SELECTOR, '#player_area > div.htmlplayer_wrap > div > div.player_item_list.playbackrate.pip.statistics > ul > li.adballoon > div.speech_bubble > a').click()
        print(e)


    try:
        for li_idx, li in enumerate(driver.find_elements(By.CSS_SELECTOR, '.statistics_list_contents > ul > li')):
            if li.find_element(By.CSS_SELECTOR, 'button').text == '채팅 수 그래프':
                target_li = li
                break

        if target_li is None:
            vod_info_df.loc[0, "chat"] = "데이터 없음"

        else:
            time.sleep(0.5)
            target_li.click()
            time.sleep(1)

            # 별별통계 데이터가 존재하지 않는 경우
            if len(driver.find_elements(By.CSS_SELECTOR, ".ui-pop.statistics_layer > div.pop-body")) > 0:
                if driver.find_element(By.CSS_SELECTOR, ".ui-pop.statistics_layer > div.pop-body").text == "해당 데이터가 존재하지 않습니다.":
                    print("별별통계 데이터 없음")
                
                    vod_info_df.loc[0, "chat"] = "데이터 없음"

                    driver.find_element(By.CSS_SELECTOR, "#star2statAlert > div.pop-btn.line > a").click()
                    time.sleep(0.5)

            else:
                
                WebDriverWait(driver, timeout=10).until(lambda x: x.find_element(By.CSS_SELECTOR, "g.highcharts-series-group > g.highcharts-series"))

                # max_chat
                a = ActionChains(driver)
                peak = driver.find_element(By.CSS_SELECTOR, 'g.highcharts-series-group > g.highcharts-markers.highcharts-tracker > path:nth-child(1)')

                a.move_to_element(peak).perform()
                time.sleep(0.5)
                a.move_to_element(peak).perform()
                tooltip = driver.find_element(By.CSS_SELECTOR, 'g.highcharts-tooltip')
                
                if "명" in tooltip.text:
                    time.sleep(5)
                    a = ActionChains(driver)
                    peak = driver.find_element(By.CSS_SELECTOR, 'g.highcharts-series-group > g.highcharts-markers.highcharts-tracker > path:nth-child(1)')

                    a.move_to_element(peak).perform()
                    time.sleep(0.5)
                    a.move_to_element(peak).perform()
                    tooltip = driver.find_element(By.CSS_SELECTOR, 'g.highcharts-tooltip')

                max_chat = int(tooltip.text.split("채팅 ")[1].split("개")[0].replace(",", ""))

                # chat
                data = driver.find_element(By.CSS_SELECTOR, 'svg > g.highcharts-series-group > g.highcharts-series > path:nth-child(1)').get_attribute("d")
                y_range = float(data.split(" L ")[0].split()[-1])
                cleansed_data = data.split(" L ")[1:-1]
                chat_df = pd.DataFrame({'data':cleansed_data})
                chat_df['x'] = chat_df['data'].apply(lambda x: float(x.split()[0]))
                chat_df['y'] = chat_df['data'].apply(lambda x: y_range - float(x.split()[1]))
                y_max = max(chat_df['y'])

                chat_df['chat'] = chat_df['y'].apply(lambda x: int(x*max_chat/y_max))

                vod_info_df.loc[0, "chat"] = int(chat_df['chat'].sum())
                
    except Exception as e:
        print(e)


    # 기타 라이브 정보
    try:
        driver.find_element(By.CSS_SELECTOR, 'div.broadcast_information > div.text_information > button').click()
        time.sleep(0.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        detail_data = soup.find("ul", class_="detail_view")
        for li in detail_data.find_all("li"):
            tag_name = li.find("strong").text
            tag_value = li.find("span").text
            vod_info_df.loc[0, tag_name] = tag_value

    except Exception as e:
        vod_info_df.loc[0, "방송시간"] = ""
        vod_info_df.loc[0, "카테고리"] = ""
        print(e)

    return vod_info_df

