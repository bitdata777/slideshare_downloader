shlideshare의 html을 파싱, 각 슬라이드(jpg)를 다운받아 PDF로 병합하여 slideshare의 제목으로 저장.


### 사용법

- 첫번째 인자는 slideshare의 url 또는 url을 기록한 파일

  e.x) python slideshare_downloader.py [http://slideshare.net/~] | [list.txt]

- 두번째 인자는 TheadPool의 사이즈값. 값이 없을 경우 기본 5 사용.




### 버그

- request.get이 대량의 slide를 읽다보면 pool관련 사이즈 에러 발생.



### 할일

코드 정리 필요
