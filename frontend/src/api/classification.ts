/**
 * 文本分类API客户端
 */
import apiClient from './client'

export interface ClassifyRequest {
  text: string
}

export interface ClassifyResponse {
  type: 'schedule' | 'memo'
  confidence: number
  extracted_data: {
    date?: string
    time?: string
    description?: string
    summary?: string
    tags?: string[]
  }
  needs_manual_selection: boolean
}

export interface ManualClassifyRequest {
  text: string
  type: 'schedule' | 'memo'
}

/**
 * 自动分类文本
 */
export async function classifyText(text: string): Promise<ClassifyResponse> {
  const response = await apiClient.post<ClassifyResponse>('/classify', {
    text
  })
  return response.data
}

/**
 * 手动选择分类
 */
export async function manualClassify(text: string, type: 'schedule' | 'memo'): Promise<any> {
  const response = await apiClient.post('/classify/manual', {
    text,
    type
  })
  return response.data
}
