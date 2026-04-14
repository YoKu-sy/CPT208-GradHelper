# GradHelper Web 后端接口对接文档

本文档基于当前前端代码（`AIChat`、`DetailView`、`KnowledgeBase`）整理，目标是让后端同学按本文即可完成可联调接口。

## 1. 基础约定

- 前端默认后端地址：
  - `AIChat`、`DetailView`：`VITE_API_BASE_URL`（未配置时回退 `http://localhost:8080`）
  - `KnowledgeBase`：当前代码写死 `http://localhost:8080`
- 需要开启 CORS（至少允许前端开发域名，例如 `http://localhost:5173`）。
- 数据编码：`UTF-8`，`Content-Type: application/json`。

## 2. 接口总览

1. `GET /api/cases/latest`
用途：`AIChat` 左侧申请案例小卡片。

2. `GET /api/universities/featured`
用途：`AIChat` 右侧学校小卡片。

3. `GET /api/details/{type}/{id}`
用途：点击 `AIChat` 小卡片后进入 `DetailView` 详情页。  
`type` 仅允许：`case` / `university`。

4. `GET /api/universities?region={regionId}`
用途：`KnowledgeBase` 按地区查询学校列表。  
`regionId` 当前使用：`hk` / `uk` / `usa` / `eu` / `aus`。

5. `POST /api/rag/search`
用途：`KnowledgeBase` 顶部搜索（RAG 检索）。

## 3. 详细契约

### 3.1 `GET /api/cases/latest`

请求：
- Query 参数：无（可选支持 `limit`，前端当前未传）

前端当前严格期望返回：`Array`（不是对象包裹）

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

可兼容字段（前端已做映射容错）：
- `offer | offerSchool | schoolAbbr`
- `major | program`
- `gpa | GPA`
- `langTest | languageTest | ielts | toefl`
- `experience | background`

### 3.2 `GET /api/universities/featured`

请求：
- Query 参数：无

前端当前严格期望返回：`Array`

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

可兼容字段（前端已做映射容错）：
- `abbr | shortName | code`
- `name | universityName`
- `country | location`

### 3.3 `GET /api/details/{type}/{id}`

请求路径参数：
- `type`: `case` 或 `university`
- `id`: 卡片主键（字符串或数字都可）

前端当前严格期望返回：`Object`（不是 `{ data: ... }`）

推荐返回结构（两种 type 共用）：

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
  "highlights": ["科研背景强", "有相关实习"]
}
```

说明：
- `case` 类型：顶部主标题优先用 `title`（没有时退化到 `name`）。
- `university` 类型：顶部主标题优先用 `name`（没有时退化到 `title`）。
- `stats` 必须是对象，`highlights` 必须是字符串数组（可空数组）。

### 3.4 `GET /api/universities?region={regionId}`

请求：
- Query 参数：`region`（`hk/uk/usa/eu/aus`）

前端当前严格期望返回：对象包裹，且列表在 `data` 字段：

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

列表项关键字段：
- `id`
- `name`
- `gpaRequirement`（或 `gpaReq`）
- `description`

### 3.5 `POST /api/rag/search`

请求体：

```json
{
  "query": "Oxford"
}
```

前端当前严格期望返回：对象包裹，且列表在 `data` 字段（结构同 3.4）

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

## 4. 错误码与异常建议

- `200`：成功
- `400`：参数错误（例如 `type` 非法、`region` 非法、query 为空）
- `404`：详情不存在
- `500`：服务端异常

建议错误结构：

```json
{
  "code": 400,
  "message": "Invalid region"
}
```

## 5. 当前联调注意事项（非常重要）

1. 当前前端的返回格式不完全统一：
- `AIChat` 两个列表接口要求直接返回数组。
- `DetailView` 详情接口要求直接返回对象。
- `KnowledgeBase` 两个接口要求返回 `{ data: [...] }`。

2. 如果后端想统一成同一种包裹格式（例如都用 `{ code, data }`），需要前端同步改解析逻辑，否则会触发 mock 回退或无数据。

3. `DetailView` 的 `type` 由路由透传，后端必须支持：
- `/api/details/case/{id}`
- `/api/details/university/{id}`

## 6. 最小可用实现顺序（建议）

1. 先完成 `GET /api/cases/latest` + `GET /api/universities/featured`（AIChat 首屏可真数据）。
2. 再完成 `GET /api/details/{type}/{id}`（卡片点进详情页可真数据）。
3. 最后完成 `KnowledgeBase` 的地区查询与搜索接口。
