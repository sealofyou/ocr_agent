import apiClient from './client'

export interface Schedule {
  id: string
  user_id: string
  date: string | null
  time: string | null
  description: string
  original_text: string
  created_at: string
  updated_at: string
}

export interface ScheduleCreateRequest {
  date?: string
  time?: string
  description: string
  original_text: string
}

export interface ScheduleUpdateRequest {
  date?: string
  time?: string
  description?: string
  original_text?: string
}

export interface ScheduleListResponse {
  schedules: Schedule[]
  total: number
}

export const scheduleApi = {
  // 创建日程
  async create(data: ScheduleCreateRequest): Promise<Schedule> {
    const response = await apiClient.post('/schedules', data)
    return response.data
  },

  // 获取日程列表
  async list(startDate?: string, endDate?: string): Promise<ScheduleListResponse> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    const response = await apiClient.get('/schedules', { params })
    return response.data
  },

  // 获取单个日程
  async get(id: string): Promise<Schedule> {
    const response = await apiClient.get(`/schedules/${id}`)
    return response.data
  },

  // 更新日程
  async update(id: string, data: ScheduleUpdateRequest): Promise<Schedule> {
    const response = await apiClient.put(`/schedules/${id}`, data)
    return response.data
  },

  // 删除日程
  async delete(id: string): Promise<void> {
    await apiClient.delete(`/schedules/${id}`)
  },

  // 格式化日期时间显示
  formatDateTime(date: string | null, time: string | null): string {
    if (!date && !time) return '未设置时间'
    if (date && time) return `${date} ${time}`
    if (date) return date
    if (time) return time
    return ''
  }
}
