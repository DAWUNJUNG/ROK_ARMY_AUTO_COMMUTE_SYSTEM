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

#### setup
```text
    1. cron이 설치된 경로에 프로젝트내에 ca.crt파일과 chromedriver.exe 파일을 복사해 두어야 합니다.
    2. crontab에 스케줄러를 입력 후 startcron.bat을 실행시켜 cron을 상시대기 상태로 변경합니다.
```

#### Windows crontab
```text
    40 9 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    40 14 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    1 14 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    1 19 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
```

## Requeired env setting value
```text
    KT_BIZMEKA_COOKIE_NAME="휴대전화 인증 후 발급된 쿠키 이름"
    KT_BIZMEKA_COOKIE_VALUE="휴대전화 인증 후 발급된 쿠키 값"
    KT_BIZMEKA_ID="비즈메카 아이디"
    KT_BIZMEKA_PW="비즈메카 비밀번호"
    KT_BIZMEKA_PW_CHANGE="비밀번호 변경 대처용 비밀번호"  //비밀번호 변경 시즌이 되면 KT_BIZMEKA_PW와 KT_BIZMEKA_PW_CHANGE가 변경되어 비밀번호를 변경합니다
    // 기능 활성화시 사용 가능
    GOOGLE_ID="구글 계정"
    GOOGLE_APP_PW="구글 앱 비밀번호"
    SOURCE_EMAIL="발신 EMAIL 주소"
    DESTINATION_EMAIL="수신 EMAIL 주소"
```

## GOOGLE APP PASSWORD
[도움말 링크](https://support.google.com/accounts/answer/185833?hl=ko)