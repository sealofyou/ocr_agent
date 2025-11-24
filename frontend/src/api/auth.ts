/**
 * 认证API客户端
 */
import apiClient from './client'

export interface UserRegisterRequest {
  username: string
  email: string
  password: string
}

export interface UserLoginRequest {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user_id: string
  username: string
}

/**
 * 用户注册
 */
export async function register(data: UserRegisterRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/register', data)
  return response.data
}

/**
 * 用户登录
 */
export async function login(data: UserLoginRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/login', data)
  return response.data
}

/**
 * 用户登出
 */
export async function logout(): Promise<void> {
  // 清除本地存储
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
}
