import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  createDocumentUUID,
  fetchDocument,
  saveDocument,
  deleteDocument,
  listDocumentUUIDs,
} from './documentApi'
import type { DocumentRecord } from '../types'

const API_BASE_URL = 'http://localhost:8002'

function mockFetchResponse(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: 'OK',
    json: async () => body,
  } as Response
}

describe('documentApi', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_API_BASE_URL', API_BASE_URL)
    vi.restoreAllMocks()
  })

  describe('createDocumentUUID', () => {
    it('returns a string', () => {
      const uuid = createDocumentUUID()
      expect(typeof uuid).toBe('string')
      expect(uuid.length).toBeGreaterThan(0)
    })

    it('returns unique values across calls', () => {
      const a = createDocumentUUID()
      const b = createDocumentUUID()
      expect(a).not.toBe(b)
    })
  })

  describe('fetchDocument', () => {
    it('returns null for a 404 response', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        mockFetchResponse(404, { detail: 'Not found' }),
      )
      const result = await fetchDocument('missing-uuid')
      expect(result).toBeNull()
    })

    it('returns a DocumentRecord on success', async () => {
      const body = {
        uuid: 'doc-1',
        content: { type: 'doc', content: [] },
        updated_at: '2026-01-01T00:00:00.000Z',
      }
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(mockFetchResponse(200, body))
      const result = await fetchDocument('doc-1')
      expect(result).toEqual<DocumentRecord>({
        uuid: 'doc-1',
        content: { type: 'doc', content: [] },
        updatedAt: '2026-01-01T00:00:00.000Z',
      })
    })

    it('returns null when fetch throws', async () => {
      vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Network error'))
      const result = await fetchDocument('doc-1')
      expect(result).toBeNull()
    })
  })

  describe('saveDocument', () => {
    it('sends a PUT request and returns the saved record', async () => {
      const body = {
        uuid: 'doc-1',
        content: { type: 'doc', content: [] },
        updated_at: '2026-01-02T00:00:00.000Z',
      }
      const fetchSpy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(mockFetchResponse(200, body))

      const record: DocumentRecord = {
        uuid: 'doc-1',
        content: { type: 'doc', content: [] },
        updatedAt: '2026-01-01T00:00:00.000Z',
      }

      const result = await saveDocument(record)
      expect(fetchSpy).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/documents`,
        expect.objectContaining({ method: 'PUT' }),
      )
      expect(result.updatedAt).toBe('2026-01-02T00:00:00.000Z')
    })

    it('throws when the response is not ok', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        mockFetchResponse(500, { detail: 'Server error' }),
      )
      await expect(
        saveDocument({
          uuid: 'doc-1',
          content: { type: 'doc', content: [] },
          updatedAt: '2026-01-01T00:00:00.000Z',
        }),
      ).rejects.toThrow()
    })
  })

  describe('deleteDocument', () => {
    it('returns true on a successful deletion', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(mockFetchResponse(204, null))
      const result = await deleteDocument('doc-1')
      expect(result).toBe(true)
    })

    it('returns false on a failed deletion', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(mockFetchResponse(404, null))
      const result = await deleteDocument('doc-1')
      expect(result).toBe(false)
    })
  })

  describe('listDocumentUUIDs', () => {
    it('returns an array of UUIDs on success', async () => {
      const uuids = ['doc-1', 'doc-2', 'doc-3']
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        mockFetchResponse(200, uuids),
      )
      const result = await listDocumentUUIDs()
      expect(result).toEqual(uuids)
    })

    it('returns an empty array when the request fails', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        mockFetchResponse(500, null),
      )
      const result = await listDocumentUUIDs()
      expect(result).toEqual([])
    })
  })
})
