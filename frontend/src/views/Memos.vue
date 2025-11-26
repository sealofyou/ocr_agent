<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">我的备忘录</h1>
        <p class="mt-2 text-gray-600">管理您的笔记和想法</p>
      </div>

      <!-- 创建备忘录表单 -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">创建新备忘录</h2>
        <form @submit.prevent="createMemo">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              内容
            </label>
            <textarea
              v-model="newMemo.content"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="输入备忘录内容..."
              required
            ></textarea>
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              标签（用逗号分隔）
            </label>
            <input
              v-model="newMemo.tagsInput"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="例如：工作, 学习, 想法"
            />
          </div>

          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="loading"
              class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {{ loading ? '创建中...' : '创建备忘录' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 标签筛选 -->
      <div class="bg-white rounded-lg shadow-md p-4 mb-6">
        <div class="flex items-center gap-4">
          <label class="text-sm font-medium text-gray-700">筛选标签：</label>
          <input
            v-model="filterTags"
            type="text"
            class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="输入标签筛选（用逗号分隔）"
          />
          <button
            @click="loadMemos"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            筛选
          </button>
          <button
            @click="clearFilter"
            class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            清除
          </button>
        </div>
      </div>

      <!-- 备忘录列表 -->
      <div v-if="loading && memos.length === 0" class="text-center py-12">
        <p class="text-gray-500">加载中...</p>
      </div>

      <div v-else-if="memos.length === 0" class="text-center py-12">
        <p class="text-gray-500">暂无备忘录</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="memo in memos"
          :key="memo.id"
          class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <!-- 编辑模式 -->
          <div v-if="editingId === memo.id">
            <textarea
              v-model="editForm.content"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
            ></textarea>
            <input
              v-model="editForm.tagsInput"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
              placeholder="标签（用逗号分隔）"
            />
            <div class="flex justify-end gap-2">
              <button
                @click="cancelEdit"
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                取消
              </button>
              <button
                @click="saveMemo(memo.id)"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                保存
              </button>
            </div>
          </div>

          <!-- 查看模式 -->
          <div v-else>
            <div class="mb-3">
              <p class="text-gray-800 whitespace-pre-wrap">{{ memo.content }}</p>
            </div>

            <div v-if="memo.tags" class="mb-3 flex flex-wrap gap-2">
              <span
                v-for="tag in parseTags(memo.tags)"
                :key="tag"
                class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {{ tag }}
              </span>
            </div>

            <div class="flex items-center justify-between text-sm text-gray-500">
              <span>{{ formatDate(memo.created_at) }}</span>
              <div class="flex gap-2">
                <button
                  @click="startEdit(memo)"
                  class="px-3 py-1 text-blue-600 hover:text-blue-800"
                >
                  编辑
                </button>
                <button
                  @click="deleteMemo(memo.id)"
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
import { memoApi, type Memo } from '../api/memo'

const memos = ref<Memo[]>([])
const loading = ref(false)
const filterTags = ref('')

const newMemo = ref({
  content: '',
  tagsInput: ''
})

const editingId = ref<string | null>(null)
const editForm = ref({
  content: '',
  tagsInput: ''
})

// 加载备忘录列表
const loadMemos = async () => {
  try {
    loading.value = true
    const response = await memoApi.list(filterTags.value || undefined)
    memos.value = response.memos
  } catch (error) {
    console.error('加载备忘录失败:', error)
    alert('加载备忘录失败')
  } finally {
    loading.value = false
  }
}

// 创建备忘录
const createMemo = async () => {
  try {
    loading.value = true
    const tags = newMemo.value.tagsInput
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)
    
    await memoApi.create({
      content: newMemo.value.content,
      tags: tags.length > 0 ? tags : undefined
    })

    newMemo.value.content = ''
    newMemo.value.tagsInput = ''
    await loadMemos()
  } catch (error) {
    console.error('创建备忘录失败:', error)
    alert('创建备忘录失败')
  } finally {
    loading.value = false
  }
}

// 开始编辑
const startEdit = (memo: Memo) => {
  editingId.value = memo.id
  editForm.value.content = memo.content
  editForm.value.tagsInput = memo.tags ? memoApi.formatTags(memoApi.parseTags(memo.tags)) : ''
}

// 取消编辑
const cancelEdit = () => {
  editingId.value = null
  editForm.value.content = ''
  editForm.value.tagsInput = ''
}

// 保存备忘录
const saveMemo = async (id: string) => {
  try {
    const tags = editForm.value.tagsInput
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0)
    
    await memoApi.update(id, {
      content: editForm.value.content,
      tags: tags.length > 0 ? tags : undefined
    })

    editingId.value = null
    await loadMemos()
  } catch (error) {
    console.error('更新备忘录失败:', error)
    alert('更新备忘录失败')
  }
}

// 删除备忘录
const deleteMemo = async (id: string) => {
  if (!confirm('确定要删除这条备忘录吗？')) return

  try {
    await memoApi.delete(id)
    await loadMemos()
  } catch (error) {
    console.error('删除备忘录失败:', error)
    alert('删除备忘录失败')
  }
}

// 清除筛选
const clearFilter = () => {
  filterTags.value = ''
  loadMemos()
}

// 解析标签
const parseTags = (tags: string | null): string[] => {
  return memoApi.parseTags(tags)
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadMemos()
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

/* 标题 */
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

.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}

.text-xl {
  font-size: 1.25rem;
  line-height: 1.75rem;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.font-bold {
  font-weight: 700;
}

.font-semibold {
  font-weight: 600;
}

.font-medium {
  font-weight: 500;
}

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

.text-blue-800 {
  color: #1e40af;
}

.text-red-600 {
  color: #dc2626;
}

.text-red-800 {
  color: #991b1b;
}

/* 卡片 */
.bg-white {
  background-color: #ffffff;
}

.rounded-lg {
  border-radius: 0.5rem;
}

.rounded-md {
  border-radius: 0.375rem;
}

.rounded-full {
  border-radius: 9999px;
}

.shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.hover\:shadow-lg:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

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

.border-gray-300 {
  border-color: #d1d5db;
}

textarea,
input[type="text"] {
  font-family: inherit;
  font-size: 0.875rem;
}

textarea:focus,
input[type="text"]:focus {
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

.bg-blue-100 {
  background-color: #dbeafe;
}

.text-white {
  color: #ffffff;
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

.flex-wrap {
  flex-wrap: wrap;
}

.flex-1 {
  flex: 1 1 0%;
}

.items-center {
  align-items: center;
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

.gap-4 {
  gap: 1rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

/* 文本 */
.text-center {
  text-align: center;
}

.whitespace-pre-wrap {
  white-space: pre-wrap;
}

/* 过渡 */
.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* 响应式 */
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
