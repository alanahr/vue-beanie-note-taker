export interface CommentRange {
  from: number
  to: number
}

export interface CommentAttrs {
  comment: string
  user: string
  createdAt: string
  closed: boolean
  range: CommentRange | null
}

export interface CommentItem {
  id: string
  text: string
  comment: string
  user: string
  createdAt: string
  closed: boolean
  range: CommentRange | null
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    comment: {
      setComment: (attrs: Partial<CommentAttrs>) => ReturnType
      toggleComment: (attrs: Partial<CommentAttrs>) => ReturnType
      unsetComment: () => ReturnType
      updateComment: (attrs: Partial<CommentAttrs>) => ReturnType
    }
  }
}
