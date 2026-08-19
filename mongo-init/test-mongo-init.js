// MongoDB test seed script
// Runs automatically on first container initialization via /docker-entrypoint-initdb.d/
// Seeds both the primary data database (tiptap_editor) and the RAG database (tiptap_rag)
// with sample documents, comments, and embeddings for end-to-end testing.

// ── Primary data database: tiptap_editor ──────────────────────────────────────

const dataDb = db.getSiblingDB('tiptap_editor');

// --- documents collection ---
dataDb.documents.drop();
dataDb.documents.insertMany([
  {
    uuid: 'test-doc-0001',
    content: {
      type: 'doc',
      content: [
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'Test Document Heading' }],
        },
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'This is a test paragraph with ' },
            { type: 'text', marks: [{ type: 'bold' }], text: 'bold text' },
            { type: 'text', text: ' and ' },
            { type: 'text', marks: [{ type: 'italic' }], text: 'italic text' },
            { type: 'text', text: '.' },
          ],
        },
      ],
    },
    updated_at: '2026-08-18T00:00:00.000Z',
  },
  {
    uuid: 'test-doc-0002',
    content: {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: 'A second document for testing list and delete endpoints.' }],
        },
      ],
    },
    updated_at: '2026-08-18T00:00:01.000Z',
  },
  {
    uuid: 'test-doc-0003',
    content: {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Document with a ' },
            {
              type: 'text',
              marks: [
                {
                  type: 'comment',
                  attrs: {
                    comment: 'This needs review',
                    user: 'admin',
                    createdAt: '2026-08-18T00:00:02.000Z',
                    closed: false,
                    range: { from: 16, to: 24 },
                  },
                },
              ],
              text: 'commented',
            },
            { type: 'text', text: ' section.' },
          ],
        },
      ],
    },
    updated_at: '2026-08-18T00:00:02.000Z',
  },
]);
dataDb.documents.createIndex({ uuid: 1 }, { unique: true });
print('Seeded tiptap_editor.documents: ' + dataDb.documents.countDocuments() + ' records');

// --- comments collection ---
dataDb.comments.drop();
dataDb.comments.insertMany([
  {
    comment_id: 'comment-0001',
    document_uuid: 'test-doc-0003',
    text: 'commented',
    comment: 'This needs review',
    user: 'admin',
    created_at: '2026-08-18T00:00:02.000Z',
    closed: false,
    range: { from: 16, to: 24 },
  },
  {
    comment_id: 'comment-0002',
    document_uuid: 'test-doc-0001',
    text: 'bold text',
    comment: 'Consider rephrasing this',
    user: 'reviewer',
    created_at: '2026-08-18T00:00:03.000Z',
    closed: true,
    range: { from: 26, to: 35 },
  },
]);
dataDb.comments.createIndex({ comment_id: 1 }, { unique: true });
dataDb.comments.createIndex({ document_uuid: 1 });
print('Seeded tiptap_editor.comments: ' + dataDb.comments.countDocuments() + ' records');

// ── RAG database: tiptap_rag ──────────────────────────────────────────────────

const ragDb = db.getSiblingDB('tiptap_rag');

// --- embeddings collection ---
ragDb.embeddings.drop();
ragDb.embeddings.insertMany([
  {
    document_uuid: 'test-doc-0001',
    chunk_text: 'Test Document Heading',
    embedding: [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08],
    created_at: '2026-08-18T00:00:00.000Z',
  },
  {
    document_uuid: 'test-doc-0001',
    chunk_text: 'This is a test paragraph with bold text and italic text.',
    embedding: [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09],
    created_at: '2026-08-18T00:00:01.000Z',
  },
  {
    document_uuid: 'test-doc-0003',
    chunk_text: 'Document with a commented section.',
    embedding: [0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
    created_at: '2026-08-18T00:00:02.000Z',
  },
]);
ragDb.embeddings.createIndex({ document_uuid: 1 });
print('Seeded tiptap_rag.embeddings: ' + ragDb.embeddings.countDocuments() + ' records');

print('Test MongoDB seed complete.');
