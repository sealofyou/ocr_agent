<template>
  <div class="ocr-preview">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>正在识别文字...</p>
    </div>

    <div v-else-if="error" class="error">
      <p class="error-message">{{ error }}</p>
      <button @click="$emit('retry')" class="btn-retry">重试</button>
    </div>

    <div v-else-if="result" class="result">
      <div class="result-header">
        <h3>识别结果</h3>
        <button @click="toggleEdit" class="btn-edit">
          {{ isEditing ? '取消编辑' : '编辑' }}
        </button>
      </div>

      <div v-if="!isEditing" class="result-text">
        <pre>{{ result.text || '未识别到文字' }}</pre>
      </div>

      <div v-else class="result-edit">
        <textarea
          v-model="editedText"
          class="edit-textarea"
          rows="10"
          placeholder="编辑识别结果..."
        ></textarea>
        <div class="edit-actions">
          <button @click="saveEdit" class="btn-save">保存</button>
          <button @click="cancelEdit" class="btn-cancel">取消</button>
        </div>
      </div>

      <!-- 保存到日程/备忘录 -->
      <div class="save-section">
        <h4>保存为</h4>
        <div class="save-buttons">
          <button @click="$emit('saveAsSchedule')" class="btn-save-schedule">
            📅 保存为日程
          </button>
          <button @click="$emit('saveAsMemo')" class="btn-save-memo">
            📝 保存为备忘录
          </button>
        </div>
      </div>

      <div v-if="result.details && result.details.length > 0" class="result-details">
        <h4>详细信息</h4>
        <div class="details-list">
          <div
            v-for="(detail, index) in result.details"
            :key="index"
            class="detail-item"
          >
            <span class="detail-text">{{ detail.text }}</span>
            <span class="detail-confidence">
              置信度: {{ (detail.confidence * 100).toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { OCRRecognizeResponse } from '../api/ocr'

interface Props {
  result: OCRRecognizeResponse | null
  loading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: null
})

const emit = defineEmits<{
  retry: []
  save: [text: string]
  saveAsSchedule: []
  saveAsMemo: []
}>()

const isEditing = ref(false)
const editedText = ref('')

watch(() => props.result, (newResult) => {
  if (newResult) {
    editedText.value = newResult.text
  }
}, { immediate: true })

function toggleEdit() {
  isEditing.value = !isEditing.value
  if (isEditing.value && props.result) {
    editedText.value = props.result.text
  }
}

function saveEdit() {
  emit('save', editedText.value)
  isEditing.value = false
}

function cancelEdit() {
  if (props.result) {
    editedText.value = props.result.text
  }
  isEditing.value = false
}
</script>

<style scoped>
.ocr-preview {
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 2rem;
}

.error-message {
  color: #ef4444;
  margin-bottom: 1rem;
}

.btn-retry {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-retry:hover {
  background: #2563eb;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.result-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-edit {
  padding: 0.5rem 1rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-edit:hover {
  background: #4b5563;
}

.result-text pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.25rem;
  margin: 0;
}

.result-edit {
  margin-bottom: 1rem;
}

.edit-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-family: inherit;
  font-size: 0.875rem;
  resize: vertical;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.btn-save {
  padding: 0.5rem 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-save:hover {
  background: #059669;
}

.btn-cancel {
  padding: 0.5rem 1rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #4b5563;
}

.result-details {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.result-details h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.details-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 0.25rem;
}

.detail-text {
  flex: 1;
  font-size: 0.875rem;
}

.detail-confidence {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 1rem;
}

.save-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.save-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.save-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-save-schedule,
.btn-save-memo {
  flex: 1;
  min-width: 150px;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save-schedule {
  background: #3b82f6;
  color: white;
}

.btn-save-schedule:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
}

.btn-save-memo {
  background: #10b981;
  color: white;
}

.btn-save-memo:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.3);
}
</style>
