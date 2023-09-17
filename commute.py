import dotenv
from dotenv import find_dotenv, load_dotenv
import os
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from datetime import datetime, timedelta
import requests
import json
import smtplib
from email.mime.text import MIMEText
import traceback
import chromedriver_autoinstaller

class AutoCommute:

    def __init__(self):
        # 로그 메시지 초기 선언
        self.log_message = ''

        # 휴무일 데이터 초기화
        self.holiday_list = {}

        # 환경 변수 파일 호출
        load_dotenv()

        # 브라우저 네트워크 통신 설정
        self.options = {
            'https': 'proxy detail',
            'disable_encoding': True
        }

        # 크로미움 설정
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument("--remote-debugging-port=9222")
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-popup-blocking')
        self.chrome_options.add_argument("--incognito")
        self.chrome_options.add_argument('ignore-certificate-errors')  # SSL 관련 오류 무시
        self.chrome_options.add_argument('ignore-ssl-errors')  # SSL 관련 오류 무시
        self.chrome_options.add_experimental_option("detach", True)

        # 로그 파일 선언
        log_dir = str(os.environ.get('LOG_DIRECTORY')) + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.logfile = open(log_dir + '/' + datetime.now().strftime('%Y-%m-%d') + '.txt', 'a',
                            encoding="UTF-8")

        # 크롬 설치
        chromedriver_autoinstaller.install()

        # 설정 정보 할당
        self.browser = webdriver.Chrome(seleniumwire_options=self.options, options=self.chrome_options)
        self.log("근태 기록 자동화 시작\n" +
                 f"프로세스 시작 시간 : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" +
                 "Made By Dawun (github : https://github.com/DAWUNJUNG)\n")

    def bizmeka_login(self):
        try:
            self.log("KTbizmeka 휴가 정보 불러오기 시작 \n")
            # 비즈메카 열기
            self.browser.get('https://ezsso.bizmeka.com/loginForm.do')
            self.browser.implicitly_wait(100)

            # 인증 쿠키 유지설정
            self.browser.add_cookie({
                'name': os.environ.get('KT_BIZMEKA_COOKIE_NAME'),
                'value': os.environ.get('KT_BIZMEKA_COOKIE_VALUE'),
                'domain': 'ezsso.bizmeka.com'
            })

            # 비즈메카 로그인
            self.browser.find_element(By.ID, 'username').send_keys(os.environ.get('KT_BIZMEKA_ID'))
            self.browser.find_element(By.ID, 'password').send_keys(os.environ.get('KT_BIZMEKA_PW'))
            self.browser.find_element(By.ID, 'btnSubmit').click()
            self.browser.implicitly_wait(100)

            # 비밀번호 변경 페이지 이동시 비밀번호 변경
            if self.browser.current_url == "https://ezsso.bizmeka.com/rule/updatePasswordView.do":
                self.log("정기 비밀번호 변경 시작 \n")
                self.browser.find_element(By.ID, 'passwordOld').send_keys(os.environ.get('KT_BIZMEKA_PW'))
                self.browser.find_element(By.ID, 'password').send_keys(os.environ.get('KT_BIZMEKA_PW_CHANGE'))
                self.browser.find_element(By.ID, 'passwordAgain').send_keys(os.environ.get('KT_BIZMEKA_PW_CHANGE'))
                self.browser.find_element(By.ID, 'submitBtn').click()
                alert = Alert(self.browser)
                alert.accept()
                self.log("정기 비밀번호 변경 완료 \n")
                old_pw = os.environ.get('KT_BIZMEKA_PW')
                dotenv.set_key(find_dotenv(), "KT_BIZMEKA_PW", os.environ.get('KT_BIZMEKA_PW_CHANGE'))
                dotenv.set_key(find_dotenv(), "KT_BIZMEKA_PW_CHANGE", old_pw)
                self.log("이전 비밀번호와 변경 대상 비밀번호 env 수정 완료 \n")
                self.browser.implicitly_wait(100)
        except Exception as e:
            self.log("\n=============================\n")
            self.log("bizmeka_login 동작 중 오류\n")
            self.log(f"오류 메시지 : {str(e)}\n")
            self.log(f"traceback : {traceback.format_exc()}\n")
            self.log("=============================\n\n\n\n\n")

    def get_annual_info(self):
        try:
            # 비즈메카 휴가신청 이동
            self.browser.get('https://ezkhuman.bizmeka.com/product/outlnk.do?code=PA02')
            self.browser.implicitly_wait(100)

            request = self.browser.wait_for_request('.*/getApplVctnList.*', timeout=100)
            request_data = json.loads(request.response.body.decode('utf-8'))

            not_approval_list = ["3", "4", "5", "6"]
            for data in request_data['list']:
                if not data['vctnAprvSt'] in not_approval_list:
                    start_date = datetime.strptime(str(data['vctnFrDt']), '%Y.%m.%d').strftime('%Y-%m-%d')
                    end_date = datetime.strptime(str(data['vctnToDt']), '%Y.%m.%d').strftime('%Y-%m-%d')

                    if "전일" in data['oneHalfGbn']:
                        if start_date != end_date:
                            diff_start_date = datetime.strptime(str(data['vctnFrDt']), '%Y.%m.%d').strftime('%Y%m%d')
                            diff_end_date = datetime.strptime(str(data['vctnToDt']), '%Y.%m.%d').strftime('%Y%m%d')
                            diff_date = datetime.strptime(diff_end_date, "%Y%m%d") - datetime.strptime(diff_start_date,
                                                                                                       "%Y%m%d")

                            for i in range(diff_date.days + 1):
                                key_date = datetime.strptime(diff_start_date, "%Y%m%d") + timedelta(days=(+ i))
                                self.holiday_list[
                                    datetime.strptime(str(key_date), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')] = {
                                    "type": "full_day"
                                }
                        else:
                            self.holiday_list[end_date] = {
                                "type": "full_day"
                            }
                    elif "오전" in data['oneHalfGbn']:
                        self.holiday_list[end_date] = {
                            "type": "morning"
                        }
                    elif "오후" in data['oneHalfGbn']:
                        self.holiday_list[end_date] = {
                            "type": "afternoon"
                        }
            self.browser.implicitly_wait(100)
            self.log("KTbizmeka 휴가 정보 불러오기 종료 \n")
        except Exception as e:
            self.log("\n=============================\n")
            self.log("get_annual_info 동작 중 오류\n")
            self.log(f"오류 메시지 : {str(e)}\n")
            self.log(f"traceback : {traceback.format_exc()}\n")
            self.log("=============================\n\n\n\n\n")

    def common_data_portal(self):
        try:
            # 공휴일 파일 확인
            if not os.path.exists(os.environ.get('HOLIDAY_DIRECTORY')):
                os.makedirs(os.environ.get('HOLIDAY_DIRECTORY'))
            if os.path.isfile(os.environ.get('HOLIDAY_DIRECTORY') + datetime.now().strftime('%Y') + '.json'):
                # 공휴일 파일 불러오기
                with open(os.environ.get('HOLIDAY_DIRECTORY') + datetime.now().strftime('%Y') + '.json',
                          'r') as holiday_file:
                    holidays_data = json.load(holiday_file)
            else:
                self.log("공공 데이터 포털 공휴일 데이터 호출 시작\n")
                # 공공데이터포털에서 공휴일 가져오기
                today = datetime.today().strftime('%Y')
                url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?_type=json&numOfRows=1000&solYear=' + str(
                    today) + '&ServiceKey=' + str(os.environ.get('DATA_PORTAL_KEY'))
                response = requests.get(url)
                self.log("공공 데이터 포털 공휴일 데이터 호출 완료\n")

                if response.status_code == 200:
                    self.log("공공 데이터 포털 공휴일 데이터 호출 성공\n")

                    json_ob = json.loads(response.text)
                    holidays_data = json_ob['response']['body']['items']['item']
                    # 공휴일 파일 생성
                    with open(os.environ.get('HOLIDAY_DIRECTORY') + datetime.now().strftime('%Y') + '.json',
                              'w') as holiday_file:
                        json.dump(holidays_data, holiday_file)

            # 공휴일 데이터 가공
            self.log("휴무일 데이터 가공 시작\n")
            for info in holidays_data:
                self.holiday_list[datetime.strptime(str(info['locdate']), '%Y%m%d').strftime('%Y-%m-%d')] = {
                    "type": "full_day"
                }
            self.log("휴무일 데이터 가공 종료\n")
        except Exception as e:
            self.log("\n=============================\n")
            self.log("common_data_portal 동작 중 오류\n")
            self.log(f"오류 메시지 : {str(e)}\n")
            self.log(f"traceback : {traceback.format_exc()}\n")
            self.log("=============================\n\n\n\n\n")

    def work_time_check(self, end_work_time):
        try:
            self.log("근무 시간 검증 시작\n")

            now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            now_date = datetime.strptime(now_datetime, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            now_time = datetime.strptime(now_datetime, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
            if not now_date in self.holiday_list:
                self.log("근무 타입 : 근무일\n")

                # 출퇴근시간 타입 구분
                go_work_time = datetime.now().strptime('10:00:00', '%H:%M:%S').strftime('%H:%M:%S')
                go_home_time = datetime.now().strptime('19:00:00', '%H:%M:%S').strftime('%H:%M:%S')

                if end_work_time == '':
                    if now_time < go_work_time:
                        return 'office'
                    elif now_time > go_home_time:
                        return 'home'
            else:
                if self.holiday_list[now_date]['type'] == 'morning':
                    self.log("근무 타입 : 오전 반차\n")

                    # 출퇴근시간 타입 구분
                    go_work_time_first = datetime.now().strptime('14:40:00', '%H:%M:%S').strftime('%H:%M:%S')
                    go_work_time_second = datetime.now().strptime('15:00:00', '%H:%M:%S').strftime('%H:%M:%S')
                    go_home_time = datetime.now().strptime('19:00:00', '%H:%M:%S').strftime('%H:%M:%S')

                    if end_work_time == '':
                        if go_work_time_first < now_time < go_work_time_second:
                            return 'office'
                        elif now_time > go_home_time:
                            return 'home'
                elif self.holiday_list[now_date]['type'] == 'afternoon':
                    self.log("근무 타입 : 오후 반차\n")

                    # 출퇴근시간 타입 구분
                    go_work_time = datetime.now().strptime('10:00:00', '%H:%M:%S').strftime('%H:%M:%S')
                    go_home_time = datetime.now().strptime('15:00:00', '%H:%M:%S').strftime('%H:%M:%S')
                    go_home_time_second = datetime.now().strptime('16:00:00', '%H:%M:%S').strftime('%H:%M:%S')

                    if end_work_time == '':
                        if now_time < go_work_time:
                            return 'office'
                        elif go_home_time_second > now_time > go_home_time:
                            return 'home'
                else:
                    self.log("근무 타입 : 연차\n")

            return 'no_commute'
        except Exception as e:
            self.log("\n=============================\n")
            self.log("work_time_check 동작 중 오류\n")
            self.log(f"오류 메시지 : {str(e)}\n")
            self.log(f"traceback : {traceback.format_exc()}\n")
            self.log("=============================\n\n\n\n\n")
            return 'no_commute';

    def auto_commute(self):
        try:
            result_status = "fail"

            # 비즈메카 근태관리 이동
            self.browser.get('https://ezkhuman.bizmeka.com/product/outlnk.do?code=PJ02')
            request = self.browser.wait_for_request('.*/getOnedayGolvwkMngPersList.*', timeout=100)
            request_data = json.loads(request.response.body.decode('utf-8'))
            if not request_data:
                self.log("***근태 관리 접근 실패***\n")

            end_work_time = request_data['result']['entity'][0]['workTimeTo']

            # 출퇴근 처리
            self.log("근태 기록 시작\n")

            # 근무 시간 체크
            commute_type = self.work_time_check(end_work_time)
            self.log("출퇴근 타입 : ")
            if commute_type == 'office':
                self.log("출근\n")
                self.browser.find_element(By.ID, 'btnGoOffice').click()
                alert = Alert(self.browser)
                alert_text = alert.text
                self.log(f"출근 기록 메시지 : {alert_text}\n")
                if '하시겠습니까?' in alert_text:
                    result_status = "출근 처리 완료"
                alert.accept()
                self.browser.implicitly_wait(100)
            elif commute_type == 'home':
                self.log("퇴근\n")
                self.browser.find_element(By.ID, 'btnGoHome').click()
                alert = Alert(self.browser)
                alert_text = alert.text
                self.log(f"퇴근 기록 메시지 : {alert_text}\n")
                if '하시겠습니까?' in alert_text:
                    result_status = "퇴근 처리 완료"
                alert.accept()
                self.browser.implicitly_wait(100)

            self.log(f"근태 기록 결과 : {result_status}\n")
            self.log("근태 기록 종료\n")
        except Exception as e:
            self.log("\n=============================\n")
            self.log("auto_commute 동작 중 오류\n")
            self.log(f"오류 메시지 : {str(e)}\n")
            self.log(f"traceback : {traceback.format_exc()}\n")
            self.log("=============================\n\n\n\n\n")

    # 로그 작성 function
    def log(self, message):
        # 로그파일 작성
        self.logfile.write(message)
        self.log_message = self.log_message + message

    # 메일 발송 function
    def mail_send(self):
        try:
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.ehlo()
            smtp.starttls()  # TLS 사용시 필요
            smtp.login(os.environ.get('GOOGLE_ID'), os.environ.get('GOOGLE_APP_PW'))

            msg = MIMEText(self.log_message)
            msg['To'] = os.environ.get('DESTINATION_EMAIL')
            msg['From'] = os.environ.get('SOURCE_EMAIL')
            msg['Subject'] = '근태 자동화 도구 동작 결과 안내 (' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ')'
            smtp.sendmail(os.environ.get('SOURCE_EMAIL'), os.environ.get('DESTINATION_EMAIL'), msg.as_string())

            smtp.quit()
        except Exception as e:
            self.log("\n=============================\n")
            self.log("mail_send 동작 중 오류\n")
            self.log(f"오류 메시지 : {str(e)}\n")
            self.log(f"traceback : {traceback.format_exc()}\n")
            self.log("=============================\n\n\n\n\n")

    def __del__(self):
        # 크로미움 종료
        self.browser.quit()

        self.log(f"프로세스 종료 시간 : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.log("근태 기록 자동화 종료\n\n\n\n\n")

        # 로그 파일 작성 종료
        self.logfile.close()


if __name__ == "__main__":
    auto_commute = AutoCommute()

    # 공공 데이터 포털 휴무일 정보 호출
    auto_commute.common_data_portal()

    # 비즈메카 로그인
    auto_commute.bizmeka_login()

    # 휴무일 데이터 호출
    auto_commute.get_annual_info()

    # 출퇴근 기록
    auto_commute.auto_commute()

    # 메일 발송
    if os.environ.get('LOG_EMAIL_SEND') == 'Y':
        auto_commute.mail_send()

    del auto_commute
