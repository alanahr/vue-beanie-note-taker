<script setup lang="ts">
import { useEditor, EditorContent, type JSONContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Comment from '../extensions/Comment'
import Document from '@tiptap/extension-document'
import FormHeader from '../extensions/FormHeader'

// Marks
import Subscript from '@tiptap/extension-subscript'
import Superscript from '@tiptap/extension-superscript'
import { TextStyle } from '@tiptap/extension-text-style'

// Nodes
import Audio from '@tiptap/extension-audio'
import { TaskList, TaskItem } from '@tiptap/extension-list'
import { Table, TableRow, TableHeader, TableCell } from '@tiptap/extension-table'
import { Details, DetailsSummary, DetailsContent } from '@tiptap/extension-details'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'

// Functionality
import Typography from '@tiptap/extension-typography'
import UniqueID from '@tiptap/extension-unique-id'
import FileHandler from '@tiptap/extension-file-handler'
import TableOfContents from '@tiptap/extension-table-of-contents'
import FindAndReplace from '@tiptap/extension-find-and-replace'
import { NodeRange } from '@tiptap/extension-node-range'

import { common, createLowlight } from 'lowlight'

import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import EditorToolbar from './EditorToolbar.vue'
import CommentPanel from './CommentPanel.vue'

const lowlight = createLowlight(common)

const CONTENT_KEY = import.meta.env.VITE_CONTENT_KEY || 'tiptap-content'
const AUTOSAVE_INTERVAL = Number(import.meta.env.VITE_AUTOSAVE_INTERVAL) || 5000
const ALLOWED_MIME_TYPES = (import.meta.env.VITE_ALLOWED_MIME_TYPES || 'image/png,image/jpeg,image/gif,image/webp').split(',')

const props = defineProps<{
  content?: JSONContent | string;
  placeholder?: string;
}>()

const emits = defineEmits<{
  (e: 'update', content: JSONContent): void;
}>()

const liveJson = ref<JSONContent | undefined>(undefined)

const CustomDocument = Document.extend({
  content: 'formHeader', // Forces the document to consist of our structured header container
})

const editor = useEditor({
  content: props.content || '',
  extensions: [
    FormHeader,
    CustomDocument,
    StarterKit.configure({
      codeBlock: false,
    }),
    Comment,

    // Marks
    Subscript,
    Superscript,
    TextStyle,

    // Nodes
    Audio,
    TaskList,
    TaskItem.configure({ nested: true }),
    Table.configure({ resizable: true }),
    TableRow,
    TableHeader,
    TableCell,
    Details,
    DetailsSummary,
    DetailsContent,
    CodeBlockLowlight.configure({ lowlight }),

    // Functionality
    Typography,
    FindAndReplace,
    NodeRange,

    UniqueID.configure({
      types: ['heading', 'paragraph', 'blockquote', 'codeBlock'],
    }),
    FileHandler.configure({
      allowedMimeTypes: ALLOWED_MIME_TYPES,
      onDrop: (currentEditor, files, pos) => {
        files.forEach((file) => {
          const reader = new FileReader()
          reader.onload = () => {
            const src = reader.result
            if (typeof src === 'string') {
              currentEditor.chain().focus().insertContentAt(pos, {
                type: 'image',
                attrs: { src },
              }).run()
            }
          }
          reader.readAsDataURL(file)
        })
        return true
      },
      onPaste: (currentEditor, files) => {
        files.forEach((file) => {
          const reader = new FileReader()
          reader.onload = () => {
            const src = reader.result
            if (typeof src === 'string') {
              currentEditor.chain().focus().insertContent({
                type: 'image',
                attrs: { src },
              }).run()
            }
          }
          reader.readAsDataURL(file)
        })
        return true
      },
    }),
    
    TableOfContents.configure({
      onUpdate: (data) => {
        console.log('Table of contents updated:', data)
      },
    }),
  ],
  autofocus: true,
  editorProps: {
    attributes: {
      class: 'prose prose-sm sm:prose lg:prose-lg mx-auto focus:outline-none p-4',
    },
  },
  onUpdate: ({ editor }) => {
    const json = editor.getJSON()
    liveJson.value = json
    emits('update', json)
    localStorage.setItem(CONTENT_KEY, JSON.stringify(json))
  },
})

const autoSaveInterval = ref<number | null>(null)

onMounted(() => {
  const savedContent = localStorage.getItem(CONTENT_KEY)
  if (savedContent && editor.value) {
    try {
      editor.value.commands.setContent(JSON.parse(savedContent))
    } catch {
      editor.value.commands.setContent(savedContent)
    }
  }

  autoSaveInterval.value = window.setInterval(() => {
    if (editor.value) {
      localStorage.setItem(CONTENT_KEY, JSON.stringify(editor.value.getJSON()))
    }
  }, AUTOSAVE_INTERVAL) as unknown as number
})

onBeforeUnmount(() => {
  if (autoSaveInterval.value !== null) {
    clearInterval(autoSaveInterval.value)
  }
})

watch(() => props.content, (newContent) => {
  if (newContent && editor.value) {
    const current = JSON.stringify(editor.value.getJSON())
    const incoming = typeof newContent === 'string' ? newContent : JSON.stringify(newContent)
    if (current !== incoming) {
      editor.value.commands.setContent(newContent)
    }
  }
}, { deep: true })
</script>

<template>
  <div class="tiptap-editor">
    <EditorToolbar :editor="editor" v-if="editor" />
    <EditorContent :editor="editor" class="editor-content" />
    <CommentPanel :editor="editor ?? null" :json="liveJson" />
  </div>
</template>

<style>
.tiptap-editor {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  transition: box-shadow 0.2s ease;
}

.tiptap-editor:focus-within {
  box-shadow: 0 1px 3px rgba(59, 130, 246, 0.5);
  border-color: #3b82f6;
}

.editor-content {
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
  padding: 0.5rem;
}

.ProseMirror:focus {
  outline: none;
}

.ProseMirror p.is-editor-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

/* Styles for content elements */
.ProseMirror p {
  margin: 0.75em 0;
}

.ProseMirror h1 {
  font-size: 1.75em;
  font-weight: 700;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.ProseMirror h2 {
  font-size: 1.5em;
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.ProseMirror h3 {
  font-size: 1.25em;
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

.ProseMirror ul, 
.ProseMirror ol {
  padding-left: 1.5em;
  margin: 0.75em 0;
}

.ProseMirror code {
  background-color: #f1f5f9;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-family: monospace;
}

.ProseMirror blockquote {
  border-left: 3px solid #e2e8f0;
  padding-left: 1em;
  color: #64748b;
  margin: 1em 0;
}

.ProseMirror .comment-mark {
  background-color: #fef9c3;
  border-bottom: 2px solid #fde047;
  border-radius: 2px;
  padding: 0 1px;
  cursor: help;
  transition: background-color 0.15s ease;
}

.ProseMirror .comment-mark[data-closed="true"] {
  background-color: #f1f5f9;
  border-bottom-color: #cbd5e1;
  text-decoration: line-through;
  text-decoration-color: #94a3b8;
}

/* Link */
.ProseMirror a {
  color: #2563eb;
  text-decoration: underline;
  cursor: pointer;
}

/* Underline */
.ProseMirror u {
  text-decoration: underline;
}

/* Subscript / Superscript */
.ProseMirror sub {
  font-size: 0.75em;
}
.ProseMirror sup {
  font-size: 0.75em;
}

/* Task list */
.ProseMirror ul[data-type="taskList"] {
  list-style: none;
  padding-left: 0;
}
.ProseMirror ul[data-type="taskList"] li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
.ProseMirror ul[data-type="taskList"] li > label {
  flex-shrink: 0;
  user-select: none;
}
.ProseMirror ul[data-type="taskList"] li > div {
  flex: 1;
}
.ProseMirror ul[data-type="taskList"] input[type="checkbox"] {
  cursor: pointer;
  width: 1rem;
  height: 1rem;
  margin-top: 0.25rem;
}

/* Tables */
.ProseMirror table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  table-layout: fixed;
  overflow: hidden;
}
.ProseMirror th, .ProseMirror td {
  border: 1px solid #cbd5e1;
  padding: 0.5rem 0.75rem;
  text-align: left;
  vertical-align: top;
}
.ProseMirror th {
  background-color: #f1f5f9;
  font-weight: 600;
}
.ProseMirror .selectedCell {
  background-color: #dbeafe;
}
.ProseMirror .tableWrapper {
  overflow-x: auto;
}

/* Audio */
.ProseMirror audio {
  display: block;
  max-width: 100%;
  margin: 1em 0;
}

/* Details */
.ProseMirror details {
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  margin: 1em 0;
  background: #f8fafc;
}
.ProseMirror details > summary {
  cursor: pointer;
  font-weight: 600;
  color: #1e293b;
  list-style: revert;
}
.ProseMirror details > div {
  margin-top: 0.5rem;
}

/* Code block with lowlight */
.ProseMirror pre {
  background: #1e293b;
  color: #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1em 0;
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}
.ProseMirror pre code {
  background: none;
  padding: 0;
  color: inherit;
}
.ProseMirror .hljs-comment, .ProseMirror .hljs-quote {
  color: #64748b;
  font-style: italic;
}
.ProseMirror .hljs-keyword, .ProseMirror .hljs-selector-tag {
  color: #c084fc;
}
.ProseMirror .hljs-string, .ProseMirror .hljs-attr {
  color: #86efac;
}
.ProseMirror .hljs-number, .ProseMirror .hljs-literal {
  color: #fdba74;
}
.ProseMirror .hljs-title, .ProseMirror .hljs-section, .ProseMirror .hljs-name {
  color: #7dd3fc;
}
.ProseMirror .hljs-tag, .ProseMirror .hljs-attribute {
  color: #fca5a5;
}
.ProseMirror .hljs-variable, .ProseMirror .hljs-template-variable {
  color: #fbbf24;
}
.ProseMirror .hljs-built_in, .ProseMirror .hljs-type {
  color: #67e8f9;
}

/* Horizontal rule */
.ProseMirror hr {
  border: none;
  border-top: 2px solid #e2e8f0;
  margin: 1.5em 0;
}

/* Find and replace */
.ProseMirror .find-result {
  background-color: #fef08a;
  border-radius: 2px;
}
.ProseMirror .find-result.current {
  background-color: #fdba74;
}
</style>
