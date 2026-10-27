<template>
  <div class="view">
    <div class="page-head">
      <h1>智能助手</h1>
      <p>联网搜索 + 工具调用 + 事实记忆的对话助手</p>
    </div>

    <div class="chat-box">
      <div class="messages" ref="msgRef">
        <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
          <div class="avatar" :class="m.role">{{ m.role === 'user' ? '我' : 'AI' }}</div>
          <div class="bubble">
            <div v-if="m.toolCalls?.length" class="tool-calls">
              <div v-for="(t, j) in m.toolCalls" :key="j" class="tool-call">
                <el-icon><Tools /></el-icon> 调用工具：<code>{{ t.name }}</code>
                <span class="args">{{ JSON.stringify(t.args) }}</span>
              </div>
            </div>
            <pre class="text">{{ m.content }}</pre>
          </div>
        </div>
        <div v-if="loading" class="msg assistant">
          <div class="avatar assistant">AI</div>
          <div class="bubble typing"><span></span><span></span><span></span></div>
        </div>
      </div>

      <div class="input-row">
        <el-input v-model="input" placeholder="问我任何金融问题，例如：帮我查一下贵州茅台的实时行情" size="large" @keyup.enter="send" />
        <el-button type="primary" size="large" :loading="loading" @click="send">发送</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { chatAssistant } from '@/api'
import { ElMessage } from 'element-plus'

interface Msg { role: 'user' | 'assistant'; content: string; toolCalls?: any[] }

const messages = ref<Msg[]>([])
const input = ref('')
const loading = ref(false)
const msgRef = ref<HTMLElement>()

async function send() {
  const text = input.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  await scrollBottom()
  try {
    const r = await chatAssistant(text)
    messages.value.push({ role: 'assistant', content: r.answer, toolCalls: r.tool_calls })
  } catch (e: any) {
    ElMessage.error(e?.message || '对话失败')
  } finally {
    loading.value = false
    await scrollBottom()
  }
}

async function scrollBottom() {
  await nextTick()
  msgRef.value?.scrollTo({ top: msgRef.value.scrollHeight, behavior: 'smooth' })
}
</script>

<style scoped>
.view { max-width: 960px; margin: 0 auto; height: 100%; display: flex; flex-direction: column; }
.page-head h1 { font-size: 24px; margin-bottom: 4px; }
.page-head p { color: var(--text-dim); font-size: 13px; margin-bottom: 20px; }
.chat-box { flex: 1; display: flex; flex-direction: column; background: var(--card); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }
.messages { flex: 1; overflow-y: auto; padding: 20px; }
.msg { display: flex; gap: 12px; margin-bottom: 20px; }
.msg.user { flex-direction: row-reverse; }
.avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; flex-shrink: 0; }
.avatar.user { background: var(--primary); color: #fff; }
.avatar.assistant { background: linear-gradient(135deg, #7c5cff, #409eff); color: #fff; }
.bubble { max-width: 75%; }
.msg.user .bubble { background: rgba(64,158,255,0.15); border: 1px solid rgba(64,158,255,0.3); border-radius: 14px 4px 14px 14px; padding: 12px 16px; }
.msg.assistant .bubble { background: var(--bg-soft); border: 1px solid var(--border); border-radius: 4px 14px 14px 14px; padding: 12px 16px; }
.text { white-space: pre-wrap; line-height: 1.7; font-size: 14px; color: var(--text); font-family: inherit; }
.tool-calls { margin-bottom: 8px; }
.tool-call { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--gold); margin-bottom: 4px; }
.tool-call code { background: rgba(230,162,60,0.15); padding: 2px 6px; border-radius: 4px; }
.args { color: var(--text-dim); }
.input-row { display: flex; gap: 12px; padding: 16px; border-top: 1px solid var(--border); }
.typing { display: flex; gap: 4px; padding: 16px; }
.typing span { width: 6px; height: 6px; border-radius: 50%; background: var(--text-dim); animation: bounce 1.2s infinite; }
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }
</style>
