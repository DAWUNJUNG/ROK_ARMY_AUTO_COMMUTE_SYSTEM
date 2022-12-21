# ROK_ARMY_AUTO_COMMUTE_SYSTEM
```text
    해당 프로젝트는 KT 비즈메카 시스템은 ERP로 사용하는 회사 대상으로 동작을 지원하는 자동 출퇴근 기록 프로그램입니다.
```

## Program Info
```text
    Support OS : Windows
                 MacOS
    
    Use Technology : 
            - Language :
                        Python 3.7 이상
            - Package :
                        dotenv
                        selenium
                        seleniumwire
                        datetime
                        requests
                        json
                        
            - Cron    : 
                        nncron (Windows)
                        crontab (MacOS)
```


## Project Setup
### KT BIZMEKA Phone Auth COOKIE SET
```text
    selenium-wire 사용을 위해 Bypass SSL 인증서를 모든 인증 방식에 등록해줘야합니다. 
    방법 URL : https://support.google.com/chrome/a/answer/3505249?hl=ko
```

### chrome SSL Set
```text
    selenium-wire 사용을 위해 Bypass SSL 인증서를 모든 인증 방식에 등록해줘야합니다. 
    방법 URL : https://support.google.com/chrome/a/answer/3505249?hl=ko
```

### Cron Scheduler

#### crontab
```text
    50 9 * * 1-5 python_DIR DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    50 14 * * 1-5 python_DIR DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    1 15 * * 1-5 python_DIR DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    1 19 * * 1-5 python_DIR DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
```

## Requeired env setting value
```text
    KT_BIZMEKA_COOKIE_NAME=휴대전화 인증 후 발급된 쿠키 이름
    KT_BIZMEKA_COOKIE_VALUE=휴대전화 인증 후 발급된 쿠키 값
    KT_BIZMEKA_ID=비즈메카 아이디
    KT_BIZMEKA_PW=비즈메카 비밀번호
    KT_BIZMEKA_PW_CHANGE=비밀번호 변경 대처용 비밀번호  //비밀번호 변경 시즌이 되면 KT_BIZMEKA_PW와 KT_BIZMEKA_PW_CHANGE가 변경되어 비밀번호를 변경합니다
    LOG_DIRECTORY=로그파일을 생성할 디렉토리
    HOLIDAY_DIRECTORY=공휴일 데이터 저장 디렉토리
    DATA_PORTAL_KEY=공공데이터포털 KEY
    // 기능 활성화시 사용 가능
    GOOGLE_ID=구글 계정
    GOOGLE_APP_PW=구글 앱 비밀번호
    SOURCE_EMAIL=발신 EMAIL 주소
    DESTINATION_EMAIL=수신 EMAIL 주소
```

## DATA PORTAL KEY Generate
[공공 데이터 포털 특일 정보 바로가기](https://www.data.go.kr/iim/api/selectAPIAcountView.do)
```text
    주의사항 : 2년에 한번씩 갱신 해줘야함
    1. 공공 데이터 포털 회원가입
    2. 공공 데이터 포털 특일 정보 페이지로 이동 (위 바로가기 클릭)
    3. 개발 계정 및 운영 계정 전환
    4. 일반 인증키 복사 및 env에 삽입
```

## GOOGLE APP PASSWORD
[도움말 링크](https://support.google.com/accounts/answer/185833?hl=ko)