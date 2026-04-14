<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans selection:bg-blue-200 pb-20">
    
    <nav class="flex items-center justify-between px-8 py-6 backdrop-blur-md bg-white/70 sticky top-0 z-50">
      <div class="text-xl font-bold tracking-tight">GradHelper Hub</div>
      <div class="space-x-6 text-sm font-medium text-gray-500 hidden md:block">
        <a href="#features" class="hover:text-black transition-colors">Features</a>
        <a href="#" class="hover:text-black transition-colors">My Profile</a>
      </div>
    </nav>

    <main class="flex flex-col items-center justify-center pt-24 pb-16 px-4 text-center">
      <h1 class="text-5xl md:text-6xl font-extrabold tracking-tighter mb-6 text-black">
        Your Exclusive <br>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">AI Admission Planner</span>
      </h1>
      <p class="text-lg text-gray-500 mb-10 max-w-2xl leading-relaxed">
        Input your background and goals. Let our RAG-enhanced AI map out your perfect postgraduate application strategy instantly.
      </p>

      <button @click="goToAI" class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-black rounded-full overflow-hidden transition-all hover:scale-105 hover:shadow-[0_10px_40px_rgba(0,0,0,0.3)]">
        <span>Launch AI Assistant</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </button>
    </main>

    <section id="features" class="max-w-6xl mx-auto px-6 py-12">
      <h2 class="text-2xl font-bold mb-8 tracking-tight">Explore More Modules</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer">
          <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mb-6 text-blue-600 font-bold">Aa</div>
          <h3 class="text-xl font-bold mb-3">IELTS Preparation</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Targeted guidance for Academic Writing Task 1 & 2. Master data analysis and high-scoring vocabulary.
          </p>
        </div>

        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer">
          <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-6 text-gray-700 font-bold">CV</div>
          <h3 class="text-xl font-bold mb-3">Resume Polishing</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Structure your academic and project experiences. Learn to highlight teamwork and technical execution precisely.
          </p>
        </div>

        <div class="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer">
          <div class="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center mb-6 text-green-600 font-bold">🏛</div>
          <h3 class="text-xl font-bold mb-3">RAG Knowledge Base</h3>
          <p class="text-gray-500 text-sm leading-relaxed">
            Explore our global university database to check minimum GPA requirements, prerequisites, and deadlines.
          </p>
        </div>

      </div>
    </section>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goToAI = () => {
  router.push('/chat')
}
</script>
