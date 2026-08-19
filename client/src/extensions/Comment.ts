import { Mark, mergeAttributes, getMarkRange } from '@tiptap/core'
import type { CommentAttrs, CommentRange } from '../types'

const defaults = (): CommentAttrs => ({
  comment: '',
  user: import.meta.env.VITE_DEFAULT_COMMENT_USER || 'admin',
  createdAt: new Date().toISOString(),
  closed: false,
  range: null,
})

export const Comment = Mark.create({
  name: 'comment',

  inclusive: false,

  excludes: '',

  addOptions() {
    return {
      HTMLAttributes: {
        class: 'comment-mark',
      },
    }
  },

  addAttributes() {
    return {
      comment: {
        default: '',
      },
      user: {
        default: import.meta.env.VITE_DEFAULT_COMMENT_USER || 'admin',
      },
      createdAt: {
        default: new Date().toISOString(),
      },
      closed: {
        default: false,
      },
      range: {
        default: null,
        rendered: false,
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-comment]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    const attrs = mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
      'data-comment': HTMLAttributes.comment,
      'data-user': HTMLAttributes.user,
      'data-closed': String(HTMLAttributes.closed),
    })
    return ['span', attrs, 0]
  },

  addCommands() {
    return {
      setComment:
        (attrs) =>
        ({ commands, state }) => {
          const { from, to } = state.selection
          return commands.setMark(this.name, {
            ...defaults(),
            range: { from, to },
            ...attrs,
          })
        },
      toggleComment:
        (attrs) =>
        ({ commands, state }) => {
          const { from, to } = state.selection
          return commands.toggleMark(this.name, {
            ...defaults(),
            range: { from, to },
            ...attrs,
          })
        },
      unsetComment:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name)
        },
      updateComment:
        (attrs) =>
        ({ tr, state }) => {
          let modified = false
          state.doc.descendants((node, pos) => {
            node.marks.forEach((mark) => {
              if (mark.type.name === this.name) {
                const from = pos
                const to = pos + node.nodeSize
                let range: CommentRange | null = null
                try {
                  const $pos = state.doc.resolve(from)
                  const computed = getMarkRange($pos, mark.type)
                  if (computed) {
                    range = { from: computed.from, to: computed.to }
                  }
                } catch {
                  range = { from, to }
                }
                tr.removeMark(from, to, mark.type)
                tr.addMark(
                  from,
                  to,
                  mark.type.create({
                    ...mark.attrs,
                    range,
                    ...attrs,
                  })
                )
                modified = true
              }
            })
            return true
          })
          return modified
        },
    }
  },
})

export default Comment
