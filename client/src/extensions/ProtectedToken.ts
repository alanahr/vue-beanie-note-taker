import { Node, mergeAttributes } from '@tiptap/core'

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
