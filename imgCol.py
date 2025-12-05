# imgCol.py (수정 버전 - src 속성 사용 + 정렬 기능)

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time
from typing import List
import re

# 이미지 요소를 찾는 XPath
MAIN_IMAGE_XPATH = '//*[@id="main"]/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div/img'
# 다음 이미지를 보는 버튼의 XPath
NEXT_BUTTON_XPATH = '//*[@id="main"]/div[2]/div/div[1]/div/div/div/div[3]'


def clean_image_url(url: str) -> str:
    """
    이미지 URL에서 불필요한 쿼리 파라미터를 제거합니다.
    예: &QT=85&SF=webp&sharpen=1x0.5 제거

    :param url: 원본 URL
    :return: 정제된 URL
    """
    if not url:
        return url

    # &QT, &SF, &sharpen 등의 파라미터 제거
    # ?l=ko는 유지하고 나머지 제거
    cleaned = re.sub(r'&(QT|SF|sharpen)=[^&]*', '', url)
    return cleaned


def extract_image_number(url: str) -> int:
    """
    이미지 URL에서 순서를 나타내는 숫자를 추출합니다.
    예: A00000023878203ko.jpg -> 203

    :param url: 이미지 URL
    :return: 추출된 숫자 (추출 실패 시 999999 반환)
    """
    try:
        # A로 시작하는 부분에서 마지막 2-3자리 숫자 추출
        # 예: A00000023878203ko.jpg에서 203 추출
        match = re.search(r'A\d+?(\d{2,3})ko\.jpg', url)
        if match:
            number = int(match.group(1))
            print(f"  -> 추출된 순서 번호: {number}")
            return number
    except Exception as e:
        print(f"  -> 숫자 추출 실패: {e}")

    return 999999  # 추출 실패 시 큰 숫자 반환 (정렬 시 뒤로 보냄)


def get_all_image_urls(driver: WebDriver, max_images: int = 10) -> List[str]:
    """
    현재 상세 페이지에 진입하여 메인 이미지 슬라이더의 모든 이미지 URL을 수집합니다.

    :param driver: Selenium WebDriver 객체
    :param max_images: 최대 수집 이미지 개수 (무한루프 방지)
    :return: 수집된 이미지 URL 문자열 리스트 (순서대로 정렬됨)
    """
    image_urls = set()  # 수집된 URL 저장 및 중복 확인을 위한 set
    consecutive_duplicates = 0  # 연속 중복 카운터
    max_consecutive_duplicates = 3  # 연속 중복 허용 횟수

    # 상세 페이지 로딩 대기
    time.sleep(3)
    print("이미지 URL 수집 시작...")

    while len(image_urls) < max_images:
        try:
            # 1. 현재 보이는 메인 이미지 요소 찾기
            image_element = driver.find_element(By.XPATH, MAIN_IMAGE_XPATH)

            # 2. 이미지 URL 가져오기 (src 속성 사용)
            img_src = image_element.get_attribute('src')

            # 3. URL 정제 (쿼리 파라미터 제거)
            if img_src and img_src.startswith('http'):
                cleaned_url = clean_image_url(img_src)

                # 수집된 URL이 이미 set에 있는지 확인
                if cleaned_url in image_urls:
                    consecutive_duplicates += 1
                    print(f"중복된 URL 발견 ({consecutive_duplicates}번째)")

                    # 연속으로 3번 중복되면 모든 이미지를 순환했다고 판단
                    if consecutive_duplicates >= max_consecutive_duplicates:
                        print("모든 이미지 순환 완료.")
                        break
                else:
                    # 새로운 URL 발견
                    consecutive_duplicates = 0  # 중복 카운터 리셋
                    image_urls.add(cleaned_url)
                    print(f"URL 수집 ({len(image_urls)}개):")
                    print(f"  {cleaned_url}")

            # 4. 다음 이미지 버튼 클릭
            try:
                next_button = driver.find_element(By.XPATH, NEXT_BUTTON_XPATH)

                # JavaScript를 사용하여 강제 클릭
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(0.8)  # 이미지 로딩 대기

            except NoSuchElementException:
                print("다음 버튼을 찾을 수 없습니다. 수집 종료.")
                break

        except StaleElementReferenceException:
            # 요소가 새로고침되어 발생하는 오류는 무시하고 다시 시도
            print("요소 참조 오류 발생. 재시도합니다.")
            time.sleep(1)
            continue

        except Exception as e:
            # 다른 종류의 오류 발생 시 루프 종료
            print(f"예상치 못한 에러 발생. 수집 종료. (에러: {type(e).__name__}: {str(e)})")
            break

    print(f"총 {len(image_urls)}개의 이미지 URL 수집 완료.")

    # URL을 순서대로 정렬
    print("\n이미지 URL 정렬 중...")
    sorted_urls = sorted(list(image_urls), key=extract_image_number)
    print("이미지 URL 정렬 완료.\n")

    return sorted_urls


def save_urls_to_file(urls: List[str], filename: str = "urls.txt"):
    """
    수집된 URL 리스트를 지정된 파일에 저장합니다.
    """
    if not urls:
        print("저장할 URL이 없습니다.")
        return

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for i, url in enumerate(urls, 1):
                # 각 URL의 순서 번호도 함께 출력
                order_num = extract_image_number(url)
                f.write(f"{i}. [순서:{order_num}] {url}\n")
        print(f"성공적으로 {len(urls)}개의 URL을 '{filename}'에 저장했습니다.")
    except Exception as e:
        print(f"파일 저장 중 에러 발생: {e}")


# 사용 예시
if __name__ == "__main__":
    from selenium import webdriver

    # 드라이버 설정 (예시)
    driver = webdriver.Chrome()

    try:
        # 상품 페이지로 이동 (예시 URL)
        driver.get("https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000238782")

        # 이미지 URL 수집
        urls = get_all_image_urls(driver)

        # 파일로 저장
        save_urls_to_file(urls, "oliveyoung_images.txt")

        # 콘솔에도 최종 결과 출력
        print("\n=== 최종 정렬된 URL 목록 ===")
        for i, url in enumerate(urls, 1):
            order_num = extract_image_number(url)
            print(f"{i}. [순서:{order_num}] {url}")

    finally:
        driver.quit()