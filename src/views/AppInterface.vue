<template>
  <div class="neo-page min-h-screen text-gray-900 font-sans selection:bg-blue-200 pb-20">
    <div class="neo-glow h-56 w-56 bg-blue-300/80 -left-20 top-24"></div>
    <div class="neo-glow h-64 w-64 bg-cyan-300/70 right-8 top-40"></div>

    <nav class="flex items-center justify-between px-8 py-6 backdrop-blur-md bg-white/75 sticky top-0 z-50 border-b border-white/60">
      <div class="text-xl font-bold tracking-tight">GradHelper Hub</div>
      <div class="space-x-6 text-sm font-medium text-gray-500 hidden md:block">
        <a href="#features" class="hover:text-black neo-soft">Features</a>
        <a href="#" class="hover:text-black neo-soft">My Profile</a>
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
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">GradHelper Planner</span>
      </h1>
      <p class="text-lg text-gray-500 mb-10 max-w-2xl leading-relaxed">
        Explore the modules below for GPA conversion, IELTS support, and university database lookup.
      </p>
    </main>

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

        <div @click="$router.push('/ielts')" class="neo-card neo-strong group p-8 rounded-3xl cursor-pointer">
          <div class="w-12 h-12 bg-rose-50 group-hover:bg-rose-100 neo-medium rounded-full flex items-center justify-center mb-6 text-rose-600 font-bold">
            IELTS
          </div>
          <h3 class="text-xl font-bold mb-3">IELTS Supplementary Learning</h3>
          <p class="text-gray-500 text-sm leading-relaxed mb-5">
            Facing complex long and difficult sentences? Just paste the text and you will get an accurate translation driven by DeepL, which will help you speed up your reading comprehension.
          </p>
          <p class="text-xs uppercase tracking-[0.15em] text-rose-500 font-semibold">DeepL API</p>
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


