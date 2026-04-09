<template>
  <div class="min-h-screen bg-black text-white font-sans selection:bg-blue-500 scroll-smooth">
    
    <header class="min-h-screen flex flex-col justify-start items-center text-center pt-20 pb-12 px-6 relative bg-cover bg-center bg-no-repeat" 
            style="/* background-image: url('/bg-hero.jpg'); */">
      
      <div class="max-w-4xl mx-auto space-y-6 animate-fade-in-up relative z-10 w-full">
        <div class="inline-block px-4 py-1.5 rounded-full border border-gray-700 text-sm font-medium text-gray-400 tracking-wide uppercase mb-2 bg-black/50 backdrop-blur-sm">
          CPT208 Student Project
        </div>
        <h1>
        </h1>
        <h1 class="text-5xl md:text-7xl font-extrabold tracking-tighter text-white">
          GradHelper AI.
        </h1>
        <p class="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
          Bridging the information gap in postgraduate applications through Retrieval-Augmented Generation (RAG).
        </p>
      </div>

      <div class="w-full max-w-6xl mx-auto mt-16 relative z-10 animate-fade-in-up" style="animation-delay: 0.2s;">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 px-4">
          
          <div class="flex flex-col items-center group">
            <div class="w-24 h-24 rounded-full overflow-hidden border-2 border-gray-800 group-hover:border-white transition-all duration-300 mb-4 shadow-lg group-hover:shadow-white/20">
              <img src="/avatar1.jpg" alt="Member" class="w-full h-full object-cover" onerror="this.src='https://api.dicebear.com/7.x/avataaars/svg?seed=Tsubasa'" />
            </div>
            <h3 class="text-lg font-bold text-white">Tsubasa</h3>
            <p class="text-xs text-gray-500 mb-3 font-mono">ID: 123456</p>
            <p class="text-sm text-gray-400 text-center leading-snug">
              Frontend UI/UX & <br> API Integration
            </p>
          </div>

          <div class="flex flex-col items-center group">
            <div class="w-24 h-24 rounded-full overflow-hidden border-2 border-gray-800 group-hover:border-white transition-all duration-300 mb-4 shadow-lg group-hover:shadow-white/20">
              <img src="/avatar2.jpg" alt="Member" class="w-full h-full object-cover" onerror="this.src='https://api.dicebear.com/7.x/avataaars/svg?seed=Alex'" />
            </div>
            <h3 class="text-lg font-bold text-white">Member 2</h3>
            <p class="text-xs text-gray-500 mb-3 font-mono">ID: 1234568</p>
            <p class="text-sm text-gray-400 text-center leading-snug">
              Backend Logic & <br> Database
            </p>
          </div>

          <div class="flex flex-col items-center group">
            <div class="w-24 h-24 rounded-full overflow-hidden border-2 border-gray-800 group-hover:border-white transition-all duration-300 mb-4 shadow-lg group-hover:shadow-white/20">
              <img src="/avatar3.jpg" alt="Member" class="w-full h-full object-cover" onerror="this.src='https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah'" />
            </div>
            <h3 class="text-lg font-bold text-white">Member 3</h3>
            <p class="text-xs text-gray-500 mb-3 font-mono">ID: 1234569</p>
            <p class="text-sm text-gray-400 text-center leading-snug">
              RAG Model & <br> Prompt Engineering
            </p>
          </div>

          <div class="flex flex-col items-center group">
            <div class="w-24 h-24 rounded-full overflow-hidden border-2 border-gray-800 group-hover:border-white transition-all duration-300 mb-4 shadow-lg group-hover:shadow-white/20">
              <img src="/avatar4.jpg" alt="Member" class="w-full h-full object-cover" onerror="this.src='https://api.dicebear.com/7.x/avataaars/svg?seed=Mike'" />
            </div>
            <h3 class="text-lg font-bold text-white">Member 4</h3>
            <p class="text-xs text-gray-500 mb-3 font-mono">ID: 1234570</p>
            <p class="text-sm text-gray-400 text-center leading-snug">
              Data Crawling & <br> Documentation
            </p>
          </div>

        </div>
      </div>

      <a href="#about" class="absolute bottom-8 flex flex-col items-center text-gray-600 hover:text-white transition-colors duration-300 animate-bounce z-10">
        <span class="text-xs font-medium mb-2 uppercase tracking-widest">Discover</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </a>
    </header>

    <section id="about" class="py-32 px-6 bg-zinc-950">
      <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
        <div class="space-y-6">
          <h2 class="text-4xl font-bold tracking-tight text-white">The Problem We Solve.</h2>
          <p class="text-lg text-gray-400 leading-relaxed">
            Navigating global university requirements, GPA thresholds, and document preparation is overwhelming. Information is scattered, outdated, and often confusing for prospective applicants.
          </p>
        </div>
        <div class="space-y-6">
          <h2 class="text-4xl font-bold tracking-tight text-white">Our Solution.</h2>
          <p class="text-lg text-gray-400 leading-relaxed">
            We built an intelligent search engine powered by LLMs and a custom RAG architecture. It instantly retrieves precise admission policies from targeted institutions, offering a personalized roadmap for your academic future.
          </p>
        </div>
      </div>
    </section>

    <section class="py-32 px-6 bg-black text-white flex flex-col items-center justify-center text-center border-t border-zinc-900">
      <h2 class="text-5xl md:text-7xl font-bold tracking-tight mb-8">Ready to explore?</h2>
      <p class="text-xl text-gray-400 mb-12 max-w-xl">
        Experience the GradHelper AI interface and start your postgraduate application journey.
      </p>
      
      <button @click="goToApp" class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-black bg-white rounded-full overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_40px_rgba(255,255,255,0.3)]">
        <span>Launch Our Project</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
      </button>
    </section>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToApp = () => {
  router.push('/app')
}
</script>

<style scoped>
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fadeInUp 1s ease-out forwards;
}
</style>