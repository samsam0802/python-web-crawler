from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re
import json

FIELD_MAP = {
    "내용물의 용량 또는 중량": "capacity",
    "제품 주요 사양": "skin_type",
    "사용기한(또는 개봉 후 사용기간)": "usage_period",
    "사용방법": "usage_method",
    "화장품제조업자,화장품책임판매업자 및 맞춤형화장품판매업자": "manufacturer",
    "제조국": "made_in_country",
    "화장품법에 따라 기재해야 하는 모든 성분": "ingredients",
    "기능성 화장품 식품의약품안전처 심사필 여부": "functional_certification",
    "사용할 때의 주의사항": "caution",
    "품질보증기준": "quality_guarantee",
    "소비자상담 전화번호": "customer_service_number",
}


def escape_sql(value) -> str:
    """SQL에서 작은 따옴표 문제 방지"""
    if value is None:
        return ""
    return str(value).replace("'", "''")


def load_detailinfo_data():
    """detailinfo_data.json 파일에서 데이터 로드"""
    filename = "detailinfo_data.json"

    if not os.path.exists(filename):
        # 파일이 없으면 초기값 생성
        data = {
            "last_id": 0,
            "next_id": 1
        }
        print(f"[INFO] '{filename}' 파일이 없어 초기값 생성: {data}")

        # 파일 저장
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return data

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 필수 필드 확인
        if "last_id" not in data or "next_id" not in data:
            print(f"[WARNING] '{filename}' 파일에 필수 필드가 없어 초기화")
            data = {
                "last_id": 0,
                "next_id": 1
            }

        print(f"[INFO] '{filename}' 파일에서 데이터 로드: {data}")
        return data

    except (json.JSONDecodeError, Exception) as e:
        print(f"[ERROR] '{filename}' 파일 읽기 실패: {e}")
        # 오류 시 기본값 반환
        return {
            "last_id": 0,
            "next_id": 1
        }


def save_detailinfo_data(data, transaction=None):
    """detailinfo_data.json 파일에 데이터 저장"""
    filename = "detailinfo_data.json"

    # JSON 문자열 생성
    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    # trailing comma 방지
    import re
    json_str = re.sub(r',\s*\n\s*}', '\n}', json_str)
    json_str = re.sub(r',\s*\n\s*]', '\n]', json_str)

    # 저장
    if transaction:
        transaction.write_file(filename, json_str)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_str)

    print(f"[INFO] '{filename}' 파일 업데이트: {data}")


def save_detailinfo_data(data, transaction=None):
    """detailinfo_data.json 파일에 데이터 저장"""
    filename = "detailinfo_data.json"

    # JSON 문자열 생성
    json_str = json.dumps(data, indent=2, ensure_ascii=False)

    # trailing comma 방지
    import re
    json_str = re.sub(r',\s*\n\s*}', '\n}', json_str)
    json_str = re.sub(r',\s*\n\s*]', '\n]', json_str)

    # 저장
    if transaction:
        transaction.write_file(filename, json_str)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_str)

    print(f"[INFO] '{filename}' 파일 업데이트: {data}")


def get_next_detailinfo_id(transaction=None):
    """다음 detailinfo ID를 가져오고 데이터 업데이트"""
    # 데이터 로드
    data = load_detailinfo_data()

    # 현재 next_id 가져오기
    current_next_id = data["next_id"]

    print(f"[INFO] 할당할 ID: {current_next_id}")

    # 데이터 업데이트: last_id = 현재 next_id, next_id = next_id + 1
    data["last_id"] = current_next_id
    data["next_id"] = current_next_id + 1

    # 저장
    save_detailinfo_data(data, transaction)

    return current_next_id


def get_product_dtailinfo_provided(driver, transaction=None, filename: str = None):
    """
    상품정보 제공고시 테이블을 가져오는 함수
    ID는 자동으로 증가합니다.

    Args:
        driver: Selenium WebDriver
        transaction: FileTransaction 객체 (트랜잭션 사용 시)
        filename: SQL 파일명

    Returns:
        tuple: (product_info dict, product_detail_info_id)
    """

    # 1. 다음 ID 가져오기 (JSON 파일 참조)
    product_detail_info_id = get_next_detailinfo_id(transaction)
    print(f"[INFO] 생성된 상세정보 ID: {product_detail_info_id}")

    try:
        # 웹 요소 찾기 및 클릭
        wait = WebDriverWait(driver, 10)
        button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="tab-panels"]/section/ul/li[1]/button/span')
            )
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)

        # 테이블 데이터 수집
        table = driver.find_element(By.CSS_SELECTOR, "div.Accordion_content__aIya4 table.Accordion_table__mcFPq")
        rows = table.find_elements(By.TAG_NAME, "tr")
        product_info = {}

        for row in rows:
            try:
                key = row.find_element(By.TAG_NAME, "th").text.strip()
                value = row.find_element(By.TAG_NAME, "td").text.strip()
                product_info[key] = value
            except:
                continue

        print(f"상품정보 제공고시 {len(product_info)}개 항목 수집 완료")

        # SQL 값 준비
        ordered_values = []
        for key, column in FIELD_MAP.items():
            value = product_info.get(key, "")
            ordered_values.append(f"'{escape_sql(str(value))}'")

        columns = ', '.join(FIELD_MAP.values())
        values = ', '.join(ordered_values)

        # SQL 문 생성
        values_sql = f"({product_detail_info_id}, {values}, NOW(), NOW())"

        # SQL 문장 전체
        full_sql = f"INSERT INTO product_detail_info (id, {columns}, created_at, updated_at)\nVALUES\n{values_sql});"

        print(f"[DEBUG] 생성된 SQL: {full_sql}")

        # 6. 파일 저장
        if filename:
            try:
                # 파일 존재 여부 및 내용 확인
                file_exists = False
                existing_content = ""

                if transaction:
                    # 트랜잭션 모드일 때는 실제 파일을 읽어봅니다
                    try:
                        with open(filename, 'r', encoding='utf-8') as f:
                            existing_content = f.read()
                        file_exists = True
                        print(f"[DEBUG] 트랜잭션 모드: 파일 존재함, 길이: {len(existing_content)}")
                    except FileNotFoundError:
                        file_exists = False
                        print("[DEBUG] 트랜잭션 모드: 파일 없음")
                else:
                    # 일반 모드일 때는 직접 확인
                    file_exists = os.path.exists(filename)
                    if file_exists and os.path.getsize(filename) > 0:
                        with open(filename, 'r', encoding='utf-8') as f:
                            existing_content = f.read()
                        print(f"[DEBUG] 일반 모드: 파일 존재함, 길이: {len(existing_content)}")
                    else:
                        file_exists = False
                        print("[DEBUG] 일반 모드: 파일 없거나 비어있음")

                if not file_exists or existing_content.strip() == "":
                    # 첫 번째 레코드: INSERT 문 전체 작성
                    if transaction:
                        transaction.write_file(filename, full_sql)
                    else:
                        with open(filename, "w", encoding='utf-8') as f:
                            f.write(full_sql)
                    print(f"✓ 첫 번째 레코드 저장 완료 (ID: {product_detail_info_id})")
                else:
                    # 기존 파일이 있으면 VALUES만 추가
                    content = existing_content.strip()

                    # 마지막 문자 상태에 따라 처리
                    if content.endswith(');'):
                        # 정상 종료된 경우: );를 ),로 교체
                        content = content[:-2] + '),'
                    elif content.endswith(';'):
                        # 세미콜론만 있는 경우: ;를 ,로 교체
                        content = content[:-1] + ','
                    elif content.endswith(')'):
                        # 괄호만 있는 경우: 콤마 추가
                        content = content + ','
                    elif content.endswith(','):
                        # 이미 콤마로 끝난 경우: 그대로 사용
                        pass
                    else:
                        # 예상치 못한 형식: 콤마 추가
                        content = content + ','

                        # 새로운 VALUES 추가 (항상 );로 종료)
                    new_content = content + f"\n{values_sql};"

                    if transaction:
                        transaction.write_file(filename, new_content)
                    else:
                        with open(filename, "w", encoding='utf-8') as f:
                            f.write(new_content)

                    print(f"✓ 추가 레코드 저장 완료 (ID: {product_detail_info_id})")

            except Exception as file_error:
                print(f"✗ 파일 저장 중 오류 발생: {file_error}")
                import traceback
                traceback.print_exc()

        return product_info, product_detail_info_id

    except Exception as e:
        print(f"✗ 상품정보 제공고시 수집 실패: {e}")
        import traceback
        traceback.print_exc()
        return {}, product_detail_info_id