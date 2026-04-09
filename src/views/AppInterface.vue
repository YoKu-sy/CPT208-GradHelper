<script setup>
// 这里后续会引入路由和逻辑
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-blue-200">
    <nav class="flex items-center justify-between px-8 py-6 backdrop-blur-md bg-white/70 sticky top-0 z-50">
      <div class="text-xl font-bold tracking-tight">GradHelper AI</div>
      <div class="space-x-6 text-sm font-medium text-gray-500">
        <a href="#" class="hover:text-black transition-colors">首页</a>
        <a href="#features" class="hover:text-black transition-colors">功能探索</a>
        <a href="#" class="hover:text-black transition-colors">我的档案</a>
      </div>
    </nav>

    <main class="flex flex-col items-center justify-center pt-32 pb-24 px-4">
      <h1 class="text-5xl md:text-6xl font-extrabold tracking-tighter text-center mb-6">
        你的专属 AI 升学规划师
      </h1>
      <p class="text-lg text-gray-500 mb-10 text-center max-w-2xl">
        输入你的背景与目标，通过增强检索技术，瞬间匹配全球高校政策与录取标准。
      </p>

      <div class="w-full max-w-3xl relative group">
        <div class="absolute inset-0 bg-blue-500/10 rounded-3xl blur-xl group-hover:bg-blue-500/20 transition-all duration-500"></div>
        <div class="relative flex items-center bg-white shadow-sm hover:shadow-md transition-shadow duration-300 rounded-3xl p-2 border border-gray-100">
          <input 
            type="text" 
            placeholder="例如：查询 EIT Digital Master School 的申请要求及需要准备的材料..." 
            class="flex-1 bg-transparent px-6 py-4 outline-none text-lg text-gray-700 placeholder-gray-400"
          />
          <button class="bg-black text-white px-8 py-4 rounded-2xl font-medium hover:bg-gray-800 transition-colors">
            开始检索
          </button>
        </div>
      </div>
    </main>

    <section id="features" class="max-w-6xl mx-auto px-6 py-12">
      <h2 class="text-2xl font-bold mb-8 tracking-tight">更多升学模块</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer">
          <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mb-6 text-blue-600 font-bold">Aa</div>
          <h3 class="text-xl font-bold mb-3">雅思备考指导</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            针对性攻克 Academic Writing Task 1，掌握线形图、表格等复杂图表数据的分析与高分表达技巧。
          </p>
        </div>

        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer">
          <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-6 text-gray-700 font-bold">CV</div>
          <h3 class="text-xl font-bold mb-3">学术简历优化</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            结构化梳理你的工程项目经历，教你如何精准提炼团队协作能力与高效执行力。
          </p>
        </div>

        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer">
          <div class="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center mb-6 text-green-600 font-bold">🏛</div>
          <h3 class="text-xl font-bold mb-3">RAG 院校知识库</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            探索已接入的全球高校数据库，查看各专业的 GPA 底线、前置课程要求及 Deadline 时间轴。
          </p>
        </div>

      </div>
    </section>
  </div>
</template>
