<template>
  <div class="ocr-page">
    <div class="container">
      <h1 class="page-title">文字识别</h1>
      
      <div class="ocr-content">
        <div class="upload-section">
          <h2 class="section-title">上传图片</h2>
          <FileUpload @uploaded="handleFileUploaded" @error="handleUploadError" />
        </div>

        <div v-if="uploadedFile" class="recognize-section">
          <button
            @click="recognizeText"
            :disabled="recognizing"
            class="btn-recognize"
          >
            {{ recognizing ? '识别中...' : '开始识别' }}
          </button>
        </div>

        <div v-if="ocrResult || recognizing || recognizeError" class="result-section">
          <h2 class="section-title">识别结果</h2>
          <OCRPreview
            :result="ocrResult"
            :loading="recognizing"
            :error="recognizeError"
            @retry="recognizeText"
            @save="handleSaveEdit"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from '../components/FileUpload.vue'
import OCRPreview from '../components/OCRPreview.vue'
import { recognizeImage, editOCRResult, type OCRRecognizeResponse } from '../api/ocr'
import type { FileUploadResponse } from '../api/upload'

const uploadedFile = ref<FileUploadResponse | null>(null)
const recognizing = ref(false)
const recognizeError = ref<string | null>(null)
const ocrResult = ref<OCRRecognizeResponse | null>(null)

function handleFileUploaded(file: FileUploadResponse) {
  uploadedFile.value = file
  ocrResult.value = null
  recognizeError.value = null
}

function handleUploadError(error: string) {
  console.error('Upload error:', error)
}

async function recognizeText() {
  if (!uploadedFile.value) return
  
  recognizing.value = true
  recognizeError.value = null
  ocrResult.value = null
  
  try {
    const result = await recognizeImage(uploadedFile.value.file_id)
    
    if (result.success) {
      ocrResult.value = result
    } else {
      recognizeError.value = result.error || '识别失败'
    }
  } catch (err: any) {
    recognizeError.value = err.response?.data?.detail || '识别失败，请重试'
  } finally {
    recognizing.value = false
  }
}

async function handleSaveEdit(editedText: string) {
  if (!uploadedFile.value) return
  
  try {
    await editOCRResult(uploadedFile.value.file_id, editedText)
    
    // 更新本地结果
    if (ocrResult.value) {
      ocrResult.value = {
        ...ocrResult.value,
        text: editedText
      }
    }
    
    alert('保存成功')
  } catch (err: any) {
    alert('保存失败：' + (err.response?.data?.detail || '请重试'))
  }
}
</script>

<style scoped>
.ocr-page {
  min-height: 100vh;
  background: #f3f4f6;
  padding: 2rem 1rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 2rem 0;
  text-align: center;
}

.ocr-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
}

.upload-section,
.recognize-section,
.result-section {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.recognize-section {
  text-align: center;
}

.btn-recognize {
  padding: 0.75rem 2rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-recognize:hover:not(:disabled) {
  background: #2563eb;
}

.btn-recognize:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .ocr-page {
    padding: 1rem 0.5rem;
  }
}
</style>
