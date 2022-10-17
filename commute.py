import dotenv
from dotenv import find_dotenv, load_dotenv
import os
from selenium import webdriver
from seleniumwire import webdriver as wired_webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from datetime import datetime, timedelta
import requests
import json


def get_annual_info():
    logfile.write("check vacation from KTbizmeka start \n")

    options = {
        'https': 'proxy detail',
        'disable_encoding': True
    }

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument('lang=ko_KR')

    browser = wired_webdriver.Chrome(executable_path='chromedriver.exe', seleniumwire_options=options, chrome_options=chrome_options)

    # 비즈메카 열기
    browser.get('https://ezsso.bizmeka.com/loginForm.do')
    browser.implicitly_wait(10)

    # 인증 쿠키 유지설정
    browser.add_cookie({
        'name': 'r4GK9DFq2vD7ofRPRoGdlh0Mi2nrl1EBkGALB2jwU',
        'value': 'q7zHr6MQZOhvtt+sK8QEHEodcbVYdgD5xuRIwHRYyyzjZjJscHj22JxxSsV1FcFU'
    })

    # 비즈메카 로그인
    browser.find_element(By.ID, 'username').send_keys(os.environ.get('KT_BIZMEKA_ID'))
    browser.find_element(By.ID, 'password').send_keys(os.environ.get('KT_BIZMEKA_PW'))
    browser.find_element(By.ID, 'btnSubmit').click()

    # 비즈메카 휴가신청 이동
    browser.get('https://ezkhuman.bizmeka.com/product/outlnk.do?code=PA02')
    browser.implicitly_wait(10)

    request = browser.wait_for_request('.*/getApplVctnList.*')
    request_data = json.loads(request.response.body.decode('utf-8'))

    not_approval_list = ["3", "4", "5", "6"]
    for data in request_data['list']:
        if not data['vctnAprvSt'] in not_approval_list:
            start_date = datetime.strptime(str(data['vctnFrDt']), '%Y.%m.%d').strftime('%Y-%m-%d')
            end_date = datetime.strptime(str(data['vctnToDt']), '%Y.%m.%d').strftime('%Y-%m-%d')

            diff_start_date = datetime.strptime(str(data['vctnFrDt']), '%Y.%m.%d').strftime('%Y%m%d')
            diff_end_date = datetime.strptime(str(data['vctnToDt']), '%Y.%m.%d').strftime('%Y%m%d')
            diff_date = datetime.strptime(diff_end_date, "%Y%m%d") - datetime.strptime(diff_start_date, "%Y%m%d")
            diff_day = diff_date.days

            if "전일" in data['oneHalfGbn']:
                if start_date != end_date:
                    for i in range(diff_day):
                        key_date = datetime.strptime(diff_start_date, "%Y%m%d") + timedelta(days=(i+1))
                        holiday_list[datetime.strptime(str(key_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')] = {
                            "type": "full_day"
                        }
                else:
                    holiday_list[end_date] = {
                        "type": "full_day"
                    }
            elif "오전" in data['oneHalfGbn']:
                holiday_list[end_date] = {
                    "type": "morning"
                }
            elif "오후" in data['oneHalfGbn']:
                holiday_list[end_date] = {
                    "type": "afternoon"
                }

    browser.quit()
    logfile.write("check vacation from KTbizmeka end \n")

def work_time_check():
    logfile.write("work time check start\n")

    logfile.write("get ROK holiday from CommonDataPortal start\n")
    # 공공데이터포털에서 공휴일 가져오기
    today = datetime.today().strftime('%Y')
    key = '7K8B2%2FjwUiPJygVIZ9ZUzlnsl%2BYxxv230EFP2s5MbrvsVE4Ua5OcUqe4jHzh78Royi8hrFCw39pAVI%2Bdlf1Yaw%3D%3D'
    url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=1000&solYear=' + str(
        today) + '&ServiceKey=' + str(key)
    response = requests.get(url)
    logfile.write("get ROK holiday from CommonDataPortal end\n")

    if response.status_code == 200:
        logfile.write("get ROK holiday from CommonDataPortal success\n")

        logfile.write("ROK holiday data processing start\n")
        json_ob = json.loads(response.text)
        holidays_data = json_ob['response']['body']['items']['item']
        for info in holidays_data:
            holiday_list[datetime.strptime(str(info['locdate']), '%Y%m%d').strftime('%Y-%m-%d')] = {
                "type": "full_day"
            }
        logfile.write("ROK holiday data processing end\n")

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now_date = datetime.strptime(now_datetime, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        now_time = datetime.strptime(now_datetime, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
        if not now_date in holiday_list:
            logfile.write("holiday type : no holiday\n")

            # 출퇴근시간 타입 구분
            go_work_time = datetime.now().strptime('10:00:00', '%H:%M:%S').strftime('%H:%M:%S')
            go_home_time = datetime.now().strptime('19:00:00', '%H:%M:%S').strftime('%H:%M:%S')

            if (now_time < go_work_time):
                return 'office'
            elif (now_time > go_home_time):
                return 'home'
        else:
            holiday_type = "full_day"

            if holiday_list[now_date]['type'] == 'morning':
                holiday_type = "morning"

                # 출퇴근시간 타입 구분
                go_work_time_first = datetime.now().strptime('14:40:00', '%H:%M:%S').strftime('%H:%M:%S')
                go_work_time_second = datetime.now().strptime('15:00:00', '%H:%M:%S').strftime('%H:%M:%S')
                go_home_time = datetime.now().strptime('19:00:00', '%H:%M:%S').strftime('%H:%M:%S')

                if now_time > go_work_time_first and now_time < go_work_time_second:
                    return 'office'
                elif now_time > go_home_time:
                    return 'home'
            elif holiday_list[now_date]['type'] == 'afternoon':
                holiday_type = "afternoon"

                # 출퇴근시간 타입 구분
                go_work_time = datetime.now().strptime('10:00:00', '%H:%M:%S').strftime('%H:%M:%S')
                go_home_time = datetime.now().strptime('14:00:00', '%H:%M:%S').strftime('%H:%M:%S')

                if now_time < go_work_time:
                    return 'office'
                elif now_time > go_home_time:
                    return 'home'

            logfile.write("holiday type : " + holiday_type + "\n")

    return 'no_commute'


def auto_commute():
    result_status = "fail"

    # 브라우저 설정
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument('lang=ko_KR')

    browser = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=chrome_options)

    # 비즈메카 열기
    browser.get('https://ezsso.bizmeka.com/loginForm.do')
    browser.implicitly_wait(10)

    # 인증 쿠키 유지설정
    browser.add_cookie({
        'name': 'r4GK9DFq2vD7ofRPRoGdlh0Mi2nrl1EBkGALB2jwU',
        'value': 'q7zHr6MQZOhvtt+sK8QEHEodcbVYdgD5xuRIwHRYyyzjZjJscHj22JxxSsV1FcFU'
    })

    # 비즈메카 로그인
    browser.find_element(By.ID, 'username').send_keys(os.environ.get('KT_BIZMEKA_ID'))
    browser.find_element(By.ID, 'password').send_keys(os.environ.get('KT_BIZMEKA_PW'))
    browser.find_element(By.ID, 'btnSubmit').click()

    if browser.current_url == "https://ezsso.bizmeka.com/rule/updatePasswordView.do":
        browser.find_element(By.ID, 'passwordOld').send_keys(os.environ.get('KT_BIZMEKA_PW'))
        browser.find_element(By.ID, 'password').send_keys(os.environ.get('KT_BIZMEKA_PW_CHANGE'))
        browser.find_element(By.ID, 'passwordAgain').send_keys(os.environ.get('KT_BIZMEKA_PW_CHANGE'))
        browser.find_element(By.ID, 'submitBtn').click()
        old_pw = os.environ.get('KT_BIZMEKA_PW')
        dotenv.set_key(find_dotenv(), "KT_BIZMEKA_PW", os.environ.get('KT_BIZMEKA_PW_CHANGE'))
        dotenv.set_key(find_dotenv(), "KT_BIZMEKA_PW_CHANGE", old_pw)

    # 비즈메카 근태관리 이동
    browser.get('https://ezkhuman.bizmeka.com/product/outlnk.do?code=PJ02')
    WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.ID, 'onedayGolvwkMngPersView')))

    # 출퇴근 처리
    logfile.write("commute processing start\n")

    commute_type = work_time_check()
    logfile.write("commute type : " + commute_type + "\n")
    if commute_type == 'office':
        browser.find_element(By.ID, 'btnGoOffice').click()
        alert = Alert(browser)
        alert_text = alert.text
        logfile.write("result alert content : " + alert_text + "\n")
        if '하시겠습니까?' in alert_text:
            result_status = "office success"
        alert.accept()
    elif commute_type == 'home':
        browser.find_element(By.ID, 'btnGoHome').click()
        alert = Alert(browser)
        alert_text = alert.text
        logfile.write("result alert content : " + alert_text + "\n")
        if '하시겠습니까?' in alert_text:
            result_status = "home success"
        alert.accept()

    logfile.write("commute processing result status : " + result_status + "\n")
    logfile.write("commute processing end\n")
    logfile.write("service end (" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ")\n\n\n\n\n")
    logfile.close()

    # 디버그용
    # while (True):
    #     pass

    browser.quit()


if __name__ == "__main__":
    ##환경변수 파일 호출
    load_dotenv()

    # 로그파일 오픈
    logfile = open('C:\\ROK_ARMY_AUTO_COMMUTE_SYSTEM\log\\' + datetime.now().strftime('%Y-%m-%d') + '.txt', 'a', encoding="UTF-8")
    logfile.write("service start (" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ") \n")

    # 휴무일 데이터 호출
    holiday_list = {}
    get_annual_info()

    # 출퇴근 기록 프로세스
    auto_commute()