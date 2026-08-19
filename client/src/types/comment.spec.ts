import { describe, it, expect } from 'vitest'
import type { JSONContent } from '@tiptap/vue-3'
import type { CommentItem, CommentRange } from '../types'

function buildDocWithComment(overrides: Partial<CommentItem> = {}): JSONContent {
  const comment: string = overrides.comment ?? 'Nice point'
  const user: string = overrides.user ?? 'admin'
  const createdAt: string = overrides.createdAt ?? '2026-01-01T00:00:00.000Z'
  const closed: boolean = overrides.closed ?? false
  const range: CommentRange | null = overrides.range ?? null

  return {
    type: 'doc',
    content: [
      {
        type: 'paragraph',
        content: [
          {
            type: 'text',
            text: overrides.text ?? 'highlighted text',
            marks: [
              {
                type: 'comment',
                attrs: { comment, user, createdAt, closed, range },
              },
            ],
          },
        ],
      },
    ],
  }
}

describe('CommentItem type shape', () => {
  it('produces a JSONContent doc with a comment mark', () => {
    const doc = buildDocWithComment()
    expect(doc.type).toBe('doc')
    const para = doc.content![0]
    expect(para.type).toBe('paragraph')
    const textNode = para.content![0]
    expect(textNode.marks).toBeDefined()
    expect(textNode.marks![0].type).toBe('comment')
  })

  it('preserves comment text and metadata in the mark attrs', () => {
    const doc = buildDocWithComment({
      comment: 'Review needed',
      user: 'reviewer',
      text: 'check this',
    })
    const mark = doc.content![0].content![0].marks![0]
    expect(mark.attrs.comment).toBe('Review needed')
    expect(mark.attrs.user).toBe('reviewer')
    expect(doc.content![0].content![0].text).toBe('check this')
  })

  it('supports an open and closed state', () => {
    const openDoc = buildDocWithComment({ closed: false })
    const closedDoc = buildDocWithComment({ closed: true })
    expect(openDoc.content![0].content![0].marks![0].attrs.closed).toBe(false)
    expect(closedDoc.content![0].content![0].marks![0].attrs.closed).toBe(true)
  })

  it('supports an optional range', () => {
    const withRange = buildDocWithComment({ range: { from: 5, to: 10 } })
    const mark = withRange.content![0].content![0].marks![0]
    expect(mark.attrs.range).toEqual({ from: 5, to: 10 })
  })

  it('allows a null range', () => {
    const noRange = buildDocWithComment({ range: null })
    const mark = noRange.content![0].content![0].marks![0]
    expect(mark.attrs.range).toBeNull()
  })
})
