<script setup lang="ts">
import { ref } from 'vue'
import { PlaySquare, Settings, Compass, LayoutGrid, Languages, Bug } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import ChatHistoryPanel from './ChatHistoryPanel.vue'
import { useDebugMode } from '../composables/useDebugMode'

const { locale } = useI18n()
const { debugMode, toggleDebug } = useDebugMode()
const emit = defineEmits<{
  (e: 'new-chat'): void
  (e: 'select-chat', id: string): void
}>()

const historyOpen = ref(false)
const panelWidth = 'clamp(12rem, 52vw, 17rem)'

function toggleHistory() {
  historyOpen.value = !historyOpen.value
}

function toggleLanguage() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
}

function handleNewChat() {
  emit('new-chat')
}

function handleSelectChat(id: string) {
  emit('select-chat', id)
}
</script>

<template>
  <aside class="relative z-20 flex h-screen flex-shrink-0">
    <div class="flex h-full border-r border-neutral-200/60 bg-white/60 backdrop-blur-xl shadow-[0_28px_60px_-42px_rgba(15,23,42,0.4)]">
      <div class="flex h-full w-16 flex-col items-center py-6">
        <div class="flex flex-col gap-6">
          <button :title="$t('sidebar.explore')" class="rounded-xl p-2 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-800">
            <Compass :size="20" stroke-width="2" />
          </button>
          <button
            :title="$t('sidebar.chat')"
            @click="toggleHistory"
            class="rounded-xl p-2 transition-all duration-300"
            :class="historyOpen ? 'bg-neutral-900 text-white shadow-md shadow-neutral-900/15' : 'text-neutral-400 hover:bg-neutral-100 hover:text-neutral-800'"
          >
            <LayoutGrid :size="20" stroke-width="2" />
          </button>
          <button :title="$t('sidebar.gallery')" class="rounded-xl p-2 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-800">
            <PlaySquare :size="20" stroke-width="2" />
          </button>
        </div>

        <div class="mt-auto flex flex-col gap-4">
          <button
            @click="toggleLanguage"
            class="flex flex-col items-center gap-0.5 rounded-xl p-2 text-neutral-400 transition-all hover:bg-neutral-100 hover:text-neutral-800"
            title="Switch Language / 切换语言"
          >
            <Languages :size="20" stroke-width="2" />
            <span class="text-[9px] font-bold uppercase">{{ locale === 'zh' ? 'EN' : 'ZH' }}</span>
          </button>

          <button
            @click="toggleDebug"
            class="rounded-xl p-2 transition-all"
            :class="debugMode ? 'bg-amber-50 text-amber-600' : 'text-neutral-400 hover:bg-neutral-100 hover:text-neutral-800'"
            :title="debugMode ? $t('sidebar.debug_on') : $t('sidebar.debug_off')"
          >
            <Bug :size="20" stroke-width="2" />
          </button>

          <button :title="$t('sidebar.settings')" class="rounded-xl p-2 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-800">
            <Settings :size="20" stroke-width="2" />
          </button>
        </div>
      </div>

      <div
        class="relative h-full overflow-hidden transition-[width,opacity] duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
        :class="historyOpen ? 'opacity-100' : 'opacity-0'"
        :style="{ width: historyOpen ? panelWidth : '0px' }"
      >
        <div
          class="flex h-full flex-col border-l border-neutral-200/50 bg-white/88 backdrop-blur-xl shadow-[inset_1px_0_0_rgba(255,255,255,0.75)]"
          :style="{ width: panelWidth }"
        >
          <ChatHistoryPanel
            @new-chat="handleNewChat"
            @select="handleSelectChat"
          />
        </div>
      </div>
    </div>
  </aside>
</template>
