from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_detail_image_urls(driver, product_id: int, filename: str = None):
    """
    상품 상세 이미지 가져오는 함수
    """
    try:
        wait = WebDriverWait(driver, 10)

        # "상품설명 더보기" 버튼 클릭
        try:
            more_button = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.GoodsDetailTabs_btn-more__zrJGJ")
                )
            )
            more_button.click()
            time.sleep(1)
        except:
            print("더보기 버튼 없음")

        # 페이지 조금씩 스크롤하며 이미지 로딩 대기
        SCROLL_PAUSE = 0.5
        last_height = driver.execute_script("return document.body.scrollHeight")
        current_pos = 0

        while current_pos < last_height:
            driver.execute_script(f"window.scrollTo(0, {current_pos});")
            time.sleep(SCROLL_PAUSE)
            current_pos += 500  # 500px씩 스크롤
            last_height = driver.execute_script("return document.body.scrollHeight")

        # 이미지 URL 수집
        imgs = driver.find_elements(By.CSS_SELECTOR, ".speedycat-container img")
        detail_urls = []
        for img in imgs:
            for attr in ["data-src", "data-original", "src"]:
                url = img.get_attribute(attr)
                if url and not url.startswith("data:image"):
                    detail_urls.append(url)
                    break

        print(f"상세 이미지 {len(detail_urls)}개 수집 완료")

        # INSERT문 생성
        if detail_urls:
            sql_lines = []
            for idx, url in enumerate(detail_urls):
                sql_lines.append(f"({product_id}, {idx}, '{url}')")
            sql_text = "INSERT INTO product_detail_images (product_id, display_order, image_url) VALUES\n"
            sql_text += ",\n".join(sql_lines) + ";\n\n"

            if filename:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(sql_text)
                print(f"상세 이미지 INSERT문이 '{filename}'에 저장되었습니다.")

        return detail_urls if detail_urls else None

    except Exception as e:
        print("상세 이미지 가져오기 실패:", e)
        return None