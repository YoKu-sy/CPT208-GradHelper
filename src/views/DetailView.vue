<template>
  <div class="min-h-screen bg-white p-8">
    <button @click="$router.back()" class="mb-8 flex items-center text-gray-500 hover:text-black transition-colors">
      <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      返回
    </button>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="detailData" class="max-w-4xl mx-auto">
      <div :class="['p-8 rounded-3xl text-white mb-8 shadow-lg', type === 'university' ? 'bg-zinc-900' : 'bg-blue-600']">
        <div class="flex items-center gap-4 mb-4">
          <span class="px-3 py-1 rounded-full bg-white/20 text-xs font-bold uppercase tracking-wider">
            {{ type === 'university' ? 'University Info' : 'Application Case' }}
          </span>
        </div>
        <h1 class="text-4xl font-bold">{{ detailData.title || detailData.name }}</h1>
        <p class="mt-4 text-white/80 text-lg">{{ detailData.subtitle || detailData.major }}</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="space-y-6">
          <div class="bg-gray-50 p-6 rounded-2xl border border-gray-100">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">关键指标 / Requirements</h3>
            <div class="space-y-4">
              <div v-for="(val, key) in detailData.stats" :key="key">
                <p class="text-xs text-gray-500">{{ key }}</p>
                <p class="text-lg font-bold text-zinc-800">{{ val }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="md:col-span-2 space-y-8">
          <section>
            <h3 class="text-xl font-bold mb-4 flex items-center">
              <span class="w-1 h-6 bg-blue-500 rounded-full mr-3"></span>
              详细介绍 / Description
            </h3>
            <div class="text-gray-600 leading-relaxed space-y-4 whitespace-pre-line">
              {{ detailData.description }}
            </div>
          </section>

          <section v-if="detailData.highlights && detailData.highlights.length">
            <h3 class="text-xl font-bold mb-4 flex items-center">
              <span class="w-1 h-6 bg-green-500 rounded-full mr-3"></span>
              核心亮点 / Highlights
            </h3>
            <ul class="grid grid-cols-1 gap-3">
              <li v-for="item in detailData.highlights" :key="item" class="flex items-start bg-zinc-50 p-4 rounded-xl">
                <svg class="w-5 h-5 text-green-500 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span class="text-gray-700">{{ item }}</span>
              </li>
            </ul>
          </section>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <p class="text-gray-400">未能获取到详情数据，请检查后端连接。</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
/**
 * =========================
 * DetailView 对接说明（给前后端同学）
 * =========================
 * 1) 当前模式：后端优先 + mock 兜底
 *    - 先请求 /api/details/:type/:id
 *    - 请求失败时自动使用 getMockDetail，页面不会空白
 *
 * 2) 路由参数：
 *    - type: case | university
 *    - id:   列表卡片传来的主键 ID
 *
 * 3) 后端接通后，你们主要确认：
 *    - 接口地址与 API_BASE 是否一致
 *    - 返回数据字段是否匹配 normalizeDetail 支持的字段
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

const type = computed(() => String(route.params.type || 'case'))
const id = computed(() => String(route.params.id || ''))

const loading = ref(true)
const detailData = ref(null)

// 将后端的 stats 转为可展示对象：{ "GPA": "3.8", "IELTS": "7.0" }
const normalizeStats = (stats) => {
  if (!stats || typeof stats !== 'object' || Array.isArray(stats)) {
    return {}
  }
  return Object.entries(stats).reduce((acc, [key, value]) => {
    acc[String(key)] = value == null ? 'N/A' : String(value)
    return acc
  }, {})
}

const normalizeHighlights = (highlights) => {
  if (!Array.isArray(highlights)) return []
  return highlights.map((item) => String(item)).filter(Boolean)
}

/**
 * 后端详情字段 -> 页面展示字段 映射层
 * 推荐后端返回结构（统一）：
 * {
 *   title?: string,    // case 用
 *   name?: string,     // university 用
 *   subtitle?: string,
 *   major?: string,
 *   description?: string,
 *   stats?: Record<string, string | number>,
 *   highlights?: string[]
 * }
 *
 * 说明：
 * - case 和 university 顶部标题字段不同，所以按 type 分支处理
 * - 这里做容错后，模板层不需要知道后端字段细节
 */
const normalizeDetail = (payload, currentType) => {
  const safePayload = payload && typeof payload === 'object' ? payload : {}
  const base = {
    description: safePayload.description ? String(safePayload.description) : 'No description available yet.',
    stats: normalizeStats(safePayload.stats),
    highlights: normalizeHighlights(safePayload.highlights)
  }

  if (currentType === 'university') {
    return {
      ...base,
      name: safePayload.name ?? safePayload.title ?? 'Unknown University',
      subtitle: safePayload.subtitle ?? safePayload.location ?? 'N/A'
    }
  }

  return {
    ...base,
    title: safePayload.title ?? safePayload.name ?? 'Application Case',
    subtitle: safePayload.subtitle ?? safePayload.major ?? 'N/A',
    major: safePayload.major ?? safePayload.subtitle ?? 'N/A'
  }
}

// ===== mock 详情区（接口不可用时兜底）=====
// 后端未完成时，点击卡片也能看到结构完整的详情页
const getMockDetail = (currentType, currentId) => {
  if (currentType === 'university') {
    return {
      name: `University #${currentId || 'N/A'}`,
      subtitle: 'International Program Overview',
      description: 'This is fallback demo data while backend detail API is not ready. Once /api/details/university/:id is available, this card will render live database fields.',
      stats: {
        Country: 'N/A',
        Ranking: 'N/A',
        Tuition: 'N/A'
      },
      highlights: ['Supports direct backend mapping', 'Keeps current card-based UI', 'Ready for real detail payload']
    }
  }

  return {
    title: `Application Case #${currentId || 'N/A'}`,
    subtitle: 'Sample Offer Profile',
    major: 'Computer Science',
    description: 'This is fallback demo data while backend detail API is not ready. Once /api/details/case/:id is available, this page will show real application details.',
    stats: {
      GPA: '3.8/4.0',
      Language: 'IELTS 7.0',
      Offer: 'KTH'
    },
    highlights: ['Maintains the same visual sections', 'Compatible with real API schema', 'Works with sidebar card IDs']
  }
}

/**
 * 拉取详情主逻辑
 * 实际请求地址：
 * - /api/details/case/:id
 * - /api/details/university/:id
 */
const fetchDetailFromServer = async () => {
  loading.value = true
  detailData.value = null

  const endpoint = `${API_BASE}/api/details/${encodeURIComponent(type.value)}/${encodeURIComponent(id.value)}`

  try {
    const response = await fetch(endpoint)
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`)
    }
    const payload = await response.json()
    detailData.value = normalizeDetail(payload, type.value)
  } catch (error) {
    console.warn('Detail API unavailable, fallback to mock data.', error)
    detailData.value = getMockDetail(type.value, id.value)
  } finally {
    loading.value = false
  }
}

// 当用户在详情页内切换不同卡片时（路由参数变化），自动重新拉取
watch([type, id], fetchDetailFromServer, { immediate: true })
</script>
