<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TiptapEditor from './components/TiptapEditor.vue'
import type { JSONContent } from '@tiptap/vue-3'
import {
  createDocumentUUID,
  fetchDocument,
  saveDocument,
} from './services/documentApi'
import type { DocumentRecord } from './types'

const defaultContent = (): JSONContent => ({
  type: 'doc',
  content: [
    {
      type: 'formHeader',
      content: [
        {
          type: 'paragraph',
          content: [
            {
              type: 'text',
              text: 'This is the first editable paragraph inside the form.',
            },
          ],
        }
      ],
    },
    { type: 'heading', attrs: { level: 2 }, content: [{ type: 'text', text: 'Welcome to the Tiptap Editor' }] },
    { type: 'paragraph', content: [
      { type: 'text', text: 'This is a rich text editor built with ' },
      { type: 'text', marks: [{ type: 'bold' }], text: 'Tiptap' },
      { type: 'text', text: ', ' },
      { type: 'text', marks: [{ type: 'bold' }], text: 'Vue 3' },
      { type: 'text', text: ', and ' },
      { type: 'text', marks: [{ type: 'bold' }], text: 'TypeScript' },
      { type: 'text', text: '.' }
    ] },
    { type: 'paragraph', content: [
      { type: 'text', text: 'Try formatting text with the toolbar above, or use keyboard shortcuts like ' },
      { type: 'text', marks: [{ type: 'code' }], text: 'Ctrl+B' },
      { type: 'text', text: ' for bold and ' },
      { type: 'text', marks: [{ type: 'code' }], text: 'Ctrl+I' },
      { type: 'text', text: ' for italic.' }
    ] }
  ]
})

const docUuid = ref<string>('')
const content = ref<JSONContent>(defaultContent())
const isSaving = ref(false)
const isLoaded = ref(false)
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const lastSavedAt = ref<string | null>(null)

const handleUpdate = (newContent: JSONContent) => {
  content.value = newContent
}

const handleSave = async () => {
  if (isSaving.value) return
  isSaving.value = true
  saveStatus.value = 'saving'
  try {
    const record: DocumentRecord = {
      uuid: docUuid.value,
      content: content.value,
      updatedAt: lastSavedAt.value ?? new Date().toISOString(),
    }
    const saved = await saveDocument(record)
    lastSavedAt.value = saved.updatedAt
    saveStatus.value = 'saved'
  } catch {
    saveStatus.value = 'error'
  } finally {
    isSaving.value = false
    setTimeout(() => {
      if (saveStatus.value === 'saved') saveStatus.value = 'idle'
    }, 2500)
  }
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const queryUuid = params.get('doc')
  docUuid.value = queryUuid || createDocumentUUID()

  if (queryUuid) {
    const existing = await fetchDocument(queryUuid)
    if (existing) {
      content.value = existing.content
      lastSavedAt.value = existing.updatedAt
    }
  }

  isLoaded.value = true
})
</script>

<template>
  <div class="app-container">
    <header>
      <h1 class="app-title">Tiptap Rich Text Editor</h1>
      <p class="app-description">
        A beautiful rich text editor powered by Tiptap, Vue 3, and TypeScript
      </p>
    </header>

    <main v-if="isLoaded">
      <div class="doc-bar">
        <div class="doc-uuid">
          <span class="doc-label">Document UUID:</span>
          <code>{{ docUuid }}</code>
        </div>
        <button
          class="save-btn"
          :disabled="isSaving"
          @click="handleSave"
        >
          <span v-if="isSaving" class="save-spinner"></span>
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
      <div v-if="saveStatus !== 'idle'" class="save-status" :class="saveStatus">
        <template v-if="saveStatus === 'saving'">Saving document...</template>
        <template v-else-if="saveStatus === 'saved'">Saved successfully{{ lastSavedAt ? ' at ' + new Date(lastSavedAt).toLocaleTimeString() : '' }}</template>
        <template v-else-if="saveStatus === 'error'">Failed to save. Please try again.</template>
      </div>

      <div class="editor-container">
        <TiptapEditor 
          :content="content" 
          placeholder="Start writing something amazing..."
          @update="handleUpdate" 
        />
      </div>

      <div class="content-preview">
        <h3>JSON Output:</h3>
        <pre>{{ JSON.stringify({ uuid: docUuid, ...content }, null, 2) }}</pre>
      </div>

      <div class="rendered-preview">
        <h3>Preview:</h3>
        <div class="preview-content" v-html="content"></div>
      </div>
    </main>
    <main v-else class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading document...</p>
    </main>

    <footer>
      <p>Tiptap Editor Example with Vue 3 and TypeScript</p>
    </footer>
  </div>
</template>

<style>
/* Global styles */
:root {
  --primary: #3B82F6;
  --primary-light: #93C5FD;
  --accent: #10B981;
  --dark: #1E293B;
  --light: #F8FAFC;
  --gray: #64748B;
  --gray-light: #E2E8F0;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: #F1F5F9;
  color: var(--dark);
  line-height: 1.5;
}

/* App container */
.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

/* Header styles */
header {
  text-align: center;
  margin-bottom: 2rem;
}

.app-title {
  font-size: 2.25rem;
  color: var(--primary);
  margin-bottom: 0.5rem;
}

.app-description {
  font-size: 1.125rem;
  color: var(--gray);
  max-width: 600px;
  margin: 0 auto;
}

/* Doc bar */
.doc-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  background: white;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
}

.doc-uuid {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  min-width: 0;
}

.doc-label {
  color: var(--gray);
  font-weight: 600;
  white-space: nowrap;
}

.doc-uuid code {
  font-family: monospace;
  font-size: 0.75rem;
  color: var(--primary);
  background: #eff6ff;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.save-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  border: none;
  background: var(--primary);
  color: white;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.1s ease;
  white-space: nowrap;
}

.save-btn:hover:not(:disabled) {
  background: #2563eb;
}

.save-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.save-status {
  font-size: 0.8125rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  margin-top: -0.5rem;
}

.save-status.saving {
  color: var(--primary);
  background: #eff6ff;
}

.save-status.saved {
  color: var(--accent);
  background: #ecfdf5;
}

.save-status.error {
  color: #dc2626;
  background: #fef2f2;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 0;
  color: var(--gray);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--gray-light);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* Main content */
main {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.editor-container {
  width: 100%;
}

/* Preview sections */
.content-preview,
.rendered-preview {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.content-preview h3,
.rendered-preview h3 {
  margin-top: 0;
  font-size: 1.25rem;
  color: var(--dark);
  border-bottom: 1px solid var(--gray-light);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.content-preview pre {
  background-color: #f1f5f9;
  padding: 1rem;
  border-radius: 0.25rem;
  overflow-x: auto;
  font-family: monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
  word-break: break-all;
}

.preview-content {
  padding: 1rem;
  border: 1px solid var(--gray-light);
  border-radius: 0.25rem;
  background-color: var(--light);
}

/* Footer */
footer {
  margin-top: 3rem;
  text-align: center;
  color: var(--gray);
  font-size: 0.875rem;
  padding: 1rem 0;
  border-top: 1px solid var(--gray-light);
}

/* Responsive adjustments */
@media (min-width: 768px) {
  .app-container {
    padding: 2rem;
  }
}
</style>