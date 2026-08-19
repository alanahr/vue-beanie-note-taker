/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string
  readonly VITE_SUPABASE_ANON_KEY: string
  readonly VITE_STORAGE_PREFIX: string
  readonly VITE_NETWORK_DELAY: string
  readonly VITE_AUTOSAVE_INTERVAL: string
  readonly VITE_CONTENT_KEY: string
  readonly VITE_ALLOWED_MIME_TYPES: string
  readonly VITE_DEFAULT_COMMENT_USER: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
