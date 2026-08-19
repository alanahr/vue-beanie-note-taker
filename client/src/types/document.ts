import type { JSONContent } from '@tiptap/vue-3'

export interface DocumentRecord {
  uuid: string
  content: JSONContent
  updatedAt: string
}
