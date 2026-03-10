<script setup lang="ts">
import { PlaySquare, Settings, Compass, LayoutGrid, Languages } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

function toggleLanguage() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
}
</script>

<template>
  <aside class="w-16 h-screen fixed left-0 top-0 flex flex-col items-center py-6 border-r border-neutral-200/50 bg-white/50 backdrop-blur-sm z-50">
    <!-- Top Icons -->
    <div class="flex flex-col gap-6">
      <button :title="$t('sidebar.explore')" class="p-2 rounded-xl text-neutral-400 hover:text-neutral-800 hover:bg-neutral-100 transition-colors">
        <Compass :size="20" stroke-width="2" />
      </button>
      <button :title="$t('sidebar.chat')" class="p-2 rounded-xl text-neutral-800 bg-neutral-100 transition-colors">
        <LayoutGrid :size="20" stroke-width="2" />
      </button>
      <button :title="$t('sidebar.gallery')" class="p-2 rounded-xl text-neutral-400 hover:text-neutral-800 hover:bg-neutral-100 transition-colors">
        <PlaySquare :size="20" stroke-width="2" />
      </button>
    </div>
    
    <div class="mt-auto flex flex-col gap-4">
      <!-- Language Toggle -->
      <button 
        @click="toggleLanguage" 
        class="p-2 rounded-xl text-neutral-400 hover:text-neutral-800 hover:bg-neutral-100 transition-all flex flex-col items-center gap-0.5 group"
        title="Switch Language / 切换语言"
      >
        <Languages :size="20" stroke-width="2" />
        <span class="text-[9px] font-bold uppercase">{{ locale === 'zh' ? 'EN' : 'ZH' }}</span>
      </button>

      <button :title="$t('sidebar.settings')" class="p-2 rounded-xl text-neutral-400 hover:text-neutral-800 hover:bg-neutral-100 transition-colors">
        <Settings :size="20" stroke-width="2" />
      </button>
    </div>
  </aside>
</template>
