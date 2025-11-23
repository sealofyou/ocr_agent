/**
 * OCR识别API客户端
 */
import apiClient from './client'

export interface OCRTextDetail {
  text: string
  confidence: number
  box: number[][]
}

export interface OCRRecognizeResponse {
  success: boolean
  text: string
  details: OCRTextDetail[]
  error?: string
}

export interface OCRRecognizeRequest {
  file_id: string
}

export interface OCREditRequest {
  file_id: string
  edited_text: string
}

/**
 * 识别图片中的文字
 */
export async function recognizeImage(fileId: string): Promise<OCRRecognizeResponse> {
  const response = await apiClient.post<OCRRecognizeResponse>('/ocr/recognize', {
    file_id: fileId
  })
  return response.data
}

/**
 * 编辑OCR识别结果
 */
export async function editOCRResult(fileId: string, editedText: string): Promise<any> {
  const response = await apiClient.post('/ocr/edit', {
    file_id: fileId,
    edited_text: editedText
  })
  return response.data
}
