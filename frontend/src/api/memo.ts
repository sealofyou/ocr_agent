import apiClient from './client'

export interface Memo {
  id: string
  user_id: string
  content: string
  summary: string
  tags: string | null
  created_at: string
  updated_at: string
}

export interface MemoCreateRequest {
  content: string
  summary?: string
  tags?: string[]
}

export interface MemoUpdateRequest {
  content?: string
  summary?: string
  tags?: string[]
}

export interface MemoListResponse {
  memos: Memo[]
  total: number
}

export const memoApi = {
  // 创建备忘录
  async create(data: MemoCreateRequest): Promise<Memo> {
    const response = await apiClient.post('/memos', data)
    return response.data
  },

  // 获取备忘录列表
  async list(tags?: string): Promise<MemoListResponse> {
    const params = tags ? { tags } : {}
    const response = await apiClient.get('/memos', { params })
    return response.data
  },

  // 获取单个备忘录
  async get(id: string): Promise<Memo> {
    const response = await apiClient.get(`/memos/${id}`)
    return response.data
  },

  // 更新备忘录
  async update(id: string, data: MemoUpdateRequest): Promise<Memo> {
    const response = await apiClient.put(`/memos/${id}`, data)
    return response.data
  },

  // 删除备忘录
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/memos/${id}`)
  },

  // 解析标签字符串为数组
  parseTags(tags: string | null): string[] {
    if (!tags) return []
    return tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0)
  },

  // 格式化标签数组为字符串
  formatTags(tags: string[]): string {
    return tags.join(', ')
  }
}
