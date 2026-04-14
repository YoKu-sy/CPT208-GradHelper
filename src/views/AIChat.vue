<template>
  <div class="h-screen flex bg-white text-gray-800 font-sans overflow-hidden">
    
    <aside class="w-80 bg-gray-50 border-r border-gray-200 flex flex-col hidden lg:flex">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-bold tracking-tight">Success Stories</h2>
        <p class="text-xs text-gray-500 mt-1">Learn from past applicants</p>
      </div>
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 cursor-pointer hover:border-blue-300 transition-colors">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold bg-green-100 text-green-700 px-2 py-1 rounded">Offer: KTH</span>
            <span class="text-xs text-gray-400">CS Major</span>
          </div>
          <p class="text-sm font-medium">GPA: 3.6 | IELTS: 7.0</p>
          <p class="text-xs text-gray-500 mt-2">2 Internships, 1 Paper</p>
        </div>
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 cursor-pointer hover:border-blue-300 transition-colors">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-1 rounded">Offer: NUS</span>
            <span class="text-xs text-gray-400">EE Major</span>
          </div>
          <p class="text-sm font-medium">GPA: 3.8 | TOEFL: 105</p>
          <p class="text-xs text-gray-500 mt-2">National Scholarship</p>
        </div>
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 cursor-pointer hover:border-blue-300 transition-colors">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold bg-purple-100 text-purple-700 px-2 py-1 rounded">Offer: UCL</span>
            <span class="text-xs text-gray-400">Business</span>
          </div>
          <p class="text-sm font-medium">GPA: 3.5 | IELTS: 7.5</p>
          <p class="text-xs text-gray-500 mt-2">Big 4 Internship</p>
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col bg-white relative">
      <header class="p-4 border-b border-gray-100 flex items-center">
        <button @click="router.push('/app')" class="text-gray-500 hover:text-black flex items-center text-sm font-medium transition-colors">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          Back to Hub
        </button>
      </header>

      <div class="flex-1 overflow-y-auto p-8 flex flex-col items-center">
        
<div v-if="!isProfileSaved" class="w-full max-w-2xl bg-gray-50 rounded-3xl p-8 mb-8 border border-gray-100 shadow-inner">
  <h2 class="text-2xl font-bold mb-6 text-black">Complete Your SAT Profile</h2>
  
  <div class="grid grid-cols-1 gap-6 mb-6">
    <div>
      <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-wider">Select Your Major</label>
      <div class="relative">
        <select 
          v-model="userProfile.major"
          class="w-full px-4 py-4 rounded-2xl border border-gray-200 bg-white focus:ring-2 focus:ring-black outline-none appearance-none cursor-pointer transition-all text-gray-700"
        >
          <option value="" disabled>Choose your major from SAT...</option>
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
              Profile saved! Based on your 3.8 GPA in CS, I recommend looking at KTH and EIT Digital. What specific requirements would you like to check?
            </div>
          </div>
        </div>

      </div>

      <div class="p-6 bg-white border-t border-gray-100">
        <div class="max-w-3xl mx-auto relative flex items-center">
          <input type="text" placeholder="Ask about specific university policies or requirements..." class="w-full bg-gray-100 px-6 py-4 rounded-full outline-none pr-16 focus:ring-2 focus:ring-blue-500 transition-all" />
          <button class="absolute right-2 w-10 h-10 bg-black text-white rounded-full flex items-center justify-center hover:scale-105 transition-transform">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
          </button>
        </div>
      </div>
    </main>

    <aside class="w-96 bg-zinc-50 border-l border-gray-200 overflow-y-auto hidden xl:block relative p-8">
      <h2 class="text-xl font-bold tracking-tight mb-12 sticky top-0 z-10 bg-zinc-50/90 backdrop-blur pb-4">Target Universities</h2>
      
      <div class="space-y-6 relative">
        
        <div class="bg-white p-5 rounded-3xl shadow-sm border border-gray-100 w-64 transform -translate-x-2 hover:-translate-y-2 hover:shadow-xl transition-all cursor-pointer">
          <div class="h-10 w-10 bg-black text-white rounded-full flex items-center justify-center font-bold text-sm mb-3">MIT</div>
          <h3 class="font-bold text-md leading-tight">Mass. Institute of Tech</h3>
          <p class="text-xs text-gray-500 mt-1">USA</p>
        </div>

        <div class="bg-white p-5 rounded-3xl shadow-sm border border-gray-100 w-64 ml-auto transform translate-x-4 hover:-translate-y-2 hover:shadow-xl transition-all cursor-pointer">
          <div class="h-10 w-10 bg-red-600 text-white rounded-full flex items-center justify-center font-bold text-sm mb-3">ETH</div>
          <h3 class="font-bold text-md leading-tight">ETH Zurich</h3>
          <p class="text-xs text-gray-500 mt-1">Switzerland</p>
        </div>

        <div class="bg-white p-5 rounded-3xl shadow-sm border border-gray-100 w-64 transform translate-x-2 hover:-translate-y-2 hover:shadow-xl transition-all cursor-pointer">
          <div class="h-10 w-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm mb-3">ICL</div>
          <h3 class="font-bold text-md leading-tight">Imperial College</h3>
          <p class="text-xs text-gray-500 mt-1">UK</p>
        </div>

         <div class="bg-white p-5 rounded-3xl shadow-sm border border-gray-100 w-64 ml-auto transform translate-x-6 -translate-y-4 hover:-translate-y-6 hover:shadow-xl transition-all cursor-pointer">
          <div class="h-10 w-10 bg-yellow-500 text-white rounded-full flex items-center justify-center font-bold text-sm mb-3">NUS</div>
          <h3 class="font-bold text-md leading-tight">Nat. Univ of Singapore</h3>
          <p class="text-xs text-gray-500 mt-1">Singapore</p>
        </div>
      </div>
    </aside>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 定义 SAT 学院的专业列表（包含中英文对照，Value 为英文方便后端处理）
const satMajors = [
  { en: "Electrical Engineering and Automation", zh: "电气工程及其自动化" },
  { en: "Electronic Science and Technology", zh: "电子科学与技术" },
  { en: "Computer Science and Technology", zh: "计算机科学与技术" },
  { en: "Mechatronics Engineering", zh: "机械电子工程" },
  { en: "Artificial Intelligence", zh: "人工智能" },
  { en: "Digital Media Technology", zh: "数字媒体技术" },
  { en: "Telecommunications Engineering", zh: "通信工程" },
  { en: "Information and Computing Science", zh: "信息与计算科学" }
]

// 存储用户输入的档案数据
const userProfile = ref({
  major: '',
  gpa: '',
  keywords: ''
})

const isSaving = ref(false)
const isProfileSaved = ref(false)

// 核心功能：保存数据并准备对接后端
const saveProfileAndInitAI = async () => {
  if (!userProfile.value.major) {
    alert('Please select your major.')
    return
  }

  isSaving.value = true

  // 【准备传给后端的数据包】
  // 这里就是你以后对接后端 API 时需要发送的内容
  const payload = {
    major: userProfile.value.major,
    gpa: userProfile.value.gpa,
    background: userProfile.value.keywords,
    timestamp: new Date().toISOString()
  }

  console.log("准备发送给后端的数据包:", payload)

  // 模拟请求成功后的逻辑（后续只需将此处替换为 axios.post 或 fetch）
  try {
    // 假设此处是真实的 API 调用：await api.post('/init-session', payload)
    isProfileSaved.value = true
    // 将档案保存在本地，防止刷新页面丢失数据
    localStorage.setItem('grad_user_profile', JSON.stringify(userProfile.value))
  } catch (error) {
    console.error("Initialization failed:", error)
  } finally {
    isSaving.value = false
  }
}
</script>