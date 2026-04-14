<script setup>
import { ref } from 'vue'

const year1 = ref(null)
const year2 = ref(null)
const year3 = ref(null)
const gpaResult = ref(null)

const calculateGPA = () => {
  if (year1.value && year2.value && year3.value) {
    // 简单的本地平均换算逻辑：(Y1+Y2+Y3)/3 / 100 * 4
    const average = (parseFloat(year1.value) + parseFloat(year2.value) + parseFloat(year3.value)) / 3
    gpaResult.value = (average / 100 * 4.0).toFixed(2)
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans flex flex-col items-center pt-32 px-4 animate-fade-in">
    <button @click="$router.back()" class="mb-8 text-sm text-gray-400 hover:text-black transition-colors">
      ← Back to Dashboard
    </button>
    
    <h1 class="text-4xl md:text-5xl font-extrabold tracking-tighter mb-6 text-center">
      GPA Calculator
    </h1>
    <p class="text-gray-500 mb-10 text-center max-w-md">
      Enter your percentage scores for the first three academic years.
    </p>

    <div class="w-full max-w-md relative group">
      <div class="absolute inset-0 bg-blue-500/10 rounded-3xl blur-xl group-hover:bg-blue-500/20 transition-all duration-700"></div>
      
      <div class="relative bg-white shadow-sm rounded-3xl p-8 border border-gray-100 space-y-6">
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 ml-1">Year 1 Score (%)</label>
          <input 
            v-model="year1"
            type="number" 
            placeholder="e.g. 80.5" 
            class="w-full bg-gray-50 px-6 py-4 rounded-2xl outline-none text-lg text-gray-700 border border-gray-100 focus:border-blue-400 focus:shadow-[0_0_15px_rgba(59,130,246,0.15)] transition-all duration-300"
          />
        </div>
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 ml-1">Year 2 Score (%)</label>
          <input 
            v-model="year2"
            type="number" 
            placeholder="e.g. 78.0" 
            class="w-full bg-gray-50 px-6 py-4 rounded-2xl outline-none text-lg text-gray-700 border border-gray-100 focus:border-blue-400 focus:shadow-[0_0_15px_rgba(59,130,246,0.15)] transition-all duration-300"
          />
        </div>
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 ml-1">Year 3 Score (%)</label>
          <input 
            v-model="year3"
            type="number" 
            placeholder="e.g. 85.0" 
            class="w-full bg-gray-50 px-6 py-4 rounded-2xl outline-none text-lg text-gray-700 border border-gray-100 focus:border-blue-400 focus:shadow-[0_0_15px_rgba(59,130,246,0.15)] transition-all duration-300"
          />
        </div>

        <button @click="calculateGPA" class="w-full bg-black text-white px-8 py-4 rounded-2xl font-medium hover:bg-gray-800 transition-colors duration-300">
          Calculate Now
        </button>

        <div v-if="gpaResult" class="mt-8 p-6 bg-blue-50 rounded-2xl text-center animate-fade-in-up">
          <p class="text-gray-500 mb-1 text-sm font-medium">Estimated GPA</p>
          <p class="text-5xl font-black text-blue-600 tracking-tighter">{{ gpaResult }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}
.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>