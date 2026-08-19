# Tiptap Rich Text Editor — Vue 3 + TypeScript + Vite

A rich text editor built with [Tiptap v3](https://tiptap.dev), Vue 3 (`<script setup>` SFCs), and TypeScript, bundled with Vite. The editor supports a wide range of formatting options, tables, task lists, code blocks with syntax highlighting, comments, audio embeds, collapsible sections, and more. Documents are persisted locally with auto-save and can be shared via URL parameters.

## Features

### Text Formatting
- **Headings** — H1, H2, H3
- **Inline styles** — bold, italic, underline, strikethrough
- **Subscript and superscript**
- **Links** — add/remove via toolbar prompt
- **Inline code** and **code blocks** with syntax highlighting (via Lowlight)
- **Typography** — smart quotes, dashes, and other text replacements

### Block Content
- **Bullet lists** and **ordered lists**
- **Task lists** with checkboxes (supports nesting)
- **Blockquotes**
- **Horizontal rules**
- **Tables** — insert, navigate, and edit cells with resizable columns
- **Collapsible sections** (Details) — expandable/collapsible content blocks with summary

### Media
- **Audio embeds** — insert audio players via URL
- **File handler** — drag-and-drop or paste images directly into the editor

### Productivity
- **Comments** — select text and add comments; view, close, and remove comments from a dedicated panel
- **Find and Replace** — extension registered for search/replace functionality (UI panel to be added)
- **Unique IDs** — stable identifiers generated for headings, paragraphs, blockquotes, and code blocks
- **Table of Contents** — automatic heading tracking with update events
- **Node Range** — range-based node selection support

### Document Management
- **Auto-save** — content saved to localStorage every 5 seconds and on every change
- **Document UUID** — each document gets a unique identifier
- **URL-based loading** — open a document by passing `?doc=<uuid>` in the URL
- **JSON output** — live JSON preview of the document structure
- **Rendered preview** — live HTML preview of the document content

## Project Organization

```
.
├── index.html                  # App entry HTML, loads Google Fonts (Inter)
├── package.json                # Dependencies and scripts
├── vite.config.ts              # Vite configuration with Vue plugin
├── tsconfig.json               # TypeScript project references config
├── tsconfig.app.json           # TypeScript config for app source
├── tsconfig.node.json          # TypeScript config for Node/Vite
├── public/
│   └── vite.svg                # Favicon
└── src/
    ├── main.ts                 # Vue app bootstrap — mounts App to #app
    ├── App.vue                 # Root component — document bar, save flow, JSON & HTML preview
    ├── style.css               # Global styles, CSS variables, dark mode support
    ├── vite-env.d.ts           # Vite type declarations
    ├── assets/
    │   └── vue.svg             # Vue logo asset
    ├── components/
    │   ├── TiptapEditor.vue    # Core editor — configures all Tiptap extensions, handles auto-save
    │   ├── EditorToolbar.vue   # Formatting toolbar — headings, inline styles, lists, tables, media, comments
    │   └── CommentPanel.vue    # Comment management — add, list, close, and remove comments
    ├── extensions/
    │   └── Comment.ts          # Custom Tiptap mark extension for inline comments
    └── services/
        └── documentApi.ts      # Document persistence layer — localStorage-based CRUD with UUID support
```

## Tech Stack

| Layer         | Technology                                      |
| ------------- | ----------------------------------------------- |
| Framework     | Vue 3 (`<script setup>` SFCs)                   |
| Language      | TypeScript                                      |
| Build Tool    | Vite                                            |
| Editor Core   | Tiptap v3 (`@tiptap/vue-3`, `@tiptap/starter-kit`) |
| Syntax Highlight | Lowlight                                     |
| Persistence   | Browser localStorage (via `documentApi.ts`)     |

## Tiptap Extensions in Use

| Extension | Package |
| --------- | ------- |
| StarterKit (bold, italic, strike, link, underline, lists, blockquote, code, horizontal rule, etc.) | `@tiptap/starter-kit` |
| Subscript | `@tiptap/extension-subscript` |
| Superscript | `@tiptap/extension-superscript` |
| Text Style | `@tiptap/extension-text-style` |
| Audio | `@tiptap/extension-audio` |
| Task List / Task Item | `@tiptap/extension-list` |
| Table / TableRow / TableHeader / TableCell | `@tiptap/extension-table` |
| Details / DetailsSummary / DetailsContent | `@tiptap/extension-details` |
| Code Block (Lowlight) | `@tiptap/extension-code-block-lowlight` |
| Typography | `@tiptap/extension-typography` |
| Find and Replace | `@tiptap/extension-find-and-replace` |
| Node Range | `@tiptap/extension-node-range` |
| Hard Break | `@tiptap/extension-hard-break` |
| Unique ID | `@tiptap/extension-unique-id` |
| File Handler | `@tiptap/extension-file-handler` |
| Table of Contents | `@tiptap/extension-table-of-contents` |
| Comment (custom) | `src/extensions/Comment.ts` |

## Scripts

- `npm run dev` — start the Vite dev server
- `npm run build` — type-check with `vue-tsc` and build for production
- `npm run preview` — preview the production build locally
- `npm run test` — run all unit tests once (headless)
- `npm run test:watch` — run unit tests in watch mode (re-runs on file changes)
- `npm run test:ui` — run unit tests with the Vitest visual UI in the browser

## Unit Tests (Vitest)

The front-end uses [Vitest](https://vitest.dev) with [jsdom](https://github.com/jsdom/jsdom) and [@vue/test-utils](https://test-utils.vuejs.org/) for unit and component testing.

### Test Files

```
src/
├── components/
│   └── CommentPanel.spec.ts        # Comment panel rendering, toggle, button states
├── services/
│   └── documentApi.spec.ts         # API functions (fetch, save, delete, list) with mocked fetch
└── types/
    └── comment.spec.ts             # Comment type shape and document structure
```

### Running Tests

From the `client/` directory:

```bash
npm run test          # Run all tests once
npm run test:watch    # Watch mode — re-runs on file changes
npm run test:ui       # Opens the Vitest browser UI dashboard
```

### Configuration

- `vitest.config.ts` — Vitest configuration (jsdom environment, global test APIs, coverage settings)
- `tsconfig.vitest.json` — TypeScript config for test files (extends `tsconfig.app.json`)

### Writing New Tests

Create a `.spec.ts` or `.test.ts` file alongside the code it tests. Tests use the Vitest API with globals enabled (no imports needed for `describe`, `it`, `expect`):

```typescript
// src/components/MyComponent.spec.ts
import { mount } from '@vue/test-utils'
import MyComponent from './MyComponent.vue'

describe('MyComponent', () => {
  it('renders', () => {
    const wrapper = mount(MyComponent)
    expect(wrapper.find('.my-element').exists()).toBe(true)
  })
})
```

For API service tests, mock `globalThis.fetch` with `vi.spyOn` and return mock `Response` objects.


# TO DO
Read more about node views in Vue: https://tiptap.dev/docs/editor/extensions/custom-extensions/node-views/vue#tracking-node-position along with https://tiptap.dev/docs/editor/extensions/custom-extensions/node-views/vue

Then install/implement functionality from https://tiptap.dev/docs/editor/extensions/functionality/drag-handle-vue

Also see src/GuideNodeViews/DragHandle/Vue/, src/Examples/CustomParagraph/Vue/, src/Examples/CustomDocument/Vue/
