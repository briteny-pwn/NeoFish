export interface SessionPreviewMessage {
  type?: string
  role?: string
  message?: string
  content?: string
  message_key?: string
  params?: Record<string, unknown>
}

interface PreviewOptions<T extends SessionPreviewMessage> {
  maxLength?: number
  resolveText?: (message: T) => string
}

const HIDDEN_PREVIEW_KEYS = new Set([
  'common.connected_ws',
  'common.context_compressing',
  'common.manual_compressing',
  'common.agent_resumed',
  'common.sent_resume',
  'common.message_queued',
  'common.agent_starting',
  'common.agent_thinking',
  'common.executing_action',
  'common.takeover_browser_opened',
  'common.takeover_ended_message',
  'common.agent_paused_for_takeover',
  'common.image_input_disabled',
  'common.max_steps_error',
])

const HIDDEN_PREVIEW_PREFIXES = [
  '[Image] ',
  '[Action Required] ',
  '[Takeover] ',
  '[Takeover Ended] ',
  'Executing action:',
  'Agent is thinking',
  'Error calling LLM:',
]

const HIDDEN_PREVIEW_SNIPPETS = [
  'Connected to NeoFish Agent WebSocket',
  'Task reached maximum steps without calling finish_task',
  'Context threshold reached',
  'Manual compression triggered',
  'Agent paused for manual takeover',
  '已发送继续执行',
]

function stripMarkdownPreview(text: string): string {
  return text
    .replace(/!\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/\[([^\]]+)]\(([^)]+)\)/g, '$1')
    .replace(/^\s{0,3}#{1,6}\s*/gm, '')
    .replace(/^\s*[-*+]\s+/gm, '')
    .replace(/^\s*\d+\.\s+/gm, '')
    .replace(/[`*_~]+/g, '')
    .replace(/^>\s*/gm, '')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^["']+|["']+$/g, '')
}

function getPreviewText<T extends SessionPreviewMessage>(
  message: T,
  resolveText?: (message: T) => string,
): string {
  const raw = resolveText ? resolveText(message) : message.message || message.content || ''
  return typeof raw === 'string' ? raw.trim() : ''
}

function isPreviewCandidate<T extends SessionPreviewMessage>(
  message: T,
  resolveText?: (message: T) => string,
): boolean {
  const content = getPreviewText(message, resolveText)
  if (!content) return false

  if (message.type === 'user' || message.role === 'user') {
    return true
  }

  if (message.message_key && HIDDEN_PREVIEW_KEYS.has(message.message_key)) {
    return false
  }

  if (HIDDEN_PREVIEW_PREFIXES.some(prefix => content.startsWith(prefix))) {
    return false
  }

  if (HIDDEN_PREVIEW_SNIPPETS.some(snippet => content.includes(snippet))) {
    return false
  }

  return true
}

export function extractSessionPreview<T extends SessionPreviewMessage>(
  messages: ReadonlyArray<T>,
  options: PreviewOptions<T> = {},
): string {
  const { maxLength = 120, resolveText } = options

  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index]
    if (!message || !isPreviewCandidate(message, resolveText)) continue

    const preview = stripMarkdownPreview(getPreviewText(message, resolveText))
    if (preview) {
      return preview.slice(0, maxLength)
    }
  }

  return ''
}
