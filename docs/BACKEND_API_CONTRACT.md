# GradHelper Web Backend API Contract

This document lists all backend endpoints required by the current frontend codebase (`AIChat`, `DetailView`, `KnowledgeBase`).

## 1. Base Rules

- API base URL:
  - `AIChat` and `DetailView`: `VITE_API_BASE_URL`, fallback `http://localhost:8080`
  - `KnowledgeBase`: currently hardcoded to `http://localhost:8080`
- Enable CORS for frontend origin (for local dev usually `http://localhost:5173`).
- Response format: `application/json`, UTF-8.

## 2. Endpoint Summary

1. `GET /api/cases/latest`
2. `GET /api/universities/featured`
3. `GET /api/details/{type}/{id}`
4. `GET /api/universities?region={regionId}`
5. `POST /api/rag/search`
6. `POST /api/chat/init`
7. `POST /api/chat/send`

## 3. Endpoint Details

### 3.1 `GET /api/cases/latest`

Used by: AIChat left sidebar cards.

Expected response by frontend: raw `Array` (not wrapped).

```json
[
  {
    "id": 101,
    "offer": "KTH",
    "major": "CS",
    "gpa": "3.6",
    "langTest": "IELTS 7.0",
    "experience": "2 Internships"
  }
]
```

Compatible aliases in frontend mapping:
- `offer | offerSchool | schoolAbbr`
- `major | program`
- `gpa | GPA`
- `langTest | languageTest | ielts | toefl`
- `experience | background`

### 3.2 `GET /api/universities/featured`

Used by: AIChat right sidebar cards.

Expected response by frontend: raw `Array` (not wrapped).

```json
[
  {
    "id": 1,
    "abbr": "MIT",
    "name": "Massachusetts Institute of Technology",
    "country": "USA"
  }
]
```

Compatible aliases in frontend mapping:
- `abbr | shortName | code`
- `name | universityName`
- `country | location`

### 3.3 `GET /api/details/{type}/{id}`

Used by: detail page after clicking AIChat cards.

Path params:
- `type`: `case` or `university`
- `id`: card id

Expected response by frontend: raw `Object` (not wrapped).

```json
{
  "title": "KTH Offer Case",
  "name": "KTH Royal Institute of Technology",
  "subtitle": "Stockholm, Sweden",
  "major": "Computer Science",
  "description": "Long text...",
  "stats": {
    "GPA": "3.8/4.0",
    "IELTS": "7.0"
  },
  "highlights": ["Research experience", "Relevant internship"]
}
```

Notes:
- For `case`, frontend prefers `title`.
- For `university`, frontend prefers `name`.
- `stats` should be an object.
- `highlights` should be an array of strings.

### 3.4 `GET /api/universities?region={regionId}`

Used by: KnowledgeBase region filtering.

Query param:
- `region`: `hk | uk | usa | eu | aus`

Expected response by frontend: wrapped object with `data`.

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "HKU",
      "gpaRequirement": "3.5",
      "description": "..."
    }
  ]
}
```

List item fields used by frontend:
- `id`
- `name`
- `gpaRequirement` (or `gpaReq`)
- `description`

### 3.5 `POST /api/rag/search`

Used by: KnowledgeBase top search box.

Request:

```json
{
  "query": "Oxford"
}
```

Expected response by frontend: same shape as 3.4 (`{ code, data: [] }`).

```json
{
  "code": 200,
  "data": [
    {
      "id": 11,
      "name": "University of Oxford",
      "gpaRequirement": "3.7",
      "description": "..."
    }
  ]
}
```

### 3.6 `POST /api/chat/init`

Used by: AIChat, after user clicks `Save Profile & Init AI`.

Request:

```json
{
  "major": "Computer Science and Technology",
  "gpa": "3.8/4.0",
  "keywords": "AI Lab, Robotics"
}
```

Expected response by frontend:
- Frontend reads `result.data.reply`.

```json
{
  "code": 200,
  "data": {
    "reply": "Great profile. I suggest focusing on CS programs in HK and UK first."
  }
}
```

### 3.7 `POST /api/chat/send`

Used by: AIChat send message.

Request:

```json
{
  "message": "Can you compare HKU and UCL for AI?",
  "history": [
    { "role": "ai", "content": "..." },
    { "role": "user", "content": "..." }
  ]
}
```

Expected response by frontend:
- Frontend reads `result.data.reply`.

```json
{
  "code": 200,
  "data": {
    "reply": "Here is a quick comparison..."
  }
}
```

## 4. Error Handling Suggestion

Suggested status codes:
- `200` success
- `400` invalid request
- `404` not found
- `500` server error

Suggested error body:

```json
{
  "code": 400,
  "message": "Invalid region"
}
```

## 5. Important Integration Notes

Current frontend expects mixed response styles:
- AIChat sidebars: raw arrays
- DetailView: raw object
- KnowledgeBase: wrapped object with `data`
- AIChat chat APIs: wrapped object with `data.reply`

If backend wants fully unified response style, frontend parsing must be updated in the corresponding views.

## 6. Recommended Delivery Order

1. `GET /api/cases/latest` + `GET /api/universities/featured`
2. `GET /api/details/{type}/{id}`
3. `POST /api/chat/init` + `POST /api/chat/send`
4. `GET /api/universities?region=...` + `POST /api/rag/search`
