import { Node } from '@tiptap/core'

export const FormHeader = Node.create({
  name: 'formHeader',
  group: 'block',
  content: 'block+', // Allows editable form blocks inside the container
  defining: true,

  parseHTML() {
    return [{ tag: 'div[data-type="form-header"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', { 'data-type': 'form-header', ...HTMLAttributes }, 0]
  },

  // Use a Node View to render an uneditable title alongside editable slots
  addNodeView() {
    return ({ node, HTMLAttributes }) => {
      const dom = document.createElement('div')
      dom.setAttribute('data-type', 'form-header')
      
      // 1. Create the completely static, uneditable header
      const title = document.createElement('h1')
      title.textContent = 'Static Form Title'
      title.setAttribute('contenteditable', 'false') // Disables typing/deletion
      title.style.userSelect = 'none' // Prevents text selection highlighting
      
      // 2. Create the container where the rest of the form content goes
      const contentDOM = document.createElement('div')
      contentDOM.className = 'form-content-area'

      dom.appendChild(title)
      dom.appendChild(contentDOM)

      return {
        dom,
        contentDOM, // Tiptap maps editable 'block+' content strictly here
      }
    }
  },
})
