# RepoMind

RepoMind는 종료된 프로젝트를 다시 사용할 수 있는 기술 자산으로 정리하는 AI 기반 프로젝트 메모리 서비스입니다. GitHub 저장소나 로컬 ZIP/보고서를 분석해 프로젝트 구조, 사용 기술, 나의 역할, 개발 과정, 결과물, 성과, 향상된 역량을 저장하고, 이후 프로필과 포트폴리오 생성에 재사용하는 것을 목표로 합니다.

## 주제

종료된 프로젝트 메모리/이력 관리 서비스

## 현재 MVP

- React/Vite 프론트엔드
- FastAPI 백엔드
- 로컬 개발용 SQLite 저장소
- GitHub 공개 저장소 분석
- 로컬 ZIP 업로드 분석
- 보고서 생성 프롬프트 제공
- 프로젝트 보관함, 내 역량, 팀원 태그 검색 화면
- 개발 로그인 기반 API 저장
- 로컬 RAG 대체 분석기
- AWS 전환용 Cognito, S3, RDS PostgreSQL, Bedrock Knowledge Bases 설정 지점

## 팀 기능 분리

| 담당 | 기능 | API/DB 연결 |
| --- | --- | --- |
| 1번 | 종료된 프로젝트 정리, GitHub/문서/이미지/보고서 업로드 | `projects`, `project_sources` |
| 2번 | 누적 프로젝트 기반 PROFILE 생성 | `profiles/me`, `profiles/{public_tag}` |
| 3번 | 포트폴리오 초안 생성 | `portfolio/drafts/{project_id}` |
| 나 | RAG 분석, DB 구축, AWS AI 연결, 로그인 | `analysis_results`, Cognito, S3, Bedrock |

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| Frontend | React 18, TypeScript, Vite, ky, Zod |
| Backend | FastAPI, Pydantic v2, SQLAlchemy async |
| Local DB | SQLite, aiosqlite |
| AWS DB | RDS PostgreSQL, asyncpg |
| Auth | Amazon Cognito User Pool |
| File Storage | Amazon S3 |
| AI/RAG | Amazon Bedrock Knowledge Bases |
| Test | Vitest, pytest |
| Deploy | S3 + CloudFront, EC2 또는 ECS Fargate |

## 프로젝트 구조

```text
repomind/
├─ backend/
│  ├─ src/repomind_api/
│  │  ├─ auth.py
│  │  ├─ aws_services.py
│  │  ├─ config.py
│  │  ├─ database.py
│  │  ├─ main.py
│  │  ├─ models.py
│  │  ├─ rag.py
│  │  ├─ repository.py
│  │  ├─ repository_records.py
│  │  ├─ schemas.py
│  │  └─ routers/projects.py
│  ├─ tests/
│  └─ pyproject.toml
├─ docs/
├─ src/
│  ├─ analysis/
│  ├─ components/
│  ├─ api.ts
│  ├─ App.tsx
│  └─ domain.ts
├─ DESIGN.md
├─ package.json
└─ vite.config.ts
```

## 로컬 실행

### 1. 프론트엔드 의존성 설치

```bash
npm install
```

### 2. 백엔드 의존성 설치

```bash
uv sync --project backend
```

### 3. 백엔드 실행

```bash
npm run dev:api
```

기본 API 주소는 `http://127.0.0.1:8000`입니다. API 문서는 백엔드 실행 후 `http://127.0.0.1:8000/docs`에서 확인합니다.

### 4. 프론트엔드 실행

```bash
npm run dev
```

같은 네트워크의 다른 기기에서 보려면 다음처럼 실행합니다.

```bash
npm run dev -- --host 0.0.0.0
```

## 환경 변수

프론트엔드 `.env` 예시:

```env
VITE_REPOMIND_API_URL=http://127.0.0.1:8000
```

백엔드 `.env` 예시:

```env
REPOMIND_DATABASE_URL=sqlite+aiosqlite:///./backend/data/repomind.db
REPOMIND_AUTH_MODE=dev
REPOMIND_AWS_REGION=ap-northeast-2
REPOMIND_COGNITO_REGION=ap-northeast-2
REPOMIND_UPLOAD_MODE=local
REPOMIND_S3_BUCKET=
REPOMIND_COGNITO_USER_POOL_ID=
REPOMIND_COGNITO_AUDIENCE=
REPOMIND_BEDROCK_KNOWLEDGE_BASE_ID=
REPOMIND_BEDROCK_DATA_SOURCE_ID=
```

RDS PostgreSQL로 전환할 때는 다음 형식으로 바꿉니다.

```env
REPOMIND_DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/repomind
```

S3 presigned upload를 사용하려면 다음 값을 설정합니다.

```env
REPOMIND_UPLOAD_MODE=s3
REPOMIND_S3_BUCKET=repomind-project-sources
```

Cognito를 실제 인증으로 사용할 때는 다음 값을 설정합니다.

```env
REPOMIND_AUTH_MODE=cognito
REPOMIND_COGNITO_USER_POOL_ID=ap-northeast-2_xxxxxxxx
REPOMIND_COGNITO_AUDIENCE=your-app-client-id
```

## 주요 API

개발 모드에서는 다음 헤더를 사용합니다.

```http
Authorization: Bearer dev:local-user
X-RepoMind-Public-Tag: SCNU_20224254
X-RepoMind-Display-Name: Gayeon
```

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/health` | 백엔드 상태 확인 |
| POST | `/auth/bootstrap` | 로그인 후 사용자 프로필 생성 |
| GET | `/projects` | 내 프로젝트 목록 조회 |
| POST | `/projects` | 프로젝트 기본 정보 저장 |
| POST | `/projects/{project_id}/sources` | GitHub, 보고서, docs, 이미지, prompt 메타데이터 저장 |
| POST | `/uploads/presign` | S3 업로드 URL 발급 |
| POST | `/projects/{project_id}/ingest` | Bedrock Knowledge Base ingestion 시작 |
| POST | `/projects/{project_id}/analyze` | RAG 기반 분석 실행 후 DB 저장 |
| GET | `/projects/{project_id}/analysis` | 분석 결과 조회 |
| GET | `/profiles/me` | 내 프로젝트 기반 프로필 조회 |
| GET | `/profiles/{public_tag}` | 팀원 검색용 공개 프로필 조회 |
| GET | `/portfolio/drafts/{project_id}` | 포트폴리오 초안 조회 |
| DELETE | `/projects/{project_id}` | 프로젝트 삭제 |

## 테스트와 빌드

```bash
npm run test
npm run build
npm run test:api
```

## AWS 생성 순서

리전은 `ap-northeast-2`로 통일합니다.

1. S3 버킷 생성: 프로젝트 보고서, docs, 이미지, ZIP 저장
2. RDS PostgreSQL 생성: `repomind` DB 준비
3. Cognito User Pool 생성: 이메일 로그인, App client, Hosted UI 설정
4. Bedrock Model access 활성화: Titan Embeddings와 생성 모델 사용 권한 확인
5. Bedrock Knowledge Base 생성: S3 버킷을 data source로 연결
6. 백엔드 배포: 신규 App Runner 제한을 고려해 EC2 또는 ECS Fargate 우선
7. 프론트 배포: Vite `dist`를 S3 + CloudFront로 배포

비밀번호, access key, secret key는 README나 채팅에 남기지 않고 로컬 `.env` 또는 AWS Secret Manager에 저장합니다.
