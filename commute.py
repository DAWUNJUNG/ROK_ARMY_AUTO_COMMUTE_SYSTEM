import dotenv
from dotenv import find_dotenv, load_dotenv
import os
import platform
from selenium import webdriver
from seleniumwire import webdriver as wired_webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from datetime import datetime, timedelta
import requests
import json
import smtplib
from email.mime.text import MIMEText
import time


def check_device_os():
    system_os = platform.system()

    if system_os == "Windows":
        return "chromedriver-windows.exe"
    elif system_os == "Darwin":
        if platform.mac_ver()[2] == "arm64":
            return "./chromedriver-mac_arm"
        else:
            return "./chromedriver-mac_x86"


def get_annual_info():
    global log_message
    log_message = log_message + "KTbizmeka 휴가 정보 불러오기 시작 \n"

    options = {
        'https': 'proxy detail',
        'disable_encoding': True
    }

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument('lang=ko_KR')

    browser = wired_webdriver.Chrome(executable_path=check_device_os(), seleniumwire_options=options,
                                     chrome_options=chrome_options)

    # 비즈메카 열기
    browser.get('https://ezsso.bizmeka.com/loginForm.do')
    browser.implicitly_wait(100)

    # 인증 쿠키 유지설정
    browser.add_cookie({
        'name': os.environ.get('KT_BIZMEKA_COOKIE_NAME'),
        'value': os.environ.get('KT_BIZMEKA_COOKIE_VALUE')
    })

    # 비즈메카 로그인
    browser.find_element(By.ID, 'username').send_keys(os.environ.get('KT_BIZMEKA_ID'))
    browser.find_element(By.ID, 'password').send_keys(os.environ.get('KT_BIZMEKA_PW'))
    browser.find_element(By.ID, 'btnSubmit').click()

    # 비즈메카 휴가신청 이동
    browser.get('https://ezkhuman.bizmeka.com/product/outlnk.do?code=PA02')
    browser.implicitly_wait(100)

    request = browser.wait_for_request('.*/getApplVctnList.*', timeout=100)
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
                        key_date = datetime.strptime(diff_start_date, "%Y%m%d") + timedelta(days=(i + 1))
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
    browser.implicitly_wait(100)
    browser.quit()
    log_message = log_message + "KTbizmeka 휴가 정보 불러오기 종료 \n"


def work_time_check():
    global log_message
    log_message = log_message + "근무 시간 검증 시작\n"

    # 공휴일 파일 확인
    if os.path.isfile(os.environ.get('HOLIDAY_DIRECTORY') + datetime.now().strftime('%Y') + '.json'):
        # 공휴일 파일 불러오기
        with open(os.environ.get('HOLIDAY_DIRECTORY') + datetime.now().strftime('%Y') + '.json', 'r') as holiday_file:
            holidays_data = json.load(holiday_file)
    else:
        log_message = log_message + "공공 데이터 포털 공휴일 데이터 호출 시작\n"
        # 공공데이터포털에서 공휴일 가져오기
        today = datetime.today().strftime('%Y')
        url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=1000&solYear=' + str(
            today) + '&ServiceKey=' + str(os.environ.get('DATA_PORTAL_KEY'))
        response = requests.get(url)
        log_message = log_message + "공공 데이터 포털 공휴일 데이터 호출 완료\n"

        if response.status_code == 200:
            log_message = log_message + "공공 데이터 포털 공휴일 데이터 호출 성공\n"

            json_ob = json.loads(response.text)
            holidays_data = json_ob['response']['body']['items']['item']
            # 공휴일 파일 생성
            with open(os.environ.get('HOLIDAY_DIRECTORY') + datetime.now().strftime('%Y') + '.json', 'w') as holiday_file:
                json.dump(holidays_data, holiday_file)

    # 공휴일 데이터 가공
    log_message = log_message + "휴무일 데이터 가공 시작\n"
    for info in holidays_data:
        holiday_list[datetime.strptime(str(info['locdate']), '%Y%m%d').strftime('%Y-%m-%d')] = {
            "type": "full_day"
        }
    log_message = log_message + "휴무일 데이터 가공 종료\n"

    now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now_date = datetime.strptime(now_datetime, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    now_time = datetime.strptime(now_datetime, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
    if not now_date in holiday_list:
        log_message = log_message + "근무 타입 : 근무일\n"

        # 출퇴근시간 타입 구분
        go_work_time = datetime.now().strptime('10:00:00', '%H:%M:%S').strftime('%H:%M:%S')
        go_home_time = datetime.now().strptime('19:00:00', '%H:%M:%S').strftime('%H:%M:%S')

        if (now_time < go_work_time):
            return 'office'
        elif (now_time > go_home_time):
            return 'home'
    else:
        holiday_type = "연차"

        if holiday_list[now_date]['type'] == 'morning':
            holiday_type = "오전 반차"

            # 출퇴근시간 타입 구분
            go_work_time_first = datetime.now().strptime('14:40:00', '%H:%M:%S').strftime('%H:%M:%S')
            go_work_time_second = datetime.now().strptime('15:00:00', '%H:%M:%S').strftime('%H:%M:%S')
            go_home_time = datetime.now().strptime('19:00:00', '%H:%M:%S').strftime('%H:%M:%S')

            if now_time > go_work_time_first and now_time < go_work_time_second:
                return 'office'
            elif now_time > go_home_time:
                return 'home'
        elif holiday_list[now_date]['type'] == 'afternoon':
            holiday_type = "오후 반차"

            # 출퇴근시간 타입 구분
            go_work_time = datetime.now().strptime('10:00:00', '%H:%M:%S').strftime('%H:%M:%S')
            go_home_time = datetime.now().strptime('15:00:00', '%H:%M:%S').strftime('%H:%M:%S')

            if now_time < go_work_time:
                return 'office'
            elif now_time > go_home_time:
                return 'home'

        log_message = log_message + "근무 타입 : " + holiday_type + "\n"

    return 'no_commute'


def auto_commute():
    global log_message
    result_status = "fail"

    # 브라우저 설정
    options = {
        'https': 'proxy detail',
        'disable_encoding': True
    }

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument('lang=ko_KR')

    browser = wired_webdriver.Chrome(executable_path=check_device_os(), seleniumwire_options=options,
                                     chrome_options=chrome_options)

    # 비즈메카 열기
    browser.get('https://ezsso.bizmeka.com/loginForm.do')
    browser.implicitly_wait(100)

    # 인증 쿠키 유지설정
    browser.add_cookie({
        'name': os.environ.get('KT_BIZMEKA_COOKIE_NAME'),
        'value': os.environ.get('KT_BIZMEKA_COOKIE_VALUE')
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
    request = browser.wait_for_request('.*/getOnedayGolvwkMngPersList.*', timeout=100)
    request_data = json.loads(request.response.body.decode('utf-8'))
    if not request_data:
        log_message = log_message + "***근태 관리 접근 실패***\n"

    # 출퇴근 처리
    log_message = log_message + "근태 기록 시작\n"

    commute_type = work_time_check()
    log_message = log_message + "출퇴근 타입 : "
    if commute_type == 'office':
        log_message = log_message + "출근\n"
        browser.find_element(By.ID, 'btnGoOffice').click()
        alert = Alert(browser)
        alert_text = alert.text
        log_message = log_message + "출근 기록 메시지 : " + alert_text + "\n"
        if '하시겠습니까?' in alert_text:
            result_status = "출근 처리 완료"
        alert.accept()
        browser.implicitly_wait(100)
    elif commute_type == 'home':
        log_message = log_message + "퇴근\n"
        browser.find_element(By.ID, 'btnGoHome').click()
        alert = Alert(browser)
        alert_text = alert.text
        log_message = log_message + "퇴근 기록 메시지 : " + alert_text + "\n"
        if '하시겠습니까?' in alert_text:
            result_status = "퇴근 처리 완료"
        alert.accept()
        browser.implicitly_wait(100)

    log_message = log_message + "근태 기록 결과 : " + result_status + "\n"
    log_message = log_message + "근태 기록 종료\n"
    log_message = log_message + "프로세스 종료 시간 : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
    log_message = log_message + "근태 기록 자동화 종료\n\n\n\n\n"

    browser.implicitly_wait(100)
    browser.quit()


def log_mail_send(result_message):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()  # TLS 사용시 필요
    smtp.login(os.environ.get('GOOGLE_ID'), os.environ.get('GOOGLE_APP_PW'))

    msg = MIMEText(result_message)
    msg['Subject'] = '근태 자동화 도구 동작 결과 안내 (' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ')'
    smtp.sendmail(os.environ.get('SOURCE_EMAIL'), os.environ.get('DESTINATION_EMAIL'), msg.as_string())

    smtp.quit()


if __name__ == "__main__":
    global log_message
    log_message = ""

    ##환경변수 파일 호출
    load_dotenv()

    # 로그파일 오픈
    logfile = open(str(os.environ.get('LOG_DIRECTORY')) + datetime.now().strftime('%Y-%m-%d') + '.txt', 'a', encoding="UTF-8")
    log_message = log_message + "근태 기록 자동화 시작\n"
    log_message = log_message + "프로세스 시작 시간 : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
    log_message = log_message + "Made By Dawun (github : https://github.com/DAWUNJUNG)\n"

    # 휴무일 데이터 호출
    holiday_list = {}
    get_annual_info()

    # 출퇴근 기록 프로세스
    auto_commute()

    # 결과 로그 파일 생성
    logfile.write(log_message)
    logfile.close()

    # 결과 메일 발송 프로세스
    # log_mail_send(log_message)