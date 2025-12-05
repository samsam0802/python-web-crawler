from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


from imgCol import get_all_image_urls, save_urls_to_file

# 가장 간단한 버전
try:
    # 드라이버 생성
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # URL 설정
    url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=1000001000100130001&fltDispCatNo=&prdSort=01&pageIdx=1&rowsPerPage=24&searchTypeSort=btn_thumb&plusButtonFlag=N&isLoginCnt=0&aShowCnt=0&bShowCnt=0&cShowCnt=0&trackingCd=Cat1000001000100130001_Small&amplitudePageGubun=&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EC%83%81%EC%84%B8_%EC%86%8C%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC&midCategory=%EC%8A%A4%ED%82%A8%2F%ED%86%A0%EB%84%88&smallCategory=%EC%A0%84%EC%B2%B4&checkBrnds=&lastChkBrnd=&t_1st_category_type=%EB%8C%80_%EC%8A%A4%ED%82%A8%EC%BC%80%EC%96%B4&t_2nd_category_type=%EC%A4%91_%EC%8A%A4%ED%82%A8%2F%ED%86%A0%EB%84%88&t_3rd_category_type=%EC%86%8C_%EC%8A%A4%ED%82%A8%2F%ED%86%A0%EB%84%88"

    # 페이지 접속
    driver.get(url)
    time.sleep(3)

    # XPATH 요소 클릭
    element = driver.find_element(By.XPATH, "//*[@id='Contents']/ul[2]/li[3]")
    element.click()
    time.sleep(3)

    ### 상품 데이터 수집 ###

    # 여기에서 get_all_image_urls 호출
    # image_urls = get_main_image_urls(driver)
    # 2. 상세 페이지에서 get_all_image_urls 호출
    print("이미지 수집 함수 호출...")
    image_urls = get_all_image_urls(driver)
    save_urls_to_file(image_urls);

    # 함수 기본정보(카테고리, 브랜드, 이름) 가져오는 함수 호출 - 병국
    # 상품 메인 이미지 url 가져오는 함수 호출 - 병국
    # 상품 디테일 이미지 url 가져오는 함수 호출 -소라
    # 상품 상세 정보 제공고시 데이터 가져오는 함수 호출 - 소라
    # 상품 옵션 정보(옵션이미지, 옵션명, 옵션가격) 가져오는 함수 호출 - 민석

    # INSERT 문 만들어주는 함수 호출 (a,b,c,d,e)

    ### 수집 후 INSERT 문 작성 insertQuery.txt 텍스트를 추가하는 방식으로 하면 되겠죠

    #######

    # 뒤로가기
    driver.back()
    time.sleep(2)

    # 종료
    driver.quit()
    print("성공적으로 실행 완료!")

except Exception as e:
    print(f"에러 발생: {e}")