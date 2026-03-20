<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronDown, ChevronRight, Brain } from 'lucide-vue-next'

interface Step {
  type: 'thinking' | 'tool'
  content: string
  completed: boolean
}

const props = defineProps<{
  steps: Step[]
  isActive: boolean
}>()

const { t } = useI18n()
const expanded = ref(false)

const currentStep = computed(() => {
  if (props.steps.length === 0) return null
  return props.steps[props.steps.length - 1]
})

const completedCount = computed(() => {
  return props.steps.filter(s => s.completed).length
})

const summaryText = computed(() => {
  if (props.isActive && currentStep.value) {
    return currentStep.value.content
  }
  return t('thinking.completed', { count: completedCount.value })
})

function toggle() {
  expanded.value = !expanded.value
}
</script>

<template>
  <div class="thinking-chain bg-neutral-50 border border-neutral-200/60 rounded-xl overflow-hidden">
    <button
      @click="toggle"
      class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-neutral-100/50 transition-colors"
    >
      <div class="w-6 h-6 rounded-full bg-neutral-900 flex-shrink-0 flex items-center justify-center">
        <Brain :size="14" class="text-white" />
      </div>
      
      <span class="flex-1 text-sm text-neutral-600 truncate">
        {{ summaryText }}
      </span>
      
      <span v-if="!isActive" class="text-xs text-neutral-400 mr-2">
        {{ completedCount }} {{ $t('thinking.steps') }}
      </span>
      
      <ChevronRight v-if="!expanded" :size="16" class="text-neutral-400" />
      <ChevronDown v-else :size="16" class="text-neutral-400" />
    </button>
    
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      leave-active-class="transition-all duration-150 ease-in"
      enter-from-class="opacity-0 max-h-0"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="expanded" class="border-t border-neutral-200/60 overflow-hidden" style="max-height: 400px;">
        <div class="px-4 py-3 space-y-2">
          <div
            v-for="(step, idx) in steps"
            :key="idx"
            class="flex items-center gap-2 text-sm"
            :class="step.completed ? 'text-neutral-500' : 'text-neutral-800'"
          >
            <span v-if="step.completed" class="text-green-500">✓</span>
            <span v-else class="text-neutral-400">○</span>
            <span>{{ step.content }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>