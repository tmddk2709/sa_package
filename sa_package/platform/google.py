import time
import onetimepass as otp

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sa_package.my_selenium.webdriver import MyChromeDriver

TIMEOUT = 10


def get_signed_in_google_driver(login_id, login_pwd, secret_key):
    
    driver = MyChromeDriver()

    google_login_url = "https://accounts.google.com/v3/signin/identifier?dsh=S-1659938691%3A1673181065994169&continue=https%3A%2F%2Fwww.google.co.kr%2F&ec=GAZAmgQ&hl=ko&passive=true&flowName=GlifWebSignIn&flowEntry=ServiceLogin&ifkv=AeAAQh70mrY_65UB8exoFTOAzHkwkl1Xm6EE-iuOz8j_lLTHN7iwU5HnbD5Xxz4BNtuUTDMUaggU_g"
    driver.get(google_login_url)

    # 아이디 입력
    driver.find_element(By.XPATH, '//*[@id="identifierId"]').send_keys(login_id)
    driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button').click()
    WebDriverWait(driver, timeout=TIMEOUT).until(lambda x: x.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input'))
    time.sleep(1)

    # 패스워드 입력
    driver.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(login_pwd)
    driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button').click()

    try:
        # 다른 인증 방법 선택
        other_auth_xpath =  '//*[@id="view_container"]/div/div/div[2]/div/div[2]/div[2]/div[2]/div/div/button/span'
        WebDriverWait(driver, timeout=TIMEOUT).until(lambda x: x.find_element(By.XPATH, other_auth_xpath))
        time.sleep(1)
        driver.find_element(By.XPATH, other_auth_xpath).click()

        # otp 인증 선택
        otp_auth_xpath =  '//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/ul/li[2]/div/div[2]'
        WebDriverWait(driver, timeout=TIMEOUT).until(lambda x: x.find_element(By.XPATH, otp_auth_xpath))
        time.sleep(1)
        driver.find_element(By.XPATH, otp_auth_xpath).click()

    except Exception as e:
        # 실패한 시도 횟수 많은 경우 opt 인증 선택으로 바로 이동
        otp_auth_xpath =  '//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/ul/li[2]/div/div[2]'
        WebDriverWait(driver, timeout=TIMEOUT).until(lambda x: x.find_element(By.XPATH, otp_auth_xpath))
        time.sleep(1)
        driver.find_element(By.XPATH, otp_auth_xpath).click()


    # 코드 입력
    code_input_xpath = '//*[@id="totpPin"]'
    WebDriverWait(driver, timeout=TIMEOUT).until(lambda x: x.find_element(By.XPATH, code_input_xpath))

    try_num = 0

    while try_num < 5:
        # otp 코드 받기
        code = otp.get_totp(secret_key)

        # otp 코드 입력
        time.sleep(1)
        driver.find_element(By.XPATH, code_input_xpath).send_keys(code)
        time.sleep(1)

        # 다음 버튼
        next_btn_xpath = '//*[@id="totpNext"]/div/button/span'
        WebDriverWait(driver, timeout=TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, next_btn_xpath)))
        driver.find_element(By.XPATH, next_btn_xpath).click()
        

        while True:
            time.sleep(3)
            # 로그인 여부 확인
            account_img = driver.find_elements(By.XPATH, '//*[@id="gb"]/div/div[2]/div[2]/div/a')
            if len(account_img) > 0:
                return driver
            else:
                # 코드 잘못된 경우 확인
                err_msg = driver.find_elements(By.XPATH, '//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[2]/div/div[2]/div[2]/div')
                if len(err_msg) > 0:
                    driver.find_element(By.XPATH, code_input_xpath).clear()
                    time.sleep(3)
                    try_num += 1
                    break

    driver.close()