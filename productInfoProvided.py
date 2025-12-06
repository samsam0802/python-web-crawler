from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_product_info_provided(driver, filename: str = None):
    """
    상품정보 제공고시 테이블을 가져오는 함수
    """
    try:
        wait = WebDriverWait(driver, 10)

        # 버튼 선택
        button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="tab-panels"]/section/ul/li[1]/button/span')
            )
        )

        # 화면에 보이도록 스크롤 후 클릭
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)

        # 테이블 선택
        table = driver.find_element(By.CSS_SELECTOR, "div.Accordion_content__aIya4 table.Accordion_table__mcFPq")

        # <tr> 단위로 데이터 추출
        rows = table.find_elements(By.TAG_NAME, "tr")
        product_info = {}

        for row in rows:
            try:
                key = row.find_element(By.TAG_NAME, "th").text.strip()
                value = row.find_element(By.TAG_NAME, "td").text.strip()
                product_info[key] = value
            except:
                continue

        print(f"상품정보 테이블 {len(product_info)}개 항목 수집 완료")

        # 파일 저장
        if filename and product_info:
            try:
                with open(filename, 'a', encoding='utf-8') as f:
                    # 상품 구분 줄 추가
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("상품정보 제공고시\n")
                    f.write("=" * 50 + "\n")
                    for i, (key, value) in enumerate(product_info.items(), start=1):
                        f.write(f"{i}. {key}: {value}\n")
                print(f"상품정보 테이블이 '{filename}'에 번호와 함께 저장되었습니다.")
            except Exception as e:
                print(f"상품정보 테이블 저장 중 오류 발생: {e}")

        return product_info if product_info else None

    except Exception as e:
        print("상품정보 테이블 가져오기 실패:", e)
        return None