import http from 'node:http'
import { URL } from 'node:url'
import { cases, universities } from './data.js'

const PORT = Number(process.env.PORT || 8080)
const ALLOWED_ORIGINS = new Set([
  'http://localhost:5173',
  'http://127.0.0.1:5173',
  'http://localhost:4173',
  'http://127.0.0.1:4173'
])

const sendJson = (res, statusCode, payload, origin) => {
  const allowOrigin = origin && ALLOWED_ORIGINS.has(origin) ? origin : '*'
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  })
  res.end(JSON.stringify(payload))
}

const notFound = (res, origin) => {
  sendJson(res, 404, { code: 404, message: 'Resource not found' }, origin)
}

const badRequest = (res, message, origin) => {
  sendJson(res, 400, { code: 400, message }, origin)
}

const normalizeKeyword = (value) =>
  String(value || '')
    .trim()
    .toLowerCase()

const scoreUniversity = (university, keyword) => {
  const normalizedName = normalizeKeyword(university.name)
  const normalizedAbbr = normalizeKeyword(university.abbr)
  const normalizedCountry = normalizeKeyword(university.country)

  if (!keyword) return 0
  if (normalizedName === keyword || normalizedAbbr === keyword) return 100
  if (normalizedName.startsWith(keyword) || normalizedAbbr.startsWith(keyword)) return 80
  if (normalizedName.includes(keyword)) return 60
  if (normalizedCountry.includes(keyword)) return 30
  return 0
}

const toKnowledgeBaseItem = (university) => ({
  id: university.id,
  name: university.name,
  gpaRequirement: university.gpaRequirement,
  description: university.description
})

const toFeaturedUniversity = (university) => ({
  id: university.id,
  abbr: university.abbr,
  name: university.name,
  country: university.country
})

const toUniversityDetail = (university) => ({
  name: university.name,
  subtitle: university.location,
  description: university.description,
  stats: university.stats,
  highlights: university.highlights
})

const parseBody = async (req) =>
  new Promise((resolve, reject) => {
    let raw = ''
    req.on('data', (chunk) => {
      raw += chunk
      if (raw.length > 1024 * 1024) {
        reject(new Error('Request body too large'))
      }
    })
    req.on('end', () => {
      if (!raw) {
        resolve({})
        return
      }

      try {
        resolve(JSON.parse(raw))
      } catch (error) {
        reject(error)
      }
    })
    req.on('error', reject)
  })

const buildChatReply = (message, historyLength) => {
  const normalized = normalizeKeyword(message)
  if (normalized.includes('oxford')) {
    return 'Oxford is highly selective. Prioritize GPA strength, research alignment, and a clear academic motivation statement.'
  }
  if (normalized.includes('hku') || normalized.includes('hong kong')) {
    return 'Hong Kong universities are usually a pragmatic target set for applicants from joint-venture universities because competitiveness and location advantages are balanced.'
  }
  if (normalized.includes('ai') || normalized.includes('computer')) {
    return 'For AI-related applications, compare curriculum depth, lab access, faculty match, and language score thresholds rather than rankings alone.'
  }
  return historyLength > 2
    ? 'Based on the current conversation, narrow your shortlist by region, language requirement, GPA threshold, and program fit before comparing rankings.'
    : 'State the university or region you want to compare, and I can structure the shortlist by competitiveness, cost, and fit.'
}

const server = http.createServer(async (req, res) => {
  const origin = req.headers.origin

  if (!req.url || !req.method) {
    notFound(res, origin)
    return
  }

  if (req.method === 'OPTIONS') {
    sendJson(res, 200, { ok: true }, origin)
    return
  }

  const requestUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`)
  const { pathname, searchParams } = requestUrl

  try {
    if (req.method === 'GET' && pathname === '/api/universities/featured') {
      sendJson(res, 200, universities.slice(0, 6).map(toFeaturedUniversity), origin)
      return
    }

    if (req.method === 'GET' && pathname === '/api/cases/latest') {
      sendJson(res, 200, cases.map(({ id, offer, major, gpa, langTest, experience }) => ({
        id,
        offer,
        major,
        gpa,
        langTest,
        experience
      })), origin)
      return
    }

    if (req.method === 'GET' && pathname === '/api/universities') {
      const region = normalizeKeyword(searchParams.get('region'))
      if (!region) {
        badRequest(res, 'Query parameter "region" is required', origin)
        return
      }

      const data = universities
        .filter((item) => item.region === region)
        .map(toKnowledgeBaseItem)

      sendJson(res, 200, { code: 200, data }, origin)
      return
    }

    if (req.method === 'GET' && pathname === '/api/universities/suggestions') {
      const keyword = normalizeKeyword(searchParams.get('keyword'))
      if (keyword.length < 1) {
        sendJson(res, 200, { code: 200, data: [] }, origin)
        return
      }

      const data = universities
        .map((item) => ({ item, score: scoreUniversity(item, keyword) }))
        .filter(({ score }) => score > 0)
        .sort((left, right) => right.score - left.score || left.item.name.localeCompare(right.item.name))
        .slice(0, 8)
        .map(({ item }) => ({
          id: item.id,
          name: item.name,
          country: item.country
        }))

      sendJson(res, 200, { code: 200, data }, origin)
      return
    }

    if (req.method === 'POST' && pathname === '/api/rag/search') {
      const body = await parseBody(req)
      const keyword = normalizeKeyword(body?.query)
      if (keyword.length < 2) {
        badRequest(res, 'Query must contain at least 2 characters', origin)
        return
      }

      const data = universities
        .map((item) => ({ item, score: scoreUniversity(item, keyword) }))
        .filter(({ score }) => score > 0)
        .sort((left, right) => right.score - left.score || left.item.name.localeCompare(right.item.name))
        .slice(0, 10)
        .map(({ item }) => toKnowledgeBaseItem(item))

      sendJson(res, 200, { code: 200, data }, origin)
      return
    }

    if (req.method === 'GET' && pathname.startsWith('/api/details/')) {
      const parts = pathname.split('/').filter(Boolean)
      const [, , type, id] = parts

      if (!type || !id) {
        badRequest(res, 'Detail route requires type and id', origin)
        return
      }

      if (type === 'university') {
        const university = universities.find((item) => String(item.id) === id)
        if (!university) {
          notFound(res, origin)
          return
        }
        sendJson(res, 200, toUniversityDetail(university), origin)
        return
      }

      if (type === 'case') {
        const applicationCase = cases.find((item) => String(item.id) === id)
        if (!applicationCase) {
          notFound(res, origin)
          return
        }
        sendJson(res, 200, {
          title: applicationCase.title,
          subtitle: applicationCase.subtitle,
          major: applicationCase.major,
          description: applicationCase.description,
          stats: applicationCase.stats,
          highlights: applicationCase.highlights
        }, origin)
        return
      }

      badRequest(res, 'Unsupported detail type', origin)
      return
    }

    if (req.method === 'POST' && pathname === '/api/chat/init') {
      const body = await parseBody(req)
      const major = String(body?.major || 'your major')
      const gpa = String(body?.gpa || 'your GPA')
      const keywords = String(body?.keywords || 'your background keywords')

      sendJson(res, 200, {
        code: 200,
        data: {
          reply: `Profile received: major=${major}, GPA=${gpa}, keywords=${keywords}. For initial targeting, consider HK and UK programs first, then compare with selective US options based on research fit and language scores.`
        }
      }, origin)
      return
    }

    if (req.method === 'POST' && pathname === '/api/chat/send') {
      const body = await parseBody(req)
      const message = String(body?.message || '')
      const history = Array.isArray(body?.history) ? body.history : []

      sendJson(res, 200, {
        code: 200,
        data: {
          reply: buildChatReply(message, history.length)
        }
      }, origin)
      return
    }

    notFound(res, origin)
  } catch (error) {
    sendJson(res, 500, {
      code: 500,
      message: 'Internal server error',
      detail: error instanceof Error ? error.message : String(error)
    }, origin)
  }
})

server.listen(PORT, () => {
  console.log(`GradHelper backend running at http://localhost:${PORT}`)
})
