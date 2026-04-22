<template>
  <div class="min-h-screen bg-slate-50 px-6 py-10 text-slate-900">
    <div class="mx-auto max-w-5xl">
      <button
        @click="$router.push('/app')"
        class="mb-8 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
      >
        <span>Back to Hub</span>
      </button>

      <div class="grid gap-8 lg:grid-cols-[380px_minmax(0,1fr)]">
        <section class="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <p class="text-xs font-semibold uppercase tracking-[0.3em] text-sky-600">Profile Search</p>
          <h1 class="mt-3 text-3xl font-bold tracking-tight">Offer Query Test Page</h1>
          <p class="mt-4 text-sm leading-6 text-slate-500">
            Input `major`, `gpa`, and `additional info`, then submit to the AI assistant backend.
          </p>

          <form class="mt-8 space-y-5" @submit.prevent="handleSearch">
            <div>
              <label for="major" class="mb-2 block text-sm font-semibold text-slate-700">Major</label>
              <input
                id="major"
                v-model.trim="searchForm.major"
                type="text"
                list="major-options"
                placeholder="Computer Science and Technology"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-400 focus:bg-white"
              />
              <datalist id="major-options">
                <option v-for="major in majorOptions" :key="major" :value="major"></option>
              </datalist>
              <p class="mt-2 text-xs text-slate-400">
                Suggested values: choose one of the known majors to avoid empty results caused by spelling differences.
              </p>
            </div>

            <div>
              <label for="gpa" class="mb-2 block text-sm font-semibold text-slate-700">GPA</label>
              <input
                id="gpa"
                v-model.trim="searchForm.gpa"
                type="text"
                placeholder="3.6 or 85/100"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-400 focus:bg-white"
              />
            </div>

            <div>
              <label for="extra" class="mb-2 block text-sm font-semibold text-slate-700">Additional Info</label>
              <textarea
                id="extra"
                v-model.trim="searchForm.additional_info"
                rows="5"
                placeholder="Research, internships, labs, competitions, target direction..."
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-sky-400 focus:bg-white"
              ></textarea>
            </div>

            <button
              type="submit"
              :disabled="isLoading"
              class="w-full rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {{ isLoading ? 'Searching...' : 'Search Offers' }}
            </button>
          </form>

          <div class="mt-6 rounded-2xl bg-slate-100 p-4 text-sm text-slate-600">
            <p>API: <span class="font-mono text-xs">{{ apiBaseUrl }}/profile/search</span></p>
            <p class="mt-2">Returned records are rendered on the right as cards.</p>
          </div>
        </section>

        <section class="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-600">Results</p>
              <h2 class="mt-2 text-2xl font-bold tracking-tight">Search Output</h2>
            </div>
            <div class="rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-600">
              {{ hasSearched ? `${resultCount} records` : 'No search yet' }}
            </div>
          </div>

          <div v-if="error" class="mt-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {{ error }}
          </div>

          <div v-else-if="isLoading" class="mt-8 flex min-h-[280px] items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-slate-50">
            <div class="text-center">
              <div class="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-sky-200 border-t-sky-600"></div>
              <p class="mt-4 text-sm font-medium text-slate-500">Querying backend data...</p>
            </div>
          </div>

          <div v-else-if="!hasSearched" class="mt-8 flex min-h-[280px] items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-slate-50 px-6 text-center text-sm text-slate-500">
            Fill in the form on the left and submit. Matching offers will appear here.
          </div>

          <div v-else-if="results.length === 0" class="mt-8 flex min-h-[280px] items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-slate-50 px-6 text-center text-sm text-slate-500">
            No matching offers were found. Try adjusting the major or GPA range.
          </div>

          <div v-else class="mt-8 grid gap-5 md:grid-cols-2">
            <article
              v-for="(item, index) in results"
              :key="`${item.offer || 'offer'}-${index}`"
              class="rounded-3xl border border-slate-200 bg-slate-50 p-5 transition hover:-translate-y-1 hover:bg-white hover:shadow-md"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <h3 class="text-lg font-bold text-slate-900">{{ item.offer || 'Unknown Offer' }}</h3>
                  <p class="mt-1 text-sm text-slate-500">{{ item.major || 'Unknown Major' }}</p>
                </div>
                <span :class="statusClass(item.status)">
                  {{ item.status || 'Unknown' }}
                </span>
              </div>

              <div class="mt-5 grid grid-cols-2 gap-3 text-sm text-slate-600">
                <div class="rounded-2xl bg-white p-3">
                  <p class="text-xs uppercase tracking-wide text-slate-400">GPA</p>
                  <p class="mt-1 font-semibold text-slate-900">{{ item.gpa || 'N/A' }}</p>
                </div>
                <div class="rounded-2xl bg-white p-3">
                  <p class="text-xs uppercase tracking-wide text-slate-400">Research</p>
                  <p class="mt-1 font-semibold text-slate-900">{{ formatCount(item.research) }}</p>
                </div>
                <div class="rounded-2xl bg-white p-3">
                  <p class="text-xs uppercase tracking-wide text-slate-400">Internship</p>
                  <p class="mt-1 font-semibold text-slate-900">{{ formatCount(item.internship) }}</p>
                </div>
                <div class="rounded-2xl bg-white p-3">
                  <p class="text-xs uppercase tracking-wide text-slate-400">Notes</p>
                  <p class="mt-1 line-clamp-2 font-semibold text-slate-900">{{ item.additional_notes || 'None' }}</p>
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const apiBaseUrl = import.meta.env.VITE_AI_API_BASE_URL || 'http://127.0.0.1:8001'

const searchForm = reactive({
  major: '',
  gpa: '',
  additional_info: ''
})

const majorOptions = [
  'Artificial Intelligence',
  'Computer Science and Technology',
  'Digital Media Technology',
  'Electrical Engineering and Automation',
  'Information and Computing Science',
  'Mechatronics Engineering',
  'Telecommunications Engineering'
]

const results = ref([])
const resultCount = ref(0)
const isLoading = ref(false)
const error = ref('')
const hasSearched = ref(false)

const formatCount = (value) => {
  if (value === null || value === undefined || value === '') {
    return '0'
  }
  return String(value)
}

const statusClass = (status) => {
  const normalized = String(status || '').toLowerCase()
  if (normalized.includes('admit') || normalized.includes('offer')) {
    return 'rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700'
  }
  if (normalized.includes('reject')) {
    return 'rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700'
  }
  if (normalized.includes('wait')) {
    return 'rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700'
  }
  return 'rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-700'
}

const handleSearch = async () => {
  if (!searchForm.major || !searchForm.gpa) {
    error.value = 'Major and GPA are required.'
    hasSearched.value = false
    return
  }

  isLoading.value = true
  error.value = ''
  hasSearched.value = true

  try {
    const response = await fetch(`${apiBaseUrl}/profile/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        major: searchForm.major,
        gpa: searchForm.gpa,
        additional_info: searchForm.additional_info
      })
    })

    if (!response.ok) {
      const message = await response.text().catch(() => '')
      throw new Error(message || `Request failed with status ${response.status}`)
    }

    const data = await response.json()
    results.value = Array.isArray(data.results) ? data.results : []
    resultCount.value = Number(data.count || results.value.length)
  } catch (err) {
    console.error(err)
    results.value = []
    resultCount.value = 0
    error.value = err instanceof Error ? err.message : 'Search failed.'
  } finally {
    isLoading.value = false
  }
}
</script>
