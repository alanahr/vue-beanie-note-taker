<template>
  <node-view-wrapper class="custom-field-wrapper">
    <!-- First Child: Label Area rendered dynamically from props -->
    <div 
      class="field-label-lock" 
      contenteditable="false" 
      @selectstart.prevent
    >
      <span class="lock-icon">📋</span> {{ node.attrs.label }}:
    </div>

    <!-- Second Child: Editable, strictly plain-text container -->
    <node-view-content class="field-content-plain" />
  </node-view-wrapper>
</template>

<script setup>
import { NodeViewContent, NodeViewWrapper } from '@tiptap/vue-3'

defineProps({
  node: { type: Object, required: true },
  updateAttributes: { type: Function, required: true },
})
</script>

<style scoped>
.custom-field-wrapper {
  border: 1px solid #ced4da;
  border-radius: 6px;
  padding: 12px;
  margin: 16px 0;
  background-color: #fdfdfd;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label-lock {
  font-weight: 600;
  color: #495057;
  user-select: none;
  cursor: not-allowed;
  font-size: 0.9rem;
}

.field-content-plain {
  border: 1px solid #e9ecef;
  padding: 8px;
  background: #ffffff;
  border-radius: 4px;
  min-height: 24px;
  font-family: inherit;
}
/* Ensure styling cues inside look unformatted even if system attempts to drop HTML markup */
.field-content-plain :deep(*) {
  font-weight: normal !important;
  font-style: normal !important;
  text-decoration: none !important;
}
</style>
