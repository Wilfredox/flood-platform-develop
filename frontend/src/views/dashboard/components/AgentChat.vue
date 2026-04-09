<script setup lang="ts">
/**
 * M09 智能体对话面板
 * [DEMO-ONLY] 嵌入大屏右栏的 AI 智能助手
 * 设计理念：智能体是驾驶舱的有机组成部分，而非外置弹窗
 */
import { ref, nextTick, onMounted } from 'vue'
import {
  mockAgentReply,
  createUserMessage,
  getWelcomeMessage,
  quickCommands
} from '@/mock/agent'
import type { AgentMessage } from '@/mock/agent'

const messages = ref<AgentMessage[]>([])
const inputText = ref('')
const isThinking = ref(false)
const chatBody = ref<HTMLDivElement>()

onMounted(() => {
  messages.value.push(getWelcomeMessage())
})

async function sendMessage(text?: string) {
  const content = (text || inputText.value).trim()
  if (!content || isThinking.value) return

  // 添加用户消息
  messages.value.push(createUserMessage(content))
  inputText.value = ''
  isThinking.value = true
  await scrollToBottom()

  // 模拟智能体回复
  try {
    const reply = await mockAgentReply(content)
    messages.value.push(reply)
  } finally {
    isThinking.value = false
  }
  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (chatBody.value) {
    chatBody.value.scrollTop = chatBody.value.scrollHeight
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

/** 智能体类型 → 图标色映射 */
function agentColor(type?: string): string {
  const map: Record<string, string> = {
    'flood-analysis': '#00D4FF',
    'alert-decision': '#FAAD14',
    'optimization': '#52C41A',
    'emergency': '#F5222D',
    'query': '#1890FF',
    'report': '#B37FEB'
  }
  return map[type || ''] || '#1890FF'
}
</script>

<template>
  <div class="agent-panel card-panel">
    <!-- 面板头部 -->
    <div class="agent-header">
      <div class="header-left">
        <span class="ai-dot"></span>
        <span class="title">防汛智能体</span>
      </div>
      <span class="status-tag" :class="{ thinking: isThinking }">
        {{ isThinking ? '思考中...' : '就绪' }}
      </span>
    </div>

    <!-- 快捷指令栏 -->
    <div class="quick-bar">
      <button
        v-for="cmd in quickCommands"
        :key="cmd.label"
        class="quick-btn"
        :disabled="isThinking"
        @click="sendMessage(cmd.prompt)"
      >
        <span class="cmd-icon">{{ cmd.icon }}</span>
        <span class="cmd-label">{{ cmd.label }}</span>
      </button>
    </div>

    <!-- 消息区域 -->
    <div ref="chatBody" class="chat-body">
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="msg-row"
        :class="msg.role"
      >
        <!-- 智能体头像 -->
        <div v-if="msg.role === 'agent'" class="avatar agent-avatar" :style="{ borderColor: agentColor(msg.agentType) }">
          AI
        </div>

        <div class="msg-bubble" :class="msg.role">
          <!-- 系统消息 -->
          <div v-if="msg.role === 'system'" class="system-msg">
            {{ msg.content }}
          </div>
          <!-- 用户消息 -->
          <div v-else-if="msg.role === 'user'" class="user-content">
            {{ msg.content }}
          </div>
          <!-- 智能体消息（支持简单 Markdown） -->
          <div v-else class="agent-content" v-html="renderMarkdown(msg.content)"></div>
          <span class="msg-time">{{ msg.timestamp }}</span>
        </div>

        <!-- 用户头像 -->
        <div v-if="msg.role === 'user'" class="avatar user-avatar">
          我
        </div>
      </div>

      <!-- 思考指示器 -->
      <div v-if="isThinking" class="msg-row agent">
        <div class="avatar agent-avatar" style="border-color: #1890FF;">AI</div>
        <div class="msg-bubble agent">
          <div class="thinking-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <input
        v-model="inputText"
        class="chat-input"
        placeholder="输入问题，如：分析当前汛情..."
        :disabled="isThinking"
        @keydown="handleKeyDown"
      />
      <button class="send-btn" :disabled="!inputText.trim() || isThinking" @click="sendMessage()">
        ▶
      </button>
    </div>
  </div>
</template>

<script lang="ts">
/** 简单 Markdown 渲染（加粗 / 表格 / 列表 / 换行） */
function renderMarkdown(text: string): string {
  let html = text
    // 转义 HTML
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    // 加粗
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 行内代码
    .replace(/`(.+?)`/g, '<code>$1</code>')

  // 处理表格
  const lines = html.split('\n')
  let inTable = false
  const result: string[] = []
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (line.startsWith('|') && line.endsWith('|')) {
      if (!inTable) {
        result.push('<table class="md-table">')
        inTable = true
      }
      // 跳过分隔行 |---|---|
      if (/^\|[\s\-:|]+\|$/.test(line)) continue
      const cells = line.split('|').filter(c => c.trim())
      const tag = result.filter(r => r.includes('<tr>')).length === 0 ? 'th' : 'td'
      result.push('<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>')
    } else {
      if (inTable) {
        result.push('</table>')
        inTable = false
      }
      // 列表
      if (/^\d+\.\s/.test(line)) {
        result.push('<div class="md-li">' + line + '</div>')
      } else if (line.startsWith('- ')) {
        result.push('<div class="md-li">' + line + '</div>')
      } else if (line === '---') {
        result.push('<hr class="md-hr"/>')
      } else {
        result.push(line)
      }
    }
  }
  if (inTable) result.push('</table>')
  return result.join('<br/>')
}

export default { methods: { renderMarkdown } }
</script>

<style scoped>
.agent-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
  height: 100%;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #52C41A;
  box-shadow: 0 0 6px #52C41A88;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(82, 196, 26, 0.15);
  color: #52C41A;
}

.status-tag.thinking {
  background: rgba(24, 144, 255, 0.15);
  color: #1890FF;
  animation: pulse 1s infinite;
}

/* 快捷指令 */
.quick-bar {
  display: flex;
  gap: 4px;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  overflow-x: auto;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 3px 8px;
  background: rgba(24, 144, 255, 0.08);
  border: 1px solid rgba(24, 144, 255, 0.25);
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.quick-btn:hover:not(:disabled) {
  background: rgba(24, 144, 255, 0.18);
  color: var(--text-primary);
  border-color: var(--color-primary);
}

.quick-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.cmd-icon {
  font-size: 12px;
}

/* 消息区 */
.chat-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.chat-body::-webkit-scrollbar {
  width: 6px;
}

.chat-body::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 3px;
}

.chat-body::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
  min-height: 30px;
}

.chat-body::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.msg-row.system {
  justify-content: center;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.agent-avatar {
  background: rgba(24, 144, 255, 0.15);
  color: #1890FF;
  border: 2px solid #1890FF;
}

.user-avatar {
  background: rgba(82, 196, 26, 0.15);
  color: #52C41A;
  border: 2px solid #52C41A;
}

.msg-bubble {
  max-width: 85%;
  position: relative;
  overflow-wrap: break-word;
  word-break: break-word;
}

.msg-bubble.system {
  max-width: 100%;
}

.system-msg {
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: center;
  padding: 4px 0;
}

.user-content {
  background: rgba(24, 144, 255, 0.12);
  border: 1px solid rgba(24, 144, 255, 0.25);
  border-radius: 12px 12px 2px 12px;
  padding: 8px 12px;
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.5;
}

.agent-content {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px 12px 12px 2px;
  padding: 10px 14px;
  font-size: 12px;
  color: var(--text-primary);
  line-height: 1.7;
}

.agent-content :deep(strong) {
  color: var(--color-accent);
}

.agent-content :deep(.md-table) {
  width: 100%;
  margin: 6px 0;
  border-collapse: collapse;
  font-size: 11px;
}

.agent-content :deep(.md-table th),
.agent-content :deep(.md-table td) {
  border: 1px solid var(--border-color);
  padding: 3px 6px;
  text-align: left;
}

.agent-content :deep(.md-table th) {
  background: rgba(24, 144, 255, 0.08);
  color: var(--text-secondary);
}

.agent-content :deep(.md-li) {
  padding-left: 8px;
}

.agent-content :deep(.md-hr) {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: 6px 0;
}

.agent-content :deep(code) {
  background: rgba(24, 144, 255, 0.1);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 11px;
}

.msg-time {
  display: block;
  font-size: 10px;
  color: var(--text-tertiary);
  margin-top: 4px;
  text-align: right;
}

.msg-row.agent .msg-time {
  text-align: left;
}

/* 思考动画 */
.thinking-dots {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}

.thinking-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: blink 1.4s infinite both;
}

.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; }
  40% { opacity: 1; }
}

/* 输入区 */
.input-area {
  display: flex;
  gap: 6px;
  padding: 8px 10px;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.chat-input {
  flex: 1;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 10px;
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: var(--color-primary);
}

.chat-input::placeholder {
  color: var(--text-tertiary);
}

.send-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: var(--color-primary);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  background: #40a9ff;
}

.send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
</style>
