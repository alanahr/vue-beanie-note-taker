import { Node, mergeAttributes } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'

export const ProtectedToken = Node.create({
  name: 'protectedToken',

  // Defines it as an inline block (like a badge or pill)
  group: 'inline',
  inline: true,
  
  // Crucial: treats the entire node as a single unit
  atom: true, 
  
  // Prevents typing inside the node
  selectable: true,

  addAttributes() {
    return {
      // Stores your JSON data structure
      jsonData: {
        default: {},
        // Parses JSON from the HTML attribute
        parseHTML: element => {
          try {
            return JSON.parse(element.getAttribute('data-json') || '{}')
          } catch {
            return {}
          }
        },
        // Renders JSON into the HTML attribute
        renderHTML: attributes => {
          return {
            'data-json': JSON.stringify(attributes.jsonData),
          }
        },
      },
      label: {
        default: 'Protected',
        parseHTML: element => element.innerText,
        renderHTML: attributes => ({ 'data-label': attributes.label })
      }
    }
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-protected-token]',
      },
    ]
  },

  renderHTML({ HTMLAttributes, node }) {
    return [
      'span',
      mergeAttributes(HTMLAttributes, { 
        'data-protected-token': '',
        'contenteditable': 'false', // Prevents internal editing
        'class': 'protected-node'  // For custom styling
      }),
      node.attrs.label,
    ]
  },

  addProseMirrorPlugins() {
    const extensionName = this.name

    return [
      new Plugin({
        key: new PluginKey('preventDeletion'),
        filterTransaction(transaction, state) {
          if (!transaction.docChanged) return true

          let shouldAllow = true
          const oldDoc = state.doc
          const newDoc = transaction.doc

          // Count target nodes before and after the transaction
          let oldNodeCount = 0
          let newNodeCount = 0

          oldDoc.descendants((node) => {
            if (node.type.name === extensionName) oldNodeCount++
          })
          
          newDoc.descendants((node) => {
            if (node.type.name === extensionName) newNodeCount++
          })

          // If the count drops, a deletion occurred—reject the transaction
          if (newNodeCount < oldNodeCount) {
            shouldAllow = false
          }

          return shouldAllow
        },
      }),
    ]
  },
  // Commands to programmatically insert the token
  addCommands() {
    return {
      insertToken:
        (attributes) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: attributes,
          })
        },
    }
  },
})

export default ProtectedToken