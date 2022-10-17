# ROK_ARMY_AUTO_COMMUTE_SYSTEM

## Program Info
```text
    Support OS : Windows
                 Unix(지원예정)
    
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
                        nncron
```


## Project Setup
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
    50 9 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    50 14 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    1 14 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
    1 19 * * 1-5  DIR\ROK_ARMY_AUTO_COMMUTE_SYSTEM\commute.py
```


## Requeired env setting value
```text
    KT_BIZMEKA_ID="비즈메카 아이디"
    KT_BIZMEKA_PW="비즈메카 비밀번호"
    KT_BIZMEKA_PW_CHANGE="비밀번호 변경 대처용 비밀번호"  //비밀번호 변경 시즌이 되면 KT_BIZMEKA_PW와 KT_BIZMEKA_PW_CHANGE가 변경되어 비밀번호를 변경합니다
```
