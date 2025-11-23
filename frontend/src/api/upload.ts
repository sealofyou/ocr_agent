/**
 * 文件上传API客户端
 */
import apiClient from './client'

export interface FileUploadResponse {
  file_id: string
  filename: string
  file_path: string
  file_size: number
  content_type: string
  uploaded_at: string
}

export interface TextInputRequest {
  text: string
  source?: string
}

export interface TextInputResponse {
  text_id: string
  text: string
  source: string
  created_at: string
}

/**
 * 上传文件
 */
export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await apiClient.post<FileUploadResponse>('/upload/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

/**
 * 输入文本
 */
export async function inputText(text: string, source: string = 'manual'): Promise<TextInputResponse> {
  const response = await apiClient.post<TextInputResponse>('/upload/text', {
    text,
    source
  })
  return response.data
}

/**
 * 获取上传文件列表
 */
export async function getUploadedFiles(skip: number = 0, limit: number = 20): Promise<FileUploadResponse[]> {
  const response = await apiClient.get<FileUploadResponse[]>('/upload/files', {
    params: { skip, limit }
  })
  return response.data
}

/**
 * 删除上传文件
 */
export async function deleteUploadedFile(fileId: string): Promise<void> {
  await apiClient.delete(`/upload/file/${fileId}`)
}
