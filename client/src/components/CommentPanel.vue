<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Editor } from '@tiptap/vue-3'
import type { JSONContent } from '@tiptap/vue-3'
import type { CommentItem } from '../types'

const props = defineProps<{
  editor: Editor | null
  json: JSONContent | string | undefined
}>()

const newComment = ref('')
const showPanel = ref(false)

const collectComments = (doc: JSONContent | string | undefined): CommentItem[] => {
  if (!doc || typeof doc === 'string') return []
  const items: CommentItem[] = []
  const walk = (node: JSONContent) => {
    if (node.type === 'text' && node.marks) {
      for (const mark of node.marks) {
        if (mark.type === 'comment') {
          const attrs = mark.attrs || {}
          items.push({
            id: `${node.text || ''}-${attrs.createdAt || ''}`,
            text: node.text || '',
            comment: attrs.comment || '',
            user: attrs.user || import.meta.env.VITE_DEFAULT_COMMENT_USER || 'admin',
            createdAt: attrs.createdAt || new Date().toISOString(),
            closed: attrs.closed ?? false,
            range: attrs.range ?? null,
          })
        }
      }
    }
    if (node.content) {
      for (const child of node.content) walk(child)
    }
  }
  walk(doc)
  return items
}

const comments = computed<CommentItem[]>(() => collectComments(props.json ?? { type: 'doc' }))

const openCount = computed(() => comments.value.filter((c) => !c.closed).length)

const formatDate = (iso: string): string => {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

const addComment = () => {
  if (!props.editor || !newComment.value.trim()) return
  props.editor.chain().focus().setComment({ comment: newComment.value.trim() }).run()
  newComment.value = ''
  showPanel.value = true
}

const toggleClosed = (item: CommentItem) => {
  if (!props.editor) return
  props.editor.commands.updateComment({
    closed: !item.closed,
  })
}

const removeComment = () => {
  if (!props.editor) return
  props.editor.chain().focus().unsetComment().run()
}

const hasSelection = ref(false)

watch(
  () => props.editor,
  (editor) => {
    if (!editor) return
    editor.on('selectionUpdate', () => {
      hasSelection.value = !editor.state.selection.empty
    })
  },
  { immediate: true }
)
</script>

<template>
  <div class="comment-feature">
    <div class="comment-input-row">
      <input
        v-model="newComment"
        type="text"
        placeholder="Type a comment, then select text and click Add"
        class="comment-input"
        @keyup.enter="addComment"
      />
      <button
        class="comment-add-btn"
        :disabled="!newComment.trim() || !hasSelection"
        :title="!hasSelection ? 'Select text in the editor first' : ''"
        @click="addComment"
      >
        Add Comment
      </button>
      <button
        class="comment-toggle-btn"
        @click="showPanel = !showPanel"
        :class="{ active: showPanel }"
      >
        {{ showPanel ? 'Hide' : 'Show' }} Comments ({{ openCount }})
      </button>
    </div>

    <transition name="slide">
      <div v-if="showPanel" class="comment-panel">
        <div v-if="comments.length === 0" class="comment-empty">
          No comments yet. Select text in the editor, type a comment above, and click Add Comment.
        </div>
        <transition-group name="list" tag="div">
          <div
            v-for="item in comments"
            :key="item.id"
            class="comment-card"
            :class="{ closed: item.closed }"
          >
            <div class="comment-card-header">
              <span class="comment-user">{{ item.user }}</span>
              <span class="comment-date">{{ formatDate(item.createdAt) }}</span>
            </div>
            <p class="comment-text">{{ item.comment }}</p>
            <div class="comment-highlight">"{{ item.text }}"</div>
            <div v-if="item.range" class="comment-range">
              Range: {{ item.range.from }}–{{ item.range.to }}
            </div>
            <div class="comment-card-actions">
              <button class="comment-action" @click="toggleClosed(item)">
                {{ item.closed ? 'Reopen' : 'Close' }}
              </button>
              <button class="comment-action danger" @click="removeComment()">
                Remove
              </button>
            </div>
            <span v-if="item.closed" class="badge-closed">Closed</span>
          </div>
        </transition-group>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.comment-feature {
  margin-top: 0.75rem;
}

.comment-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.comment-input {
  flex: 1;
  min-width: 200px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1e293b;
  background: #fff;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.comment-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.comment-add-btn,
.comment-toggle-btn {
  padding: 0.5rem 0.875rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.comment-add-btn:not(:disabled):hover {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

.comment-add-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.comment-toggle-btn:hover,
.comment-toggle-btn.active {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.comment-toggle-btn.active {
  color: #1e293b;
}

.comment-panel {
  margin-top: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 0.75rem;
  max-height: 340px;
  overflow-y: auto;
}

.comment-empty {
  color: #64748b;
  font-size: 0.875rem;
  text-align: center;
  padding: 1.5rem 0.5rem;
}

.comment-card {
  position: relative;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-left: 3px solid #3b82f6;
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  transition: opacity 0.2s ease, border-color 0.2s ease;
}

.comment-card.closed {
  border-left-color: #94a3b8;
  opacity: 0.7;
}

.comment-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.375rem;
}

.comment-user {
  font-weight: 600;
  font-size: 0.8125rem;
  color: #1e293b;
}

.comment-date {
  font-size: 0.75rem;
  color: #94a3b8;
}

.comment-text {
  font-size: 0.875rem;
  color: #334155;
  margin: 0 0 0.375rem;
  line-height: 1.4;
}

.comment-highlight {
  font-size: 0.75rem;
  color: #64748b;
  background: #fef9c3;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-style: italic;
  margin-bottom: 0.5rem;
  border-left: 2px solid #fde047;
}

.comment-range {
  font-size: 0.6875rem;
  color: #94a3b8;
  font-family: monospace;
  margin-bottom: 0.5rem;
}

.comment-card-actions {
  display: flex;
  gap: 0.5rem;
}

.comment-action {
  font-size: 0.75rem;
  padding: 0.25rem 0.625rem;
  border-radius: 0.25rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
}

.comment-action:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.comment-action.danger:hover {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #dc2626;
}

.badge-closed {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  background: #e2e8f0;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
  max-height: 340px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.2s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

.list-move {
  transition: transform 0.2s ease;
}
</style>
