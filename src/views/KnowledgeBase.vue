<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// ==========================================
// 1. 导入旗帜图片
// 确保图片已经放在了 src/assets/flags/ 目录下
// ==========================================
import hkFlag from '../assets/flags/hk.png'
import ukFlag from '../assets/flags/uk.png'
import usaFlag from '../assets/flags/usa.png'
import euFlag from '../assets/flags/eu.png'
import ausFlag from '../assets/flags/aus.png'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

const searchQuery = ref('')
const selectedRegion = ref(null)
const isLoading = ref(false)
const universityList = ref([]) // 存放后端返回的院校数据
const router = useRouter()

// 将导入的图片绑定到地区数据中
const regionsData = [
  { id: 'hk', name: 'Hong Kong', icon: hkFlag },
  { id: 'uk', name: 'UK', icon: ukFlag },
  { id: 'usa', name: 'USA', icon: usaFlag },
  { id: 'eu', name: 'Europe', icon: euFlag },
  { id: 'aus', name: 'Australia', icon: ausFlag }
]

// ==========================================
// 2. 后端对接逻辑：按地区点击查询
// 给后端同学的说明：
// - 接口类型：GET 请求
// - 期望 URL 示例：/api/universities?region=hk
// - 跨域处理：请务必在 Spring Boot Controller 上加 @CrossOrigin 注解，否则前端会报 CORS 错误
// ==========================================
const handleRegionClick = async (regionId, regionName) => {
  selectedRegion.value = regionName
  isLoading.value = true
  universityList.value = [] // 切换地区时清空旧数据
  
  try {
        // 【对接修改点1】将这里的 URL 换成后端同学提供的真实服务器地址
    // 假设传给后端的参数名叫 region
    const response = await fetch(`${API_BASE}/api/universities?region=${regionId}`)
    
    if (!response.ok) throw new Error('Network response was not ok')
    
    // 【对接修改点2】解析后端返回的 JSON 数据
    // 假设后端返回格式为: { "code": 200, "data": [ { "id": 1, "name": "HKU", "gpaReq": "3.0" } ] }
    const result = await response.json()
    
    // 赋值给前端响应式变量
    universityList.value = result.data 
    
  } catch (error) {






        console.error("Failed to fetch region data:", error)
    // 启用了简单的 mock 数据，用于前端断网/未接通时的界面测试
    /* universityList.value = [
      { id: 1, name: `${regionName} University of Tech`, gpaRequirement: "3.5", description: `Mock program info for ${regionName}. Waiting for real backend integration.` },
      { id: 2, name: `${regionName} National College`, gpaRequirement: "3.2", description: "Sample detailed requirements will be populated from DB." }
    ] */
  } finally {
    isLoading.value = false
  }
}

// ==========================================
// 3. 后端对接逻辑：顶部搜索框模糊查询/RAG检索
// 给后端同学的说明：
// - 接口类型：POST 请求 (因为可能要传大段文本进行 RAG 处理)
// - 期望 URL 示例：/api/rag/search
// - Request Body：JSON 格式，例如 { "query": "Oxford" }
// - 返回类型：与上方按地区查询的返回格式保持一致即可
// ==========================================
const handleSearch = async () => {
  if (!searchQuery.value) return
  
  isLoading.value = true
  selectedRegion.value = null // 搜索时清除下方的地区高亮
  universityList.value = []
  
    try {
    // 【对接修改点3】将这里的 URL 换成后端的 RAG 搜索接口地址
    const response = await fetch(`${API_BASE}/api/rag/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json' // 告诉后端我们传的是 JSON
      },
      // 将前端输入框的值打包成 JSON 发给后端
      body: JSON.stringify({ 
        query: searchQuery.value 
      })
    })
    
    if (!response.ok) throw new Error('Search request failed')
      
    const result = await response.json()
    universityList.value = result.data
    
  } catch (error) {





        console.error("Search failed:", error)
    // 启用了搜索功能的 mock 数据
    /* universityList.value = [
      { id: 101, name: "Search Result University", gpaRequirement: "3.8", description: `This is a simulated RAG search result for "${searchQuery.value}". Backend is not connected yet.` }
    ] */
  } finally {
    isLoading.value = false
  }
}

const handleUniversitySelect = (universityId) => {
  router.push(`/detail/university/${universityId}`)
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans p-8 pt-24 animate-fade-in">
    <div class="max-w-6xl mx-auto flex flex-col items-center">
      <button @click="$router.back()" class="self-start mb-8 text-sm text-gray-400 hover:text-black transition-colors">
        ← Back to Dashboard
      </button>

      <h1 class="text-4xl font-extrabold tracking-tight mb-4">University Database</h1>
      <p class="text-gray-500 mb-12 text-center">Search by institution name or explore via regional categories.</p>

      <div class="w-full max-w-2xl mb-16 relative">
        <input 
          v-model="searchQuery"
          @keyup.enter="handleSearch"
          type="text" 
          placeholder="Search for universities, e.g., 'University of Oxford'..." 
          class="w-full bg-white px-8 py-5 rounded-3xl shadow-sm border border-gray-100 outline-none focus:border-blue-400 focus:shadow-[0_0_15px_rgba(59,130,246,0.15)] transition-all duration-300 text-lg"
        />
        <button @click="handleSearch" class="absolute right-4 top-4 bg-black text-white px-6 py-2 rounded-2xl hover:bg-gray-800 transition-colors">
          Search
        </button>
      </div>

      <div class="w-full">
        <h2 class="text-xl font-bold mb-8 text-center">Select a Region</h2>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-8">
          <div 
            v-for="region in regionsData" 
            :key="region.id"
            class="flex flex-col items-center group cursor-pointer"
            @click="handleRegionClick(region.id, region.name)"
          >
            <div 
              class="w-28 h-28 mb-4 rounded-full p-1 border-2 flex items-center justify-center overflow-hidden transition-all duration-500"
              :class="selectedRegion === region.name ? 'border-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.3)]' : 'border-transparent bg-white shadow-sm group-hover:border-blue-200 group-hover:-translate-y-2'"
            >
               <img :src="region.icon" :alt="region.name" class="w-full h-full object-cover rounded-full" />
            </div>
            <span class="font-medium transition-colors" :class="selectedRegion === region.name ? 'text-blue-600 font-bold' : 'text-gray-600 group-hover:text-blue-500'">
              {{ region.name }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="mt-16 w-full max-w-4xl animate-fade-in-up min-h-[200px]">
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-12 text-blue-500">
          <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mb-4"></div>
          <p class="font-medium">Connecting to Database...</p>
        </div>

        <div v-else-if="universityList.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="uni in universityList"
            :key="uni.id"
            @click="handleUniversitySelect(uni.id)"
            class="p-8 bg-white rounded-3xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
          >
            <h3 class="text-2xl font-bold mb-2">{{ uni.name || 'University Name' }}</h3>
            <div class="inline-block bg-blue-50 text-blue-600 px-3 py-1 rounded-full text-sm font-bold mb-4">
              GPA Req: {{ uni.gpaRequirement || uni.gpaReq || 'N/A' }}
            </div>
            <p class="text-gray-500 text-sm leading-relaxed">
              {{ uni.description || 'Detailed program information retrieved from RAG database will be displayed here.' }}
            </p>
          </div>
        </div>

        <div v-else class="p-12 border-2 border-dashed border-gray-200 rounded-3xl text-center text-gray-400">
          <p v-if="selectedRegion">No results found for <span class="text-black font-bold">{{ selectedRegion }}</span>.</p>
          <p v-else>Select a region or use the search bar to explore universities.</p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.8s ease-out forwards; }
.animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>

