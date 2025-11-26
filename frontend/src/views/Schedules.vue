<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">我的日程</h1>
        <p class="mt-2 text-gray-600">管理您的日程安排</p>
      </div>

      <!-- 创建日程表单 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">创建新日程</h2>
        <form @submit.prevent="createSchedule">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                日期
              </label>
              <input
                v-model="newSchedule.date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                时间
              </label>
              <input
                v-model="newSchedule.time"
                type="time"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              事件描述 *
            </label>
            <input
              v-model="newSchedule.description"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入事件描述..."
              required
            />
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              原始文本
            </label>
            <textarea
              v-model="newSchedule.originalText"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="原始文本（可选）"
            ></textarea>
          </div>

          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="loading"
              class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {{ loading ? '创建中...' : '创建日程' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 日期范围筛选 -->
      <div class="bg-white rounded-lg shadow-md p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              开始日期
            </label>
            <input
              v-model="dateFilter.startDate"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              结束日期
            </label>
            <input
              v-model="dateFilter.endDate"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div class="flex gap-2">
            <button
              @click="loadSchedules"
              class="flex-1 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              筛选
            </button>
            <button
              @click="clearFilter"
              class="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
            >
              清除
            </button>
          </div>
        </div>
      </div>

      <!-- 日程列表 -->
      <div v-if="loading && schedules.length === 0" class="text-center py-12">
        <p class="text-gray-500">加载中...</p>
      </div>

      <div v-else-if="schedules.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无日程</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="schedule in schedules"
          :key="schedule.id"
          class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <!-- 编辑模式 -->
          <div v-if="editingId === schedule.id">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <input
                v-model="editForm.date"
                type="date"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                v-model="editForm.time"
                type="time"
                class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <input
              v-model="editForm.description"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
              placeholder="事件描述"
            />
            <textarea
              v-model="editForm.originalText"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
              placeholder="原始文本"
            ></textarea>
            <div class="flex justify-end gap-2">
              <button
                @click="cancelEdit"
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                取消
              </button>
              <button
                @click="saveSchedule(schedule.id)"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                保存
              </button>
            </div>
          </div>

          <!-- 查看模式 -->
          <div v-else>
            <div class="flex items-start justify-between mb-3">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-lg font-semibold text-blue-600">
                    {{ formatDateTime(schedule.date, schedule.time) }}
                  </span>
                </div>
                <h3 class="text-xl font-medium text-gray-900 mb-2">
                  {{ schedule.description }}
                </h3>
                <p v-if="schedule.original_text" class="text-gray-600 text-sm">
                  原文：{{ schedule.original_text }}
                </p>
              </div>
            </div>

            <div class="flex items-center justify-between text-sm text-gray-500 pt-3 border-t">
              <span>创建于 {{ formatDate(schedule.created_at) }}</span>
              <div class="flex gap-2">
                <button
                  @click="startEdit(schedule)"
                  class="px-3 py-1 text-blue-600 hover:text-blue-800"
                >
                  编辑
                </button>
                <button
                  @click="deleteSchedule(schedule.id)"
                  class="px-3 py-1 text-red-600 hover:text-red-800"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { scheduleApi, type Schedule } from '../api/schedule'

const schedules = ref<Schedule[]>([])
const loading = ref(false)

const dateFilter = ref({
  startDate: '',
  endDate: ''
})

const newSchedule = ref({
  date: '',
  time: '',
  description: '',
  originalText: ''
})

const editingId = ref<string | null>(null)
const editForm = ref({
  date: '',
  time: '',
  description: '',
  originalText: ''
})

// 加载日程列表
const loadSchedules = async () => {
  try {
    loading.value = true
    const response = await scheduleApi.list(
      dateFilter.value.startDate || undefined,
      dateFilter.value.endDate || undefined
    )
    schedules.value = response.schedules
  } catch (error) {
    console.error('加载日程失败:', error)
    alert('加载日程失败')
  } finally {
    loading.value = false
  }
}

// 创建日程
const createSchedule = async () => {
  try {
    loading.value = true
    await scheduleApi.create({
      date: newSchedule.value.date || undefined,
      time: newSchedule.value.time || undefined,
      description: newSchedule.value.description,
      original_text: newSchedule.value.originalText || newSchedule.value.description
    })

    newSchedule.value.date = ''
    newSchedule.value.time = ''
    newSchedule.value.description = ''
    newSchedule.value.originalText = ''
    await loadSchedules()
  } catch (error: any) {
    console.error('创建日程失败:', error)
    alert(error.response?.data?.detail || '创建日程失败')
  } finally {
    loading.value = false
  }
}

// 开始编辑
const startEdit = (schedule: Schedule) => {
  editingId.value = schedule.id
  editForm.value.date = schedule.date || ''
  editForm.value.time = schedule.time || ''
  editForm.value.description = schedule.description
  editForm.value.originalText = schedule.original_text
}

// 取消编辑
const cancelEdit = () => {
  editingId.value = null
  editForm.value.date = ''
  editForm.value.time = ''
  editForm.value.description = ''
  editForm.value.originalText = ''
}

// 保存日程
const saveSchedule = async (id: string) => {
  try {
    await scheduleApi.update(id, {
      date: editForm.value.date || undefined,
      time: editForm.value.time || undefined,
      description: editForm.value.description,
      original_text: editForm.value.originalText
    })

    editingId.value = null
    await loadSchedules()
  } catch (error) {
    console.error('更新日程失败:', error)
    alert('更新日程失败')
  }
}

// 删除日程
const deleteSchedule = async (id: string) => {
  if (!confirm('确定要删除这个日程吗？')) return

  try {
    await scheduleApi.delete(id)
    await loadSchedules()
  } catch (error) {
    console.error('删除日程失败:', error)
    alert('删除日程失败')
  }
}

// 清除筛选
const clearFilter = () => {
  dateFilter.value.startDate = ''
  dateFilter.value.endDate = ''
  loadSchedules()
}

// 格式化日期时间
const formatDateTime = (date: string | null, time: string | null): string => {
  return scheduleApi.formatDateTime(date, time)
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadSchedules()
})
</script>


<style scoped>
/* 页面容器 */
.min-h-screen {
  min-height: 100vh;
}

.bg-gray-50 {
  background-color: #f9fafb;
}

.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.max-w-4xl {
  max-width: 56rem;
}

.mx-auto {
  margin-left: auto;
  margin-right: auto;
}

.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}

/* 间距 */
.mb-8 {
  margin-bottom: 2rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.pt-3 {
  padding-top: 0.75rem;
}

/* 文字大小 */
.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}

.text-xl {
  font-size: 1.25rem;
  line-height: 1.75rem;
}

.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

/* 字体粗细 */
.font-bold {
  font-weight: 700;
}

.font-semibold {
  font-weight: 600;
}

.font-medium {
  font-weight: 500;
}

/* 颜色 */
.text-gray-900 {
  color: #111827;
}

.text-gray-800 {
  color: #1f2937;
}

.text-gray-700 {
  color: #374151;
}

.text-gray-600 {
  color: #4b5563;
}

.text-gray-500 {
  color: #6b7280;
}

.text-blue-600 {
  color: #2563eb;
}

.text-red-600 {
  color: #dc2626;
}

.text-red-800 {
  color: #991b1b;
}

.text-white {
  color: #ffffff;
}

/* 背景色 */
.bg-white {
  background-color: #ffffff;
}

.bg-blue-600 {
  background-color: #2563eb;
}

.bg-gray-600 {
  background-color: #4b5563;
}

.bg-gray-300 {
  background-color: #d1d5db;
}

.bg-gray-400 {
  background-color: #9ca3af;
}

.bg-fee2e2 {
  background-color: #fee2e2;
}

/* 圆角 */
.rounded-lg {
  border-radius: 0.5rem;
}

.rounded-md {
  border-radius: 0.375rem;
}

/* 阴影 */
.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.hover\:shadow-lg:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* 内边距 */
.p-6 {
  padding: 1.5rem;
}

.p-4 {
  padding: 1rem;
}

.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}

.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.py-1 {
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.py-12 {
  padding-top: 3rem;
  padding-bottom: 3rem;
}

/* 表单 */
.block {
  display: block;
}

.w-full {
  width: 100%;
}

.border {
  border-width: 1px;
}

.border-t {
  border-top-width: 1px;
}

.border-gray-300 {
  border-color: #d1d5db;
}

input[type="date"],
input[type="time"],
input[type="text"],
textarea {
  font-family: inherit;
  font-size: 0.875rem;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 按钮 */
button {
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.hover\:bg-blue-700:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.hover\:bg-gray-700:hover {
  background-color: #374151;
}

.hover\:bg-gray-400:hover {
  background-color: #9ca3af;
}

.hover\:text-blue-800:hover {
  color: #1e40af;
}

.hover\:text-red-800:hover {
  color: #991b1b;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.disabled\:bg-gray-400:disabled {
  background-color: #9ca3af;
}

.disabled\:cursor-not-allowed:disabled {
  cursor: not-allowed;
}

/* 布局 */
.flex {
  display: flex;
}

.flex-1 {
  flex: 1 1 0%;
}

.items-start {
  align-items: flex-start;
}

.items-center {
  align-items: center;
}

.items-end {
  align-items: flex-end;
}

.justify-end {
  justify-content: flex-end;
}

.justify-between {
  justify-content: space-between;
}

.gap-2 {
  gap: 0.5rem;
}

.gap-3 {
  gap: 0.75rem;
}

.gap-4 {
  gap: 1rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

/* Grid */
.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

/* 文本 */
.text-center {
  text-align: center;
}

/* 过渡 */
.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* 响应式 */
@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .md\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .text-3xl {
    font-size: 1.5rem;
    line-height: 2rem;
  }
  
  .px-4 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }
  
  .p-6 {
    padding: 1rem;
  }
}
</style>
