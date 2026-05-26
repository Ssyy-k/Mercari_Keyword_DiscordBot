import os
import time
import asyncio
import requests
import nest_asyncio

from dotenv import load_dotenv
from mercapi import Mercapi
from mercapi.requests import SearchRequestData

# --------------------------------------------------
# .env 파일 불러오기
# --------------------------------------------------
load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
KEYWORD = os.getenv("MERCARI_KEYWORD", "アイカツ")
INTERVAL = int(os.getenv("INTERVAL", "90"))

if not WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")

# --------------------------------------------------
# 메루카리 API
# --------------------------------------------------
api = Mercapi()

# 이미 본 상품 저장
seen_ids = set()

# --------------------------------------------------
# 상품 ID 추출
# --------------------------------------------------
def get_item_id(item_obj):
    if item_obj is None:
        return None

    # 자주 쓰이는 후보 필드들
    for attr in ["id", "id_", "item_id"]:
        val = getattr(item_obj, attr, None)
        if val:
            return str(val)

    # __dict__ 내부도 확인
    d = getattr(item_obj, "__dict__", {})
    for key in ["id", "id_", "item_id"]:
        if key in d and d[key]:
            return str(d[key])

    return None

# --------------------------------------------------
# 이미지 URL 추출
# --------------------------------------------------
def get_first_image(item_obj):
    for attr in ["thumbnails", "photos", "images"]:
        val = getattr(item_obj, attr, [])

        if val and len(val) > 0:
            first = val[0]

            # 문자열이면 그대로 반환
            if isinstance(first, str):
                return first

            # 객체면 url 속성 확인
            return getattr(first, "url", "")

    return ""

# --------------------------------------------------
# 디스코드 웹훅 전송
# --------------------------------------------------
def send_to_discord(item_id, item_name, item_price, img_url):
    embed = {
        "title": f"✨ [신상 발견] {item_name}",
        "description": (
            f"**가격:** {item_price}엔\n"
            f"[상품 보러가기](https://jp.mercari.com/item/{item_id})"
        ),
        "color": 16711680,
    }

    if img_url:
        embed["image"] = {"url": img_url}

    payload = {
        "embeds": [embed]
    }

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10
        )

        if response.status_code in [200, 204]:
            print("디스코드 알림 전송 완료")
        else:
            print(f"디스코드 전송 실패: {response.status_code}")

    except Exception as e:
        print(f"디스코드 전송 에러: {e}")

# --------------------------------------------------
# 새 상품 체크
# --------------------------------------------------
async def check_new_items():
    global seen_ids

    print(f"[{time.strftime('%H:%M:%S')}] '{KEYWORD}' 감시 중...")

    try:
        # 최신순 검색
        search_res = await api.search(
            KEYWORD,
            sort_by=SearchRequestData.SortBy.SORT_CREATED_TIME,
            sort_order=SearchRequestData.SortOrder.ORDER_DESC,
            status=[SearchRequestData.Status.STATUS_ON_SALE],
        )

        # 응답 검증
        if not search_res or not hasattr(search_res, "items"):
            print("메루카리 응답 오류")
            return

        if not search_res.items:
            print("검색 결과 없음")
            return

        current_items_data = []

        # 상위 3개만 검사
        for item in search_res.items[:3]:

            try:
                # 검색 결과 객체에서 먼저 ID 추출 시도
                item_id = get_item_id(item)

                # 상세 정보 불러오기
                full_item = await item.full_item()

                # 상세 객체에서 다시 ID 추출
                if not item_id:
                    item_id = get_item_id(full_item)

                # ID 없으면 스킵
                if not item_id:
                    print("ID 추출 실패")
                    continue

                item_name = getattr(
                    full_item,
                    "name",
                    getattr(item, "name", "이름 없음")
                )

                item_price = getattr(
                    full_item,
                    "price",
                    getattr(item, "price", 0)
                )

                img_url = get_first_image(full_item)

                current_items_data.append({
                    "id": item_id,
                    "name": item_name,
                    "price": item_price,
                    "img_url": img_url
                })

            except Exception as e:
                print(f"상품 처리 중 오류: {e}")
                continue

        # 기준점 설정
        if not seen_ids:
            for it in current_items_data:
                seen_ids.add(it["id"])

            print(f"초기 기준점 설정 완료 ({len(seen_ids)}개)")
            return

        # 새 상품 찾기
        new_items = [
            it for it in current_items_data
            if it["id"] not in seen_ids
        ]

        # 새 상품 있으면 알림
        if new_items:

            # 오래된 것부터 보내기
            for it in reversed(new_items):

                print(f"신상 발견: {it['name']}")

                send_to_discord(
                    it["id"],
                    it["name"],
                    it["price"],
                    it["img_url"]
                )

                seen_ids.add(it["id"])

            # 메모리 정리
            if len(seen_ids) > 100:
                seen_ids = set(list(seen_ids)[-50:])

        else:
            print("아직 새로운 상품이 없습니다.")

    except Exception as e:
        print(f"에러 발생: {type(e).__name__}: {e}")

# --------------------------------------------------
# 메인 루프
# --------------------------------------------------
async def main():

    print("------------------------------------------")
    print(f"메루카리 디스코드 알림 봇 시작")
    print(f"검색 키워드: {KEYWORD}")
    print(f"검사 간격: {INTERVAL}초")
    print("------------------------------------------")

    while True:
        await check_new_items()
        await asyncio.sleep(INTERVAL)

# --------------------------------------------------
# 실행
# --------------------------------------------------
if __name__ == "__main__":

    try:
        nest_asyncio.apply()
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n프로그램 종료")