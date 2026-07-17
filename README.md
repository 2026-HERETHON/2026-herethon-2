2026-herethon-2
-
2026 여기톤 : HE:REthon 2팀

<br/>

<img src="static/img/readme.svg" width="510" /> 
 
> 경력단절 여성을 위한, 프로젝트 매칭 서비스 RE:Bridge입니다.
 
 
<br/>

## 🌱 프로젝트 소개
 
경력 단절 여성은 재취업까지 **평균 7.5년**이 걸립니다.

저희는 이들에게 작은 프로젝트부터 **다시 시작**할 수 있는 단계적인 복귀 경로가 필요하다고 보았습니다.

리브릿지는 **여성 인재**와 **기업**을 **프로젝트**로 연결해, 

**다시** 일을 시작하고 업무 감각을 **회복**할 수 있도록 돕습니다.

 
<br/>

## ✨ 주요 기능
 
| 기능 | 설명 |
|------|------|
| 📝 4단계 자가진단 | 직무 · 스킬 · 조건 · 공백기 활동을 입력하고, **실무 프로젝트**와 **워밍업 프로젝트** 중 현재 상황에 맞는 경로 선택 |
| 🔄 숨은 능력 번역 | **공백기 경험**을 **비즈니스 직무 역량**으로 변환해 프로젝트 매칭에 활용 |
| 📊 실시간 매칭률 | **8가지 기준**을 바탕으로 프로젝트별 **매칭률**을 계산해 적합한 프로젝트 추천 |
| 🏷️ 스킬 갭 분석 | 내 보유 스킬과 기업의 필요 스킬을 **초록색/회색 태그로 대조해 보완할 역량을 한눈에 표시 |
 
<br/>

## 🖼️ 시연 영상
 

 
<br/>

## 🛠 기술 스택
 
**Frontend**

 ![이름](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=이름&logoColor=white) ![이름](https://img.shields.io/badge/CSS3-663399?style=for-the-badge&logo=이름&logoColor=white) ![이름](https://img.shields.io/badge/Javascript-F7DF1E?style=for-the-badge&logo=이름&logoColor=white)
  
**Backend**

![이름](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=이름&logoColor=white) 
![이름](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=이름&logoColor=white)

**협업**

<img src="https://img.shields.io/badge/Git-F03C2E?style=flat&logo=Git&logoColor=white"/>  <img src="https://img.shields.io/badge/github-181717?style=flat&logo=GitHub&logoColor=white"/> <img src="https://img.shields.io/badge/Figma-F24E1E?style=flat&logo=Figma&logoColor=white"/> <img src="https://img.shields.io/badge/Notion-000000?style=flat&logo=Notion&logoColor=white"/> 

<br/>

## 👩‍💻 팀원
 
| 이름 | 역할 | GitHub |
|------|------|--------|
| 시원 | 기획/디자인 | [@co0000oo000l](https://github.com/co0000oo000l) |
| 지민 | Frontend | [@jiminxha](https://github.com/jiminxha) |
| 수빈 | Frontend | [@chubin925](https://github.com/아이디) |
| 현주 | Backend | [@0hyunj](https://github.com/0hyunj) |
| 가윤 | Backend | [@riveryunny](https://github.com/riveryunny) |



<br/>

## 📂 폴더 구조
 
```
2026-herethon-2/
├── config/              # Django 프로젝트 설정
├── <app이름>/            # 기능별 앱
│   ├── templates/       # HTML 템플릿
│   ├── views.py
│   └── models.py
│   └── static/          # CSS, JS, 이미지
├── manage.py
└── requirements.txt
```

 
<br/>

## 🚀 실행 방법
 
```bash
# 1. 클론
git clone https://github.com/2026-HERETHON/2026-herethon-2.git
cd 2026-herethon-2
 
# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
 
# 3. 패키지 설치
pip install -r requirements.txt
 
# 4. 마이그레이션 및 실행
python manage.py migrate
python manage.py runserver
```

<br/>

## 🌿 협업 규칙
 
**브랜치 전략**
- `main`: 최종 배포 및 발표용
- `develop`: 개발 통합
- `fe/feat/기능명`: 프론트 기능 개발
- `be/feat/기능명`: 백엔드 기능 개발

<br/>
 
**커밋 컨벤션**
| 태그 | 설명 |
|------|------|
| `feat` | 새 기능 추가 |
| `fix` | 버그 수정 |
| `design` | UI/CSS 수정 |
| `refactor` | 코드 리팩토링 |
| `chore` | 잡무/세팅 |
| `docs` | 문서 수정 |
| `test` | 테스트 |

<br/>
