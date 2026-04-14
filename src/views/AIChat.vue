<template>
  <div class="h-screen flex bg-white text-gray-800 font-sans overflow-hidden">
    <aside class="w-80 bg-gray-50 border-r border-gray-200 flex flex-col hidden lg:flex">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-bold tracking-tight">Success Stories</h2>
        <p class="text-xs text-gray-500 mt-1">Learn from past applicants</p>
      </div>
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div
          v-for="story in successStories"
          :key="story.id"
          @click="goToDetail('case', story.id)"
          class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all"
        >
          <div class="flex items-center justify-between mb-2">
            <span :class="['text-xs font-bold px-2 py-1 rounded', story.tagClass]">
              Offer: {{ story.offer }}
            </span>
            <span class="text-xs text-gray-400">{{ story.major }}</span>
          </div>
          <p class="text-sm font-medium">GPA: {{ story.gpa }} | {{ story.langTest }}</p>
          <p class="text-xs text-gray-500 mt-2">{{ story.experience }}</p>
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col bg-white relative">
      <header class="p-4 border-b border-gray-100 flex items-center">
        <button
          @click="router.push('/app')"
          class="text-gray-500 hover:text-black flex items-center text-sm font-medium transition-colors"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          Back to Hub
        </button>
      </header>

      <div class="flex-1 overflow-y-auto p-8 flex flex-col items-center">
        <div v-if="!isProfileSaved" class="w-full max-w-2xl bg-gray-50 rounded-3xl p-8 mb-8 border border-gray-100 shadow-inner">
          <h2 class="text-2xl font-bold mb-6 text-black">Complete Your Profile</h2>

          <div class="grid grid-cols-1 gap-6 mb-6">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Select Your Major</label>
              <div class="relative">
                <select
                  v-model="userProfile.major"
                  class="w-full px-4 py-4 rounded-2xl border border-gray-200 bg-white focus:ring-2 focus:ring-black outline-none appearance-none cursor-pointer transition-all text-gray-700"
                >
                  <option value="" disabled>Choose your major...</option>
                  <option v-for="major in satMajors" :key="major.en" :value="major.en">
                    {{ major.en }} ({{ major.zh }})
                  </option>
                </select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-400">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Current GPA</label>
                <input
                  v-model="userProfile.gpa"
                  type="text"
                  placeholder="e.g. 3.8/4.0"
                  class="w-full px-4 py-4 rounded-2xl border border-gray-200 bg-white focus:ring-2 focus:ring-black outline-none transition-all"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Keywords</label>
                <input
                  v-model="userProfile.keywords"
                  type="text"
                  placeholder="e.g. Robotics, AI Lab"
                  class="w-full px-4 py-4 rounded-2xl border border-gray-200 bg-white focus:ring-2 focus:ring-black outline-none transition-all"
                />
              </div>
            </div>
          </div>

          <button
            @click="saveProfileAndInitAI"
            :disabled="isSaving"
            class="w-full bg-black text-white py-4 rounded-2xl font-bold hover:bg-gray-800 transition-all flex justify-center items-center disabled:bg-gray-400"
          >
            <span v-if="!isSaving">Save Profile & Init AI</span>
            <span v-else>Processing...</span>
          </button>
        </div>

        <div class="w-full max-w-2xl space-y-6 opacity-50 pointer-events-none">
          <div class="flex items-start">
            <div class="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-white font-bold text-xs">AI</div>
            <div class="ml-4 bg-gray-100 rounded-2xl rounded-tl-none px-5 py-4 text-sm text-gray-700">
              Profile saved! How can I help you today?
            </div>
          </div>
        </div>
      </div>

      <div class="p-6 bg-white border-t border-gray-100">
        <div class="max-w-3xl mx-auto relative flex items-center">
          <input
            type="text"
            placeholder="Ask about specific university policies..."
            class="w-full bg-gray-100 px-6 py-4 rounded-full outline-none pr-16 focus:ring-2 focus:ring-blue-500 transition-all"
          />
          <button class="absolute right-2 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center hover:scale-105 transition-transform">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </div>
      </div>
    </main>

    <aside class="w-96 bg-zinc-50 border-l border-gray-200 overflow-y-auto hidden xl:block relative p-8">
      <h2 class="text-xl font-bold tracking-tight mb-12 sticky top-0 z-10 bg-zinc-50/90 backdrop-blur pb-4">Target Universities</h2>

      <div class="space-y-6 relative">
        <div
          v-for="uni in targetUniversities"
          :key="uni.id"
          @click="goToDetail('university', uni.id)"
          :class="['bg-white p-5 rounded-3xl shadow-sm border border-gray-100 w-64 hover:-translate-y-2 hover:shadow-xl transition-all cursor-pointer', uni.positionClass]"
        >
          <div :class="['h-10 w-10 text-white rounded-full flex items-center justify-center font-bold text-sm mb-3', uni.bgColor]">
            {{ uni.abbr }}
          </div>
          <h3 class="font-bold text-md leading-tight">{{ uni.name }}</h3>
          <p class="text-xs text-gray-500 mt-1">{{ uni.country }}</p>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
/**
 * =========================
 * AIChat 数据对接说明（给前后端同学）
 * =========================
 * 1) 现在这页是「后端优先，mock 兜底」模式：
 *    - 先请求后端接口拿真实数据
 *    - 请求失败 / 返回空数组时，自动使用本地 mock，保证页面可演示
 *
 * 2) 后端接通后，你们主要确认两点：
 *    - VITE_API_BASE_URL 是否配置正确（例如 http://localhost:8080）
 *    - 接口返回字段是否能被 normalizeStory / normalizeUniversity 映射到页面字段
 *
 * 3) 当前页面真实展示字段（卡片样式保持不变）：
 *    - success story 卡片：offer, major, gpa, langTest, experience
 *    - university 卡片：abbr, name, country
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

const TAG_CLASSES = ['bg-green-100 text-green-700', 'bg-blue-100 text-blue-700', 'bg-amber-100 text-amber-700']
const UNI_BG_CLASSES = ['bg-black', 'bg-red-600', 'bg-blue-600']
const UNI_POSITION_CLASSES = ['transform -translate-x-2', 'ml-auto transform translate-x-4', 'transform translate-x-2']

const successStories = ref([])
const targetUniversities = ref([])

// ===== mock 数据区（后端不可用时显示）=====
// 这里的数据会在接口失败时兜底显示，方便现在联调前演示 UI
const STORY_MOCK_DATA = [
  { id: 101, offer: 'KTH', major: 'CS', gpa: '3.6', langTest: 'IELTS 7.0', experience: '2 Internships', tagClass: 'bg-green-100 text-green-700' },
  { id: 102, offer: 'NUS', major: 'EE', gpa: '3.8', langTest: 'TOEFL 105', experience: 'National Scholarship', tagClass: 'bg-blue-100 text-blue-700' }
]

const UNIVERSITY_MOCK_DATA = [
  { id: 1, abbr: 'MIT', name: 'Mass. Institute of Tech', country: 'USA', bgColor: 'bg-black', positionClass: 'transform -translate-x-2' },
  { id: 2, abbr: 'ETH', name: 'ETH Zurich', country: 'Switzerland', bgColor: 'bg-red-600', positionClass: 'ml-auto transform translate-x-4' },
  { id: 3, abbr: 'ICL', name: 'Imperial College', country: 'UK', bgColor: 'bg-blue-600', positionClass: 'transform translate-x-2' }
]

/**
 * 后端字段 -> 前端卡片字段 映射层
 * 作用：
 * - 后端字段名和前端字段不完全一致时，不需要改模板
 * - 模板永远吃统一结构，降低联调成本
 *
 * 下面是当前兼容的常见别名示例：
 * - offer <- offer / offerSchool / schoolAbbr
 * - gpa <- gpa / GPA
 * - langTest <- langTest / languageTest / ielts / toefl
 */
const normalizeStory = (story, index) => ({
  id: story?.id ?? `story-${index + 1}`,
  offer: story?.offer ?? story?.offerSchool ?? story?.schoolAbbr ?? 'N/A',
  major: story?.major ?? story?.program ?? 'N/A',
  gpa: story?.gpa ?? story?.GPA ?? 'N/A',
  langTest: story?.langTest ?? story?.languageTest ?? story?.ielts ?? story?.toefl ?? 'N/A',
  experience: story?.experience ?? story?.background ?? 'N/A',
  tagClass: story?.tagClass ?? TAG_CLASSES[index % TAG_CLASSES.length]
})

const normalizeUniversity = (uni, index) => ({
  id: uni?.id ?? `uni-${index + 1}`,
  abbr: uni?.abbr ?? uni?.shortName ?? uni?.code ?? 'UNI',
  name: uni?.name ?? uni?.universityName ?? 'Unknown University',
  country: uni?.country ?? uni?.location ?? 'N/A',
  bgColor: uni?.bgColor ?? UNI_BG_CLASSES[index % UNI_BG_CLASSES.length],
  positionClass: uni?.positionClass ?? UNI_POSITION_CLASSES[index % UNI_POSITION_CLASSES.length]
})

// 通用 GET JSON：非 2xx 直接抛错，交给上层触发 mock 回退
const fetchJson = async (url) => {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`)
  }
  return response.json()
}

const fetchSidebarData = async () => {
  // 默认先放 mock，只有接口成功且有数据才会覆盖
  let stories = STORY_MOCK_DATA
  let universities = UNIVERSITY_MOCK_DATA

  // ===== 后端接口约定（建议）=====
  // GET /api/cases/latest          -> Case[]
  // GET /api/universities/featured -> University[]
  const [storiesResult, universitiesResult] = await Promise.allSettled([
    fetchJson(`${API_BASE}/api/cases/latest`),
    fetchJson(`${API_BASE}/api/universities/featured`)
  ])

  // stories 接口成功且返回非空数组 -> 用后端真实数据
  if (storiesResult.status === 'fulfilled' && Array.isArray(storiesResult.value) && storiesResult.value.length > 0) {
    stories = storiesResult.value
  }
  // universities 接口成功且返回非空数组 -> 用后端真实数据
  if (universitiesResult.status === 'fulfilled' && Array.isArray(universitiesResult.value) && universitiesResult.value.length > 0) {
    universities = universitiesResult.value
  }

  // 最终统一走映射层，保证模板字段稳定
  successStories.value = stories.map(normalizeStory)
  targetUniversities.value = universities.map(normalizeUniversity)
}

// 点击卡片进入详情：type 用于区分 case / university，id 用于查具体详情
const goToDetail = (type, id) => {
  router.push(`/detail/${type}/${id}`)
}

onMounted(fetchSidebarData)

const satMajors = [
  { en: 'Electrical Engineering and Automation', zh: '电气工程及其自动化' },
  { en: 'Electronic Science and Technology', zh: '电子科学与技术' },
  { en: 'Computer Science and Technology', zh: '计算机科学与技术' },
  { en: 'Mechatronics Engineering', zh: '机械电子工程' },
  { en: 'Artificial Intelligence', zh: '人工智能' },
  { en: 'Digital Media Technology', zh: '数字媒体技术' },
  { en: 'Telecommunications Engineering', zh: '通信工程' },
  { en: 'Information and Computing Science', zh: '信息与计算科学' }
]

const userProfile = ref({
  major: '',
  gpa: '',
  keywords: ''
})

const isSaving = ref(false)
const isProfileSaved = ref(false)

const saveProfileAndInitAI = async () => {
  if (!userProfile.value.major) return
  isSaving.value = true

  setTimeout(() => {
    isProfileSaved.value = true
    isSaving.value = false
    localStorage.setItem('grad_user_profile', JSON.stringify(userProfile.value))
  }, 1000)
}
</script>
