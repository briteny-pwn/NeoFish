<script setup lang="ts">
import { ref } from 'vue'
import { Plus, ArrowUp, FileText, Globe, X, File, Image, FileVideo, FileAudio } from 'lucide-vue-next'

const props = defineProps<{
  minimal?: boolean
}>()

const query = ref('')
const pendingImages = ref<string[]>([])  // base64 data-URLs for images (for vision)
const pendingFiles = ref<{ name: string; data: string; type: string }[]>([])  // other files
const fileInputRef = ref<HTMLInputElement | null>(null)
const emit = defineEmits<{
  (e: 'submit', payload: { text: string; images: string[]; files: { name: string; data: string; type: string }[] }): void
}>()

// ── File picker ──────────────────────────────────────────────────────────────
function openFilePicker() {
  fileInputRef.value?.click()
}

function onFilesSelected(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files) return
  Array.from(files).forEach(readFile)
  // reset so the same file can be re-selected
  ;(e.target as HTMLInputElement).value = ''
}

function readFile(file: File) {
  const reader = new FileReader()
  reader.onload = () => {
    if (typeof reader.result === 'string') {
      if (file.type.startsWith('image/')) {
        // Images go to pendingImages for vision
        pendingImages.value.push(reader.result)
      } else {
        // Other files go to pendingFiles
        pendingFiles.value.push({
          name: file.name,
          data: reader.result,
          type: file.type || 'application/octet-stream',
        })
      }
    }
  }
  reader.readAsDataURL(file)
}

// ── Clipboard paste ──────────────────────────────────────────────────────────
function onPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  for (const item of Array.from(items)) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) readFile(file)
    }
  }
}

function removeImage(idx: number) {
  pendingImages.value.splice(idx, 1)
}

function removeFile(idx: number) {
  pendingFiles.value.splice(idx, 1)
}

function getFileIcon(type: string) {
  if (type.startsWith('image/')) return Image
  if (type.startsWith('video/')) return FileVideo
  if (type.startsWith('audio/')) return FileAudio
  return File
}

function formatFileSize(dataUrl: string): string {
  // Estimate size from base64 (rough approximation)
  const base64Length = dataUrl.length - dataUrl.indexOf(',') - 1
  const bytes = Math.round(base64Length * 0.75)
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// ── Submit ───────────────────────────────────────────────────────────────────
function handleSubmit(e?: Event) {
  if (e instanceof KeyboardEvent && e.isComposing) return
  const hasText = query.value.trim().length > 0
  const hasImages = pendingImages.value.length > 0
  const hasFiles = pendingFiles.value.length > 0
  if (!hasText && !hasImages && !hasFiles) return

  emit('submit', {
    text: query.value.trim(),
    images: [...pendingImages.value],
    files: [...pendingFiles.value],
  })
  query.value = ''
  pendingImages.value = []
  pendingFiles.value = []
}
</script>

<template>
  <div class="flex flex-col items-center justify-center w-full max-w-3xl mx-auto px-4" :class="{ 'h-full': !minimal }">
    <!-- Centered prominent text in serif -->
    <h1 v-if="!minimal" class="font-serif text-4xl md:text-5xl lg:text-6xl text-neutral-800 mb-12 tracking-wide font-medium">
      {{ $t('landing.hero_title') }}
    </h1>

    <!-- Image previews -->
    <div v-if="pendingImages.length > 0 || pendingFiles.length > 0" class="w-full max-w-2xl mb-2 flex flex-wrap gap-2 px-2">
      <!-- Image thumbnails -->
      <div
        v-for="(src, idx) in pendingImages"
        :key="'img-' + idx"
        class="relative group w-16 h-16 rounded-xl overflow-hidden border border-neutral-200 shadow-sm flex-shrink-0"
      >
        <img :src="src" class="w-full h-full object-cover" alt="attached image" />
        <button
          @click="removeImage(idx)"
          class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
        >
          <X :size="16" class="text-white" />
        </button>
      </div>

      <!-- File thumbnails -->
      <div
        v-for="(file, idx) in pendingFiles"
        :key="'file-' + idx"
        class="relative group w-auto min-w-16 h-16 px-3 rounded-xl overflow-hidden border border-neutral-200 shadow-sm flex-shrink-0 flex items-center gap-2 bg-neutral-50"
      >
        <component :is="getFileIcon(file.type)" :size="20" class="text-neutral-500" />
        <div class="flex flex-col overflow-hidden">
          <span class="text-xs font-medium text-neutral-700 truncate max-w-32">{{ file.name }}</span>
          <span class="text-[10px] text-neutral-400">{{ formatFileSize(file.data) }}</span>
        </div>
        <button
          @click="removeFile(idx)"
          class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <X :size="12" />
        </button>
      </div>
    </div>

    <!-- Floating Input Box -->
    <div
      class="relative w-full max-w-2xl bg-white rounded-3xl shadow-soft p-2 flex items-center transition-all duration-300 focus-within:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.1)] border border-neutral-100"
      :class="(pendingImages.length > 0 || pendingFiles.length > 0) ? 'rounded-t-xl' : ''"
    >
      <!-- Hidden file input -->
      <input
        ref="fileInputRef"
        type="file"
        multiple
        class="hidden"
        @change="onFilesSelected"
      />

      <!-- Attach button -->
      <button
        @click="openFilePicker"
        :title="$t('input.attach_file')"
        class="p-3 text-neutral-400 hover:text-neutral-700 transition-colors rounded-full hover:bg-neutral-50 ml-1 relative"
        :class="(pendingImages.length > 0 || pendingFiles.length > 0) ? 'text-blue-500' : ''"
      >
        <Plus :size="22" stroke-width="2" />
        <span
          v-if="pendingImages.length > 0 || pendingFiles.length > 0"
          class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-blue-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center"
        >{{ pendingImages.length + pendingFiles.length }}</span>
      </button>

      <input
        v-model="query"
        @keydown.enter="handleSubmit"
        @paste="onPaste"
        type="text"
        class="flex-1 bg-transparent border-none outline-none px-4 py-3 text-lg text-neutral-800 placeholder:text-neutral-400 font-sans"
        :placeholder="$t('landing.input_placeholder')"
      />

      <button
        @click="handleSubmit"
        class="p-3 rounded-2xl transition-colors min-w-[48px] flex items-center justify-center mr-1"
        :class="(query.trim() || pendingImages.length > 0 || pendingFiles.length > 0) ? 'bg-black text-white hover:bg-neutral-800' : 'bg-neutral-100 text-neutral-400'"
      >
        <ArrowUp :size="20" stroke-width="3" />
      </button>
    </div>

    <!-- Suggestion Cards -->
    <div v-if="!minimal" class="flex gap-4 mt-8 w-full max-w-2xl px-2">
      <button class="flex items-center gap-2 px-4 py-2.5 rounded-full bg-white/60 hover:bg-white border border-neutral-200/50 text-neutral-600 text-sm font-medium transition-all shadow-sm">
        <FileText :size="16" class="text-orange-400" />
        {{ $t('landing.suggest_ppt') }}
      </button>
      <button class="flex items-center gap-2 px-4 py-2.5 rounded-full bg-white/60 hover:bg-white border border-neutral-200/50 text-neutral-600 text-sm font-medium transition-all shadow-sm">
        <Globe :size="16" class="text-blue-400" />
        {{ $t('landing.suggest_analyze') }}
      </button>
    </div>
  </div>
</template>