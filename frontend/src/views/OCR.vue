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
          
          <!-- 显示分类建议 -->
          <div v-if="classification && !recognizing" class="classification-hint">
            <span class="hint-icon">{{ classification.type === 'schedule' ? '📅' : '📝' }}</span>
            <span class="hint-text">
              AI建议保存为<strong>{{ classification.type === 'schedule' ? '日程' : '备忘录' }}</strong>
              (置信度: {{ (classification.confidence * 100).toFixed(0) }}%)
            </span>
          </div>
          
          <OCRPreview
            :result="ocrResult"
            :loading="recognizing"
            :error="recognizeError"
            @retry="recognizeText"
            @save="handleSaveEdit"
            @saveAsSchedule="handleSaveAsSchedule"
            @saveAsMemo="handleSaveAsMemo"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FileUpload from '../components/FileUpload.vue'
import OCRPreview from '../components/OCRPreview.vue'
import { recognizeImage, editOCRResult, type OCRRecognizeResponse } from '../api/ocr'
import type { FileUploadResponse } from '../api/upload'
import { classifyText, type ClassifyResponse } from '../api/classification'
import { scheduleApi } from '../api/schedule'
import { memoApi } from '../api/memo'

const router = useRouter()
const uploadedFile = ref<FileUploadResponse | null>(null)
const recognizing = ref(false)
const recognizeError = ref<string | null>(null)
const ocrResult = ref<OCRRecognizeResponse | null>(null)
const classification = ref<ClassifyResponse | null>(null)

function handleFileUploaded(file: FileUploadResponse) {
  uploadedFile.value = file
  ocrResult.value = null
  recognizeError.value = null
  classification.value = null
}

function handleUploadError(error: string) {
  console.error('Upload error:', error)
}

async function recognizeText() {
  if (!uploadedFile.value) return
  
  recognizing.value = true
  recognizeError.value = null
  ocrResult.value = null
  classification.value = null
  
  try {
    const result = await recognizeImage(uploadedFile.value.file_id)
    
    if (result.success) {
      ocrResult.value = result
      
      // 自动分类识别的文本
      if (result.text) {
        try {
          const classifyResult = await classifyText(result.text)
          classification.value = classifyResult
          console.log('分类结果:', classifyResult)
        } catch (err) {
          console.error('分类失败:', err)
        }
      }
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
    
    // 重新分类编辑后的文本
    if (editedText) {
      try {
        const classifyResult = await classifyText(editedText)
        classification.value = classifyResult
      } catch (err) {
        console.error('重新分类失败:', err)
      }
    }
    
    alert('保存成功')
  } catch (err: any) {
    alert('保存失败：' + (err.response?.data?.detail || '请重试'))
  }
}

async function handleSaveAsSchedule() {
  if (!ocrResult.value?.text) {
    alert('没有可保存的内容')
    return
  }
  
  try {
    const data = classification.value?.extracted_data || {}
    
    await scheduleApi.create({
      date: data.date,
      time: data.time,
      description: data.description || ocrResult.value.text,
      original_text: ocrResult.value.text
    })
    
    alert('已保存为日程')
    router.push('/schedules')
  } catch (err: any) {
    alert('保存失败：' + (err.response?.data?.detail || '请重试'))
  }
}

async function handleSaveAsMemo() {
  if (!ocrResult.value?.text) {
    alert('没有可保存的内容')
    return
  }
  
  try {
    const data = classification.value?.extracted_data || {}
    
    await memoApi.create({
      content: ocrResult.value.text,
      summary: data.summary || ocrResult.value.text.substring(0, 50),
      tags: data.tags
    })
    
    alert('已保存为备忘录')
    router.push('/memos')
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

.classification-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.hint-icon {
  font-size: 1.5rem;
}

.hint-text {
  color: #0369a1;
  font-size: 0.875rem;
}

.hint-text strong {
  font-weight: 600;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .ocr-page {
    padding: 1rem 0.5rem;
  }
  
  .classification-hint {
    flex-direction: column;
    text-align: center;
  }
}
</style>
