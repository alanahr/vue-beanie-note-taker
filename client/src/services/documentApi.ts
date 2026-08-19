import type { DocumentRecord } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002'

const generateUUID = (): string => {
  
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  //TODO - what is this... 
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export function createDocumentUUID(): string {
  // TODO what
  return generateUUID()
}

export async function fetchDocument(uuid: string): Promise<DocumentRecord | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/documents/${uuid}`)
    if (response.status === 404) return null
    if (!response.ok) throw new Error(`Failed to fetch document: ${response.statusText}`)
    const data = await response.json()
    return {
      uuid: data.uuid,
      content: data.content,
      updatedAt: data.updated_at,
    }
  } catch {
    return null
  }
}

export async function saveDocument(record: DocumentRecord): Promise<DocumentRecord> {
  const response = await fetch(`${API_BASE_URL}/api/documents`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      uuid: record.uuid,
      content: record.content,
      updated_at: record.updatedAt,
    }),
  })
  if (!response.ok) throw new Error(`Failed to save document: ${response.statusText}`)
  const data = await response.json()
  return {
    uuid: data.uuid,
    content: data.content,
    updatedAt: data.updated_at,
  }
}

export async function deleteDocument(uuid: string): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${uuid}`, {
    method: 'DELETE',
  })
  return response.ok
}

export async function listDocumentUUIDs(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/api/documents`)
  if (!response.ok) return []
  return response.json()
}
