<template>
  <div class="file-upload">
    <div class="upload-area" @click="triggerFileInput" @drop.prevent="handleDrop" @dragover.prevent>
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/bmp"
        @change="handleFileSelect"
        style="display: none"
      />
      
      <div v-if="!uploading && !uploadedFile" class="upload-prompt">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="upload-text">点击或拖拽图片到此处上传</p>
        <p class="upload-hint">支持 JPG、PNG、BMP 格式，最大 10MB</p>
      </div>

      <div v-else-if="uploading" class="uploading">
        <div class="spinner"></div>
        <p>上传中...</p>
      </div>

      <div v-else-if="uploadedFile" class="uploaded">
        <svg class="success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <p class="success-text">{{ uploadedFile.filename }}</p>
        <p class="success-hint">{{ formatFileSize(uploadedFile.file_size) }}</p>
        <button @click.stop="clearFile" class="btn-clear">重新上传</button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { uploadFile, type FileUploadResponse } from '../api/upload'

const emit = defineEmits<{
  uploaded: [file: FileUploadResponse]
  error: [error: string]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadedFile = ref<FileUploadResponse | null>(null)
const error = ref<string | null>(null)

function triggerFileInput() {
  fileInput.value?.click()
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    await handleFile(file)
  }
}

async function handleDrop(event: DragEvent) {
  const file = event.dataTransfer?.files[0]
  if (file) {
    await handleFile(file)
  }
}

async function handleFile(file: File) {
  error.value = null
  
  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
  if (!validTypes.includes(file.type)) {
    error.value = '不支持的文件格式，请上传 JPG、PNG 或 BMP 图片'
    return
  }
  
  // 验证文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    error.value = '文件大小超过 10MB 限制'
    return
  }
  
  uploading.value = true
  
  try {
    const response = await uploadFile(file)
    uploadedFile.value = response
    emit('uploaded', response)
  } catch (err: any) {
    error.value = err.response?.data?.detail || '上传失败，请重试'
    emit('error', error.value)
  } finally {
    uploading.value = false
  }
}

function clearFile() {
  uploadedFile.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #3b82f6;
  background: #f9fafb;
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-icon {
  width: 48px;
  height: 48px;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  margin: 0 0 0.5rem 0;
}

.upload-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.uploading {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner {
  width: 40px;
  height: 40px;
  margin-bottom: 1rem;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.uploaded {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.success-icon {
  width: 48px;
  height: 48px;
  color: #10b981;
  margin-bottom: 1rem;
}

.success-text {
  font-size: 1rem;
  font-weight: 500;
  color: #374151;
  margin: 0 0 0.25rem 0;
}

.success-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 1rem 0;
}

.btn-clear {
  padding: 0.5rem 1rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-clear:hover {
  background: #4b5563;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}
</style>
