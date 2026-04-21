<template>
  <div class="neo-page h-screen flex text-gray-800 font-sans overflow-hidden">
    <div class="neo-glow h-64 w-64 bg-blue-300/70 -left-16 top-24"></div>
    <div class="neo-glow h-72 w-72 bg-cyan-300/60 right-0 top-20"></div>

    <aside class="w-80 bg-white/70 backdrop-blur-sm border-r border-gray-200 flex flex-col hidden lg:flex relative z-10">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-bold tracking-tight">Success Stories</h2>
        <p class="text-xs text-gray-500 mt-1">Learn from past applicants</p>
      </div>
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div
          v-for="story in successStories"
          :key="story.id"
          @click="goToDetail('case', story.id)"
          class="neo-card neo-medium p-4 rounded-2xl cursor-pointer"
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

    <main class="flex-1 flex flex-col bg-white/75 backdrop-blur-[2px] relative z-10">
      <header class="p-4 border-b border-gray-100 flex items-center">
        <button
          @click="router.push('/app')"
          class="text-gray-500 hover:text-black flex items-center text-sm font-medium neo-soft"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          Back to Hub
        </button>
      </header>

      <div ref="chatScrollEl" class="flex-1 overflow-y-auto p-8 flex flex-col items-center">
        <div v-if="!isProfileSaved" class="w-full max-w-2xl neo-card rounded-3xl p-8 mb-8">
          <h2 class="text-2xl font-bold mb-6 text-black">Complete Your Profile</h2>

          <div class="grid grid-cols-1 gap-6 mb-6">
            <div>
              <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Select Your Major</label>
              <div class="relative">
                <select
                  v-model="userProfile.major"
                  class="w-full px-4 py-4 rounded-2xl border border-gray-200 bg-white focus:ring-2 focus:ring-black outline-none appearance-none cursor-pointer neo-soft text-gray-700"
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
                  class="w-full px-4 py-4 rounded-2xl border border-gray-200 bg-white focus:ring-2 focus:ring-black outline-none neo-soft"
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Keywords</label>
                <input
                  v-model="userProfile.keywords"
                  type="text"
                  placeholder="e.g. Robotics, AI Lab"
                  class="w-full px-4 py-4 rounded-2xl border border-gray-200 bg-white focus:ring-2 focus:ring-black outline-none neo-soft"
                />
              </div>
            </div>
          </div>

          <button
            @click="saveProfileAndInitAI"
            :disabled="isSaving"
            class="w-full bg-black text-white py-4 rounded-2xl font-bold hover:bg-gray-800 neo-medium flex justify-center items-center disabled:bg-gray-400"
          >
            <span v-if="!isSaving">Save Profile & Init AI</span>
            <span v-else>Initializing AI...</span>
          </button>
        </div>

        <div v-if="isProfileSaved" class="w-full max-w-2xl space-y-6 pb-10">
          <div
            v-for="(msg, index) in chatMessages"
            :key="index"
            :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
          >
            <div v-if="msg.role === 'ai'" class="flex items-start max-w-[85%]">
              <div class="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-white font-bold text-xs shadow-sm">AI</div>
              <div class="ml-4 neo-card rounded-2xl rounded-tl-none px-5 py-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {{ msg.content }}
                <span v-if="msg.typing" class="inline-block w-2 h-4 ml-1 align-middle bg-gray-500 animate-pulse"></span>
              </div>
            </div>

            <div v-else class="flex items-start max-w-[85%] flex-row-reverse">
              <div class="w-8 h-8 rounded-full bg-black flex-shrink-0 flex items-center justify-center text-white font-bold text-xs shadow-sm">U</div>
              <div class="mr-4 bg-blue-50 text-blue-900 border border-blue-100 rounded-2xl rounded-tr-none px-5 py-4 text-sm whitespace-pre-wrap leading-relaxed neo-soft">
                {{ msg.content }}
              </div>
            </div>
          </div>

          <div v-if="isSendingMsg" class="flex items-start max-w-[85%]">
            <div class="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-white font-bold text-xs">AI</div>
            <div class="ml-4 neo-card rounded-2xl rounded-tl-none px-5 py-4 text-sm text-gray-500 animate-pulse">
              AI is typing...
            </div>
          </div>
        </div>
      </div>

      <div class="p-6 bg-white/85 border-t border-gray-100">
        <div class="max-w-3xl mx-auto relative flex items-center">
          <input
            v-model="userInput"
            @keyup.enter="sendMessage"
            :disabled="!isProfileSaved || isSendingMsg"
            type="text"
            placeholder="Ask about specific university policies..."
            class="w-full bg-gray-100 px-6 py-4 rounded-full outline-none pr-16 focus:ring-2 focus:ring-blue-500 neo-soft disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            @click="sendMessage"
            :disabled="!isProfileSaved || isSendingMsg"
            class="absolute right-2 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center hover:scale-105 neo-medium disabled:opacity-50 disabled:hover:scale-100"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </div>
      </div>
    </main>

    <aside class="w-96 bg-white/70 backdrop-blur-sm border-l border-gray-200 overflow-y-auto hidden xl:block relative p-8 z-10">
      <h2 class="text-xl font-bold tracking-tight mb-12 sticky top-0 z-10 bg-white/85 backdrop-blur pb-4">Target Universities</h2>
      <div class="space-y-6 relative">
        <div
          v-for="uni in targetUniversities"
          :key="uni.id"
          @click="goToDetail('university', uni.id)"
          :class="['neo-card neo-strong p-5 rounded-3xl w-64 cursor-pointer', uni.positionClass]"
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
import { nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
const TYPE_SPEED_MS = 18

const TAG_CLASSES = ['bg-green-100 text-green-700', 'bg-blue-100 text-blue-700', 'bg-amber-100 text-amber-700']
const UNI_BG_CLASSES = ['bg-black', 'bg-red-600', 'bg-blue-600']
const UNI_POSITION_CLASSES = ['transform -translate-x-2', 'ml-auto transform translate-x-4', 'transform translate-x-2']

const successStories = ref([])
const targetUniversities = ref([])
const chatScrollEl = ref(null)

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

const userProfile = ref({ major: '', gpa: '', keywords: '' })
const isSaving = ref(false)
const isProfileSaved = ref(false)
const chatMessages = ref([])
const userInput = ref('')
const isSendingMsg = ref(false)

const STORY_MOCK_DATA = [
  { id: 101, offer: 'KTH', major: 'CS', gpa: '3.6', langTest: 'IELTS 7.0', experience: '2 Internships' },
  { id: 102, offer: 'NUS', major: 'EE', gpa: '3.8', langTest: 'TOEFL 105', experience: 'National Scholarship' }
]

const UNIVERSITY_MOCK_DATA = [
  { id: 1, abbr: 'MIT', name: 'Mass. Institute of Tech', country: 'USA' },
  { id: 2, abbr: 'ETH', name: 'ETH Zurich', country: 'Switzerland' },
  { id: 3, abbr: 'ICL', name: 'Imperial College', country: 'UK' }
]

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const scrollToBottom = async () => {
  await nextTick()
  if (chatScrollEl.value) {
    chatScrollEl.value.scrollTop = chatScrollEl.value.scrollHeight
  }
}

const appendAiMessageWithTyping = async (fullText) => {
  const msg = { role: 'ai', content: '', typing: true }
  chatMessages.value.push(msg)
  await scrollToBottom()

  for (const ch of String(fullText || '')) {
    msg.content += ch
    await sleep(TYPE_SPEED_MS)
    await scrollToBottom()
  }

  msg.typing = false
}

const saveProfileAndInitAI = async () => {
  if (!userProfile.value.major) return
  isSaving.value = true

  let reply = `Profile saved! Based on your ${userProfile.value.gpa || 'current'} GPA, I recommend focusing on top schools in HK and UK. How can I help you?`

  try {
    const res = await fetch(`${API_BASE}/api/chat/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userProfile.value)
    })
    if (!res.ok) throw new Error('Init failed')

    const result = await res.json()
    reply = result?.data?.reply || reply
  } catch (error) {
    console.warn('Backend not ready, using fallback', error)
  } finally {
    isProfileSaved.value = true
    isSaving.value = false
    localStorage.setItem('grad_user_profile', JSON.stringify(userProfile.value))
  }

  await appendAiMessageWithTyping(reply)
  await scrollToBottom()
}

const sendMessage = async () => {
  const text = userInput.value.trim()
  if (!text || !isProfileSaved.value || isSendingMsg.value) return

  chatMessages.value.push({ role: 'user', content: text, typing: false })
  userInput.value = ''
  isSendingMsg.value = true
  await scrollToBottom()

  let reply = 'Backend error: Could not reach the AI brain.'

  try {
    const history = chatMessages.value.slice(0, -1).map((item) => ({
      role: item.role,
      content: item.content
    }))

    const res = await fetch(`${API_BASE}/api/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history })
    })
    if (!res.ok) throw new Error('Chat API failed')

    const result = await res.json()
    reply = result?.data?.reply || 'No response.'
  } catch (error) {
    console.warn('Chat API error', error)
  }

  await appendAiMessageWithTyping(reply)
  isSendingMsg.value = false
  await scrollToBottom()
}

const normalizeStory = (story, index) => ({
  id: story?.id ?? `story-${index + 1}`,
  offer: story?.offer ?? story?.offerSchool ?? 'N/A',
  major: story?.major ?? 'N/A',
  gpa: story?.gpa ?? 'N/A',
  langTest: story?.langTest ?? 'N/A',
  experience: story?.experience ?? 'N/A',
  tagClass: TAG_CLASSES[index % TAG_CLASSES.length]
})

const normalizeUniversity = (uni, index) => ({
  id: uni?.id ?? `uni-${index + 1}`,
  abbr: uni?.abbr ?? 'UNI',
  name: uni?.name ?? 'Unknown',
  country: uni?.country ?? 'N/A',
  bgColor: UNI_BG_CLASSES[index % UNI_BG_CLASSES.length],
  positionClass: UNI_POSITION_CLASSES[index % UNI_POSITION_CLASSES.length]
})

const fetchSidebarData = async () => {
  let stories = STORY_MOCK_DATA
  let universities = UNIVERSITY_MOCK_DATA

  try {
    const [storiesRes, unisRes] = await Promise.allSettled([
      fetch(`${API_BASE}/api/cases/latest`).then((r) => (r.ok ? r.json() : Promise.reject())),
      fetch(`${API_BASE}/api/universities/featured`).then((r) => (r.ok ? r.json() : Promise.reject()))
    ])

    if (storiesRes.status === 'fulfilled' && Array.isArray(storiesRes.value) && storiesRes.value.length > 0) {
      stories = storiesRes.value
    }
    if (unisRes.status === 'fulfilled' && Array.isArray(unisRes.value) && unisRes.value.length > 0) {
      universities = unisRes.value
    }
  } catch (e) {
    console.warn('API connection failed, using mock sidebars')
  }

  successStories.value = stories.map(normalizeStory)
  targetUniversities.value = universities.map(normalizeUniversity)
}

const goToDetail = (type, id) => router.push(`/detail/${type}/${id}`)

onMounted(fetchSidebarData)
</script>
