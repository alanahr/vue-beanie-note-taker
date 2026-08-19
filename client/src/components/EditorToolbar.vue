<script setup lang="ts">
import { type Editor } from '@tiptap/vue-3'
import { ref } from 'vue'

const props = defineProps<{
  editor: Editor | null
}>()

const isActive = (type: string, options?: any) => {
  if (!props.editor) return false
  return props.editor.isActive(type, options)
}

const headingLevel = ref(0)

const updateHeadingLevel = (level: number) => {
  headingLevel.value = isActive('heading', { level }) ? 0 : level
}
const addToken = () =>{
  props.editor.commands.insertToken({
  label: 'User: John Doe',
  jsonData: { id: 123, role: 'admin', email: 'john@example.com' }
})
}
const addComment = () => {
  if (!props.editor || props.editor.state.selection.empty) return
  const text = props.editor.state.doc.textBetween(
    props.editor.state.selection.from,
    props.editor.state.selection.to,
    ' '
  )
  if (!text) return
  const comment = window.prompt('Enter a comment for the selected text:')
  if (comment && comment.trim()) {
    props.editor.chain().focus().setComment({ comment: comment.trim() }).run()
  }
}

const setLink = () => {
  if (!props.editor) return
  const previous = props.editor.getAttributes('link').href || ''
  const url = window.prompt('URL', previous)
  if (url === null) return
  if (url === '') {
    props.editor.chain().focus().extendMarkRange('link').unsetLink().run()
    return
  }
  props.editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
}

const insertTable = () => {
  if (!props.editor) return
  props.editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
}

const addAudio = () => {
  if (!props.editor) return
  const url = window.prompt('Audio URL')
  if (url) {
    props.editor.chain().focus().setAudio({ src: url }).run()
  }
}

const addDetails = () => {
  if (!props.editor) return
  props.editor.chain().focus().setDetails().run()
}
</script>

<template>
  <div class="editor-toolbar" v-if="editor">
    <div class="toolbar-group">
      <button
        class="toolbar-button"
        :class="{ active: isActive('heading', { level: 1 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run(); updateHeadingLevel(1)"
        title="Heading 1"
      >
        H1
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('heading', { level: 2 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run(); updateHeadingLevel(2)"
        title="Heading 2"
      >
        H2
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('heading', { level: 3 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run(); updateHeadingLevel(3)"
        title="Heading 3"
      >
        H3
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-button"
        :class="{ active: isActive('bold') }"
        @click="editor.chain().focus().toggleBold().run()"
        title="Bold"
      >
        B
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('italic') }"
        @click="editor.chain().focus().toggleItalic().run()"
        title="Italic"
      >
        I
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('underline') }"
        @click="editor.chain().focus().toggleUnderline().run()"
        title="Underline"
      >
        U
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('strike') }"
        @click="editor.chain().focus().toggleStrike().run()"
        title="Strike"
      >
        S
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('subscript') }"
        @click="editor.chain().focus().toggleSubscript().run()"
        title="Subscript"
      >
        X₂
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('superscript') }"
        @click="editor.chain().focus().toggleSuperscript().run()"
        title="Superscript"
      >
        X²
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('link') }"
        @click="setLink"
        title="Link"
      >
        Link
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-button"
        :class="{ active: isActive('bulletList') }"
        @click="editor.chain().focus().toggleBulletList().run()"
        title="Bullet List"
      >
        • List
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('orderedList') }"
        @click="editor.chain().focus().toggleOrderedList().run()"
        title="Numbered List"
      >
        1. List
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-button"
        :class="{ active: isActive('blockquote') }"
        @click="editor.chain().focus().toggleBlockquote().run()"
        title="Blockquote"
      >
        ""
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('code') }"
        @click="editor.chain().focus().toggleCode().run()"
        title="Code"
      >
        { }
      </button>
      <button
        class="toolbar-button"
        :class="{ active: isActive('codeBlock') }"
        @click="editor.chain().focus().toggleCodeBlock().run()"
        title="Code Block"
      >
        &lt;/&gt;
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-button"
        :class="{ active: isActive('taskList') }"
        @click="editor.chain().focus().toggleTaskList().run()"
        title="Task List"
      >
        ☑ Tasks
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-button"
        @click="insertTable"
        title="Insert Table"
      >
        Table
      </button>
      <button
        class="toolbar-button"
        @click="addAudio"
        title="Insert Audio"
      >
        Audio
      </button>
      <button
        class="toolbar-button"
        @click="addDetails"
        title="Insert Collapsible Section"
      >
        Details
      </button>
      <button
        class="toolbar-button"
        @click="editor.chain().focus().setHorizontalRule().run()"
        title="Horizontal Rule"
      >
        ---
      </button>
    </div>

    <div class="toolbar-divider"></div>

    <div class="toolbar-group">
      <button
        class="toolbar-button comment-btn"
        :class="{ active: isActive('comment') }"
        @click="addComment"
        title="Add Comment"
      >
        💬 Comment
      </button>
    </div>
  </div>
</template>

<style>
.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  padding: 0.5rem;
  gap: 0.25rem;
  align-items: center;
}

.toolbar-group {
  display: flex;
  gap: 0.25rem;
}

.toolbar-button {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2rem;
  height: 2rem;
  padding: 0 0.5rem;
  background-color: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 0.25rem;
  color: #475569;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.toolbar-button:hover {
  background-color: #f1f5f9;
}

.toolbar-button.active {
  background-color: #dbeafe;
  border-color: #60a5fa;
  color: #2563eb;
}

.toolbar-divider {
  width: 1px;
  height: 1.5rem;
  background-color: #e2e8f0;
  margin: 0 0.5rem;
}

.toolbar-button.comment-btn {
  background: linear-gradient(135deg, #fef9c3, #fde68a);
  border-color: #fde047;
  color: #854d0e;
}

.toolbar-button.comment-btn:hover {
  background: linear-gradient(135deg, #fde047, #facc15);
}

.toolbar-button.comment-btn.active {
  background: #facc15;
  color: #1e293b;
}

@media (max-width: 640px) {
  .editor-toolbar {
    justify-content: center;
    padding: 0.25rem;
  }

  .toolbar-button {
    min-width: 1.75rem;
    height: 1.75rem;
    padding: 0 0.25rem;
    font-size: 0.75rem;
  }

  .toolbar-divider {
    margin: 0 0.25rem;
  }
}
</style>
