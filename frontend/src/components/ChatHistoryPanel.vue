<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Trash2, Pencil, Check, X, MessageSquare } from 'lucide-vue-next'
import { useChatHistory, type ChatSession } from '../composables/useChatHistory'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { sessions, activeChatId, createNewChat, deleteChat, renameChat } = useChatHistory()

const emit = defineEmits<{
  (e: 'select', id: string): void
  (e: 'new-chat'): void
}>()

// Inline rename state
const editingId = ref<string | null>(null)
const editingTitle = ref('')

function startRename(session: ChatSession) {
  editingId.value = session.id
  editingTitle.value = session.title
}

async function confirmRename(id: string) {
  if (editingTitle.value.trim()) {
    await renameChat(id, editingTitle.value.trim())
  }
  editingId.value = null
}

function cancelRename() {
  editingId.value = null
}

async function handleDelete(id: string) {
  await deleteChat(id)
  // If we deleted the active one, parent handles switching via activeChatId change
}

async function handleNewChat() {
  await createNewChat()
  emit('new-chat')
}

function handleSelect(id: string) {
  activeChatId.value = id
  emit('select', id)
}

function formatDate(iso: string) {
  const d = new Date(iso)
  const now = new Date()
  const diffDays = Math.floor((now.getTime() - d.getTime()) / 86400000)
  if (diffDays === 0) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  if (diffDays === 1) return t('history.yesterday')
  if (diffDays < 7) return t('history.days_ago', { n: diffDays })
  return d.toLocaleDateString()
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="px-3 py-4 border-b border-neutral-100">
      <h2 class="text-xs font-semibold text-neutral-500 uppercase tracking-widest mb-3">
        {{ $t('history.panel_title') }}
      </h2>
      <button
        @click="handleNewChat"
        class="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl bg-neutral-900 text-white text-sm font-medium hover:bg-neutral-700 transition-all active:scale-95"
      >
        <Plus :size="16" />
        {{ $t('history.new_chat') }}
      </button>
    </div>

    <!-- Sessions list -->
    <div class="flex-1 overflow-y-auto py-2 custom-scrollbar">
      <div v-if="sessions.length === 0" class="flex flex-col items-center justify-center h-40 text-neutral-400 gap-2">
        <MessageSquare :size="28" stroke-width="1.5" />
        <p class="text-xs">{{ $t('history.empty_state') }}</p>
      </div>

      <div
        v-for="session in sessions"
        :key="session.id"
        class="group mx-2 mb-1 rounded-xl transition-all cursor-pointer"
        :class="session.id === activeChatId
          ? 'bg-neutral-100'
          : 'hover:bg-neutral-50'"
        @click="handleSelect(session.id)"
      >
        <!-- Editing mode -->
        <div v-if="editingId === session.id" class="flex items-center gap-1 p-2" @click.stop>
          <input
            v-model="editingTitle"
            @keydown.enter="confirmRename(session.id)"
            @keydown.esc="cancelRename"
            class="flex-1 text-sm text-neutral-800 bg-white border border-neutral-300 rounded-lg px-2 py-1 outline-none focus:border-neutral-500"
            :placeholder="$t('history.rename_placeholder')"
            autofocus
          />
          <button @click="confirmRename(session.id)" class="p-1 text-green-600 hover:bg-green-50 rounded-md transition-colors">
            <Check :size="14" />
          </button>
          <button @click="cancelRename" class="p-1 text-neutral-400 hover:bg-neutral-100 rounded-md transition-colors">
            <X :size="14" />
          </button>
        </div>

        <!-- Normal mode -->
        <div v-else class="flex items-start gap-2 p-2.5 pr-2">
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-neutral-800 truncate leading-snug">
              {{ session.title || $t('history.new_chat') }}
            </p>
            <p v-if="session.preview" class="text-xs text-neutral-400 truncate mt-0.5 leading-relaxed">
              {{ session.preview }}
            </p>
            <p class="text-[10px] text-neutral-300 mt-1">{{ formatDate(session.created_at) }}</p>
          </div>

          <!-- Action buttons (visible on hover) -->
          <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-0.5" @click.stop>
            <button
              @click="startRename(session)"
              class="p-1 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-200 rounded-md transition-colors"
              :title="$t('history.rename')"
            >
              <Pencil :size="12" />
            </button>
            <button
              @click="handleDelete(session.id)"
              class="p-1 text-neutral-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
              :title="$t('history.delete')"
            >
              <Trash2 :size="12" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 3px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.08); border-radius: 10px; }
</style>
