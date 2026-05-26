# 🛍️ 메루카리 디스코드 알림봇

메루카리에서 특정 키워드로 신규 상품이 등록되면 디스코드 웹훅으로 실시간 알림을 보내주는 봇입니다.

---

## ✨ 주요 기능

- 지정한 키워드로 메루카리 최신순 검색
- 새로운 상품 감지 시 디스코드 채널에 임베드 알림 전송
- 상품명, 가격, 이미지, 상품 링크 포함
- 설정 가능한 검사 주기 (기본 90초)

---

## 📸 알림 예시

디스코드에 아래와 같은 형태로 알림이 전송됩니다.

> ✨ **[신상 발견] 상품 제목**
> **가격:** 500엔
> [상품 보러가기](https://jp.mercari.com/item/...)

---

## 🚀 시작하기

### 1. 레포지토리 클론

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example`을 복사해 `.env` 파일을 만들고 값을 채워주세요.

```bash
cp .env.example .env
```

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook
MERCARI_KEYWORD=아이카츠
INTERVAL=90
```

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `DISCORD_WEBHOOK_URL` | 디스코드 웹훅 URL (필수) | - |
| `MERCARI_KEYWORD` | 검색할 키워드 | `アイカツ` |
| `INTERVAL` | 검사 주기 (초) | `90` |

### 4. 실행

```bash
python main.py
```

---

## 📦 의존성

```
mercapi
python-dotenv
requests
nest_asyncio
```

---

## 📁 프로젝트 구조

```
.
├── main.py          # 메인 봇 스크립트
├── .env             # 환경 변수 (git 제외)
├── .env.example     # 환경 변수 예시
├── requirements.txt
└── README.md
```

---

## ⚠️ 주의사항

- `.env` 파일은 절대 깃허브에 올리지 마세요. `.gitignore`에 추가해두세요.
- 메루카리 API는 비공식 라이브러리(`mercapi`)를 사용하므로 서비스 변경에 따라 동작하지 않을 수 있습니다.
- 검사 주기를 너무 짧게 설정하면 API 요청이 차단될 수 있습니다. 60초 이상 권장합니다.

