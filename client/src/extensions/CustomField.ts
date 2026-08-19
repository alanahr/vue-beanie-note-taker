import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import CustomFieldComponent from '../components/CustomFieldComponent.vue'

export const CustomField = Node.create({
  name: 'customField',
  group: 'block',
  
  // Enforces structural layout: 1 label block, 1 content block
  content: 'customFieldLabel customFieldContent',
  
  defining: true,
  isolating: true,
  selectable: true,

  // Defines the label as an argument/property passed during instantiation
  addAttributes() {
    return {
      label: {
        default: 'Default Label',
        // Instructs Tiptap how to extract this property from incoming HTML/JSON
        parseHTML: element => element.getAttribute('data-label'),
        renderHTML: attributes => ({ 'data-label': attributes.label }),
      },
    }
  },

  parseHTML() {
    return [{ tag: 'div[data-type="custom-field"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'custom-field' }), 0]
  },

  addNodeView() {
    return VueNodeViewRenderer(CustomFieldComponent)
  },

  // Custom ProseMirror Plugin to trap and block complete node deletion
  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: new PluginKey('preventCustomFieldDeletion'),
        props: {
          handleKeyDown(view, event) {
            const { state } = view
            const { selection } = state
            
            // Intercept Backspace and Delete keys
            if (event.key === 'Backspace' || event.key === 'Delete') {
              let isTargetNodeSelected = false

              // Check if the user has selected the entire node block directly
              state.doc.nodesBetween(selection.from, selection.to, (node) => {
                if (node.type.name === 'customField') {
                  isTargetNodeSelected = true
                }
              })

              // Block the transaction if they attempt to delete the entire structural component
              if (isTargetNodeSelected) {
                event.preventDefault()
                return true
              }
            }
            return false
          },
        },
      }),
    ]
  },
})

// The Static Label Child Node
export const CustomFieldLabel = Node.create({
  name: 'customFieldLabel',
  group: 'block',
  content: 'text*', // Text only
  selectable: false,
  atom: true,

  parseHTML() {
    return [{ tag: 'div[data-type="custom-field-label"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'custom-field-label', contenteditable: 'false' }), 0]
  },
})

// The Restructured Content Child Node (Strictly unformatted plain text blocks)
export const CustomFieldContent = Node.create({
  name: 'customFieldContent',
  group: 'block',
  
  // 'text*' instead of 'paragraph+' strips out all nested block schemas and block elements
  content: 'text*', 
  // Marks: false explicitly bans bold, italic, underlines, links, and code spans
  marks: '', 
  
  selectable: false,
  defining: true,
  isolating: true,

  parseHTML() {
    return [{ tag: 'div[data-type="custom-field-content"]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'custom-field-content' }), 0]
  },
})

export default CustomField