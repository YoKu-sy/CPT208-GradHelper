<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50 text-slate-900">
    <header class="sticky top-0 z-20 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 md:px-8">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.25em] text-sky-600">IELTS Assistant Hub</p>
          <h1 class="text-lg font-bold md:text-xl">Your One-Stop IELTS Prep Assistant</h1>
        </div>
        <button
          class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:text-slate-950"
          @click="goBack"
        >
          Back to Home
        </button>
      </div>
    </header>

    <main class="mx-auto grid max-w-7xl gap-8 px-5 py-8 md:px-8 lg:grid-cols-[1fr_1.2fr] lg:py-12">
      <section class="space-y-6 rounded-[2rem] border border-slate-200 bg-white/80 p-6 shadow-[0_20px_80px_rgba(15,23,42,0.08)] backdrop-blur xl:p-8">
        <div class="space-y-3">
          <span class="inline-flex rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-700">Study smarter, not harder</span>
          <h2 class="text-3xl font-black tracking-tight md:text-4xl">From Listening to Writing, your dedicated IELTS study partner.</h2>
          <p class="max-w-xl text-sm leading-6 text-slate-600 md:text-base">
            Ask about question types, techniques, vocabulary, speaking templates, or writing feedback. Press Enter to send. I'll keep you company while you wait for a reply.
          </p>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">What to ask</p>
            <p class="mt-2 text-sm text-slate-700">Listening question types, reading passage location, common speaking topics, writing structure, study plans.</p>
          </div>
        </div>

        <div class="rounded-[1.5rem] bg-slate-950 p-5 text-white shadow-lg">
          <p class="text-xs font-semibold uppercase tracking-[0.25em] text-sky-300">Example Questions</p>
          <div class="mt-4 space-y-3 text-sm leading-6 text-slate-200">
            <p>"What are the common listening question types?"</p>
            <p>"What's the usual format for Part 1?"</p>
          </div>
        </div>
      </section>

      <section class="flex min-h-[70vh] flex-col rounded-[2rem] border border-slate-200 bg-white/90 shadow-[0_20px_80px_rgba(15,23,42,0.1)] overflow-hidden">
        <div class="border-b border-slate-200 px-5 py-4 md:px-6">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-sky-500 to-cyan-400 text-sm font-black text-white shadow-lg shadow-sky-200">
              IELTS
            </div>
            <div>
              <p class="font-semibold">IELTS AI Assistant</p>
            </div>
          </div>
        </div>

        <div ref="chatPanelRef" class="flex-1 overflow-y-auto px-4 py-5 md:px-6">
          <div class="space-y-4">
            <div class="flex max-w-[88%] gap-3">
              <div class="mt-1 flex h-9 w-9 flex-none items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">AI</div>
              <div class="rounded-3xl rounded-tl-md bg-slate-100 px-4 py-3 text-sm leading-6 text-slate-700 shadow-sm">
                Hello! I'm your IELTS prep assistant. Where should we start? Listening, Reading, Writing, or Speaking?
              </div>
            </div>

            <template v-for="(message, index) in messages" :key="index">
              <div v-if="message.role === 'user'" class="flex justify-end">
                <div class="max-w-[88%] rounded-3xl rounded-tr-md bg-sky-600 px-4 py-3 text-sm leading-6 text-white shadow-lg shadow-sky-200">
                  {{ message.content }}
                </div>
              </div>
              <div v-else class="flex max-w-[88%] gap-3">
                <div class="mt-1 flex h-9 w-9 flex-none items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">AI</div>
                <div class="rounded-3xl rounded-tl-md bg-slate-100 px-4 py-3 text-sm leading-6 text-slate-700 shadow-sm whitespace-pre-wrap">
                  {{ message.content }}
                </div>
              </div>
            </template>

            <div v-if="isWaiting" class="flex max-w-[88%] gap-3">
              <div class="mt-1 flex h-9 w-9 flex-none items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">AI</div>
              <div class="rounded-3xl rounded-tl-md bg-slate-100 px-4 py-3 text-sm leading-6 text-slate-700 shadow-sm">
                <div class="flex items-center gap-2">
                  <span>Looking through my notes</span>
                  <span class="inline-flex gap-1">
                    <span class="h-2 w-2 animate-bounce rounded-full bg-sky-500 [animation-delay:-0.2s]"></span>
                    <span class="h-2 w-2 animate-bounce rounded-full bg-sky-500 [animation-delay:-0.1s]"></span>
                    <span class="h-2 w-2 animate-bounce rounded-full bg-sky-500"></span>
                  </span>
                </div>
                <p class="mt-2 text-xs text-slate-500">The assistant is thinking hard to give you the best answer.</p>
              </div>
            </div>
          </div>
        </div>

        <form class="border-t border-slate-200 bg-white px-4 py-4 md:px-6" @submit.prevent="sendQuestion">
          <div class="flex items-end gap-3 rounded-[1.4rem] border border-slate-200 bg-slate-50 p-3">
            <textarea
              v-model="question"
              rows="1"
              @keydown.enter.exact.prevent="sendQuestion"
              @keydown.enter.shift.stop
              placeholder="Type your IELTS question and press Enter to send..."
              class="min-h-[48px] max-h-40 flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-6 outline-none placeholder:text-slate-400"
              :disabled="isWaiting"
            ></textarea>
            <button
              type="submit"
              class="inline-flex h-12 items-center justify-center rounded-full bg-slate-950 px-5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              :disabled="isWaiting || !question.trim()"
            >
              Send
            </button>
          </div>
          <p class="mt-3 text-xs text-slate-500">The first question doesn't require a session_id. It will be handled automatically.</p>
        </form>
      </section>
    </main>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/ielts-api'

const chatPanelRef = ref(null)
const question = ref('')
const sessionId = ref('')
const isWaiting = ref(false)
const messages = ref([])

const goBack = () => router.push('/app')

const scrollToBottom = async () => {
  await nextTick()
  if (chatPanelRef.value) {
    chatPanelRef.value.scrollTop = chatPanelRef.value.scrollHeight
  }
}

const sendQuestion = async () => {
  const content = question.value.trim()
  if (!content || isWaiting.value) return

  messages.value.push({ role: 'user', content })
  question.value = ''
  isWaiting.value = true
  await scrollToBottom()

  try {
    const payload = { question: content }
    if (sessionId.value) payload.session_id = sessionId.value

    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!res.ok) throw new Error(`Request failed: ${res.status}`)

    const data = await res.json()
    sessionId.value = data.session_id || sessionId.value
    messages.value.push({ role: 'ai', content: data.reply || "Sorry, I couldn't get a response. Please try again later." })
  } catch (error) {
    messages.value.push({
      role: 'ai',
      content: 'Oops, I got a bit lost looking for that. Please check if the backend address is correct and try again.'
    })
    console.error(error)
  } finally {
    isWaiting.value = false
    await scrollToBottom()
  }
}
</script>
