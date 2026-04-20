<template>
  <div class="neo-page min-h-screen text-gray-900 font-sans selection:bg-blue-200 pb-20">
    <div class="neo-glow h-56 w-56 bg-blue-300/80 -left-20 top-24"></div>
    <div class="neo-glow h-64 w-64 bg-cyan-300/70 right-8 top-40"></div>

    <nav class="flex items-center justify-between px-8 py-6 backdrop-blur-md bg-white/75 sticky top-0 z-50 border-b border-white/60">
      <div class="text-xl font-bold tracking-tight">GradHelper Hub</div>
      <div class="space-x-6 text-sm font-medium text-gray-500 hidden md:block">
        <a href="#features" class="hover:text-black neo-soft">Features</a>
        <a href="#chat-modules" class="hover:text-black neo-soft">Chat Modules</a>
        <a
          href="https://github.com/YoKu-sy/CPT208-GradHelper.git"
          target="_blank"
          rel="noopener noreferrer"
          class="hover:text-black neo-soft"
        >
          GitHub Repo
        </a>
      </div>
    </nav>

    <main class="flex flex-col items-center justify-center pt-24 pb-16 px-4 text-center relative z-10">
      <h1 class="text-5xl md:text-6xl font-extrabold tracking-tighter mb-6 text-black">
        Your Exclusive <br>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">AI Admission Planner</span>
      </h1>
      <p class="text-lg text-gray-500 mb-10 max-w-2xl leading-relaxed">
        Input your background and goals. Let our RAG-enhanced AI map out your perfect postgraduate application strategy instantly.
      </p>

      <div class="flex flex-col sm:flex-row gap-4">
        <button
          @click="goToAI"
          class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-black rounded-full overflow-hidden neo-medium hover:scale-105 hover:shadow-[0_10px_40px_rgba(0,0,0,0.3)]"
        >
          <span>Launch AI Assistant</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2 group-hover:translate-x-1 neo-soft" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </button>

        <button
          @click="goToIelts"
          class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-sky-600 rounded-full overflow-hidden neo-medium hover:scale-105 hover:shadow-[0_10px_40px_rgba(14,165,233,0.35)]"
        >
          <span>Launch IELTS Assistant</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2 group-hover:translate-x-1 neo-soft" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </button>
      </div>
    </main>

    <section id="chat-modules" class="max-w-6xl mx-auto px-6 py-12 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div @click="goToAI" class="neo-card neo-strong group p-8 rounded-3xl cursor-pointer">
          <div class="w-12 h-12 bg-blue-50 group-hover:bg-blue-100 neo-medium rounded-full flex items-center justify-center mb-6 text-blue-600 font-bold">
            AI
          </div>
          <h3 class="text-xl font-bold mb-3">升学助手</h3>
          <p class="text-gray-500 text-sm leading-relaxed mb-5">
            点击进入原来的升学问答对话页，继续使用你原本的聊天逻辑。
          </p>
          <p class="text-xs uppercase tracking-[0.15em] text-blue-500 font-semibold">Open Chat</p>
        </div>

        <div @click="goToIelts" class="neo-card neo-strong group p-8 rounded-3xl cursor-pointer">
          <div class="w-12 h-12 bg-sky-50 group-hover:bg-sky-100 neo-medium rounded-full flex items-center justify-center mb-6 text-sky-600 font-bold">
            IEL
          </div>
          <h3 class="text-xl font-bold mb-3">雅思备考助手</h3>
          <p class="text-gray-500 text-sm leading-relaxed mb-5">
            点击进入雅思备考问答页面，和独立的 session 对话流程继续交流。
          </p>
          <p class="text-xs uppercase tracking-[0.15em] text-sky-500 font-semibold">Open Chat</p>
        </div>
      </div>
    </section>

    <section id="features" class="max-w-6xl mx-auto px-6 py-12 relative z-10">
      <h2 class="text-2xl font-bold mb-8 tracking-tight">Explore More Modules</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div @click="$router.push('/gpa')" class="neo-card neo-strong group p-8 rounded-3xl cursor-pointer">
          <div class="w-12 h-12 bg-blue-50 group-hover:bg-blue-100 neo-medium rounded-full flex items-center justify-center mb-6 text-blue-600 font-bold">
            100
          </div>
          <h3 class="text-xl font-bold mb-3">GPA Conversion</h3>
          <p class="text-gray-500 text-sm leading-relaxed mb-5">
            Enter your current percentage score and we will instantly convert it to the standard GPA, providing you with precise data for your college application.
          </p>
          <p class="text-xs uppercase tracking-[0.15em] text-blue-500 font-semibold">Fast Calculator</p>
        </div>

        <div class="neo-card neo-strong p-8 rounded-3xl cursor-pointer">
          <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-6 text-gray-700 font-bold">CV</div>
          <h3 class="text-xl font-bold mb-3">Resume Polishing</h3>
          <p class="text-gray-500 text-sm leading-relaxed mb-5">
            Structure your academic and project experiences. Learn to highlight teamwork and technical execution precisely.
          </p>
          <p class="text-xs uppercase tracking-[0.15em] text-gray-500 font-semibold">Coming Next</p>
        </div>

        <div @click="$router.push('/knowledge')" class="neo-card neo-strong group p-8 rounded-3xl cursor-pointer">
          <div class="w-12 h-12 bg-green-50 group-hover:bg-green-100 neo-medium rounded-full flex items-center justify-center mb-6 text-green-600 font-bold">UNI</div>
          <h3 class="text-xl font-bold mb-3">University Database</h3>
          <p class="text-gray-500 text-sm leading-relaxed mb-5">
            Explore regional requirements, GPA thresholds, and prerequisite courses for global top institutions.
          </p>
          <p class="text-xs uppercase tracking-[0.15em] text-emerald-500 font-semibold">RAG Search</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import AIChat from './AIChat.vue'
import IeltsAssistant from './IeltsAssistant.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const goToIelts = () => {
  router.push('/ielts')
}

const goToAI = () => {
  router.push('/chat')
}
</script>
