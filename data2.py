from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.get("https://news.naver.com/")
driver.maximize_window()

# 메뉴 UL XPATH
menu_ul_xpath = "/html/body/section/header/div[2]/div/div/div/div/div/ul"

# 메뉴 로딩
menu_ul = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, menu_ul_xpath))
)

# 메뉴 href 목록 수집
menus = menu_ul.find_elements(By.TAG_NAME, "a")
menu_list = [(m.text, m.get_attribute("href")) for m in menus]

print("메뉴 리스트:", menu_list)

# 각 메뉴 순차 이동
for name, url in menu_list:
    print(f"\n▶ 메뉴 '{name}' 이동 중 → {url}")
    driver.get(url)
    time.sleep(2)

    try:
        # 헤드라인 첫 번째 뉴스 a 태그 찾기
        # ID가 랜덤일 수 있으므로 contains()로 대응
        headline_xpath = '(//*[contains(@id,"_SECTION_HEADLINE_LIST")]/li[1]/div/div/div[1]/div/a)'

        a_tag = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, headline_xpath))
        )

        # 내부 img 태그 찾기
        img_tag = a_tag.find_element(By.TAG_NAME, "img")
        img_src = img_tag.get_attribute("src")

        print(f"  ✔ '{name}' 메뉴의 헤드라인 이미지 src → {img_src}")

    except Exception as e:
        print(f"  ✖ '{name}' 메뉴에서 헤드라인 이미지 찾기 실패:", e)
        continue  # 예외 발생 시 다음 메뉴로 이동

driver.quit()
