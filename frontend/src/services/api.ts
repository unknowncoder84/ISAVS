/**
 * API Service Layer for ISAVS Frontend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

// Use environment variable for production, fallback to proxy for development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Create axios instance with auth token interceptor
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('supabase.auth.token')
  if (token) {
    const session = JSON.parse(token)
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }
  }
  return config
})

export { api }

// Types
export interface EnrollRequest {
  name: string;
  student_id_card_number: string;
  face_image: string;
}

export interface EnrollResponse {
  success: boolean;
  student_id?: number;
  message: string;
}

export interface StartSessionResponse {
  success: boolean;
  session_id: string;
  otp_count: number;
  expires_at: string;
  message: string;
}

export interface VerifyRequest {
  student_id: string;
  otp: string;
  face_image: string;
  session_id: string;
  latitude?: number;
  longitude?: number;
}

export interface FactorResults {
  face_verified: boolean;
  face_confidence: number;
  liveness_passed: boolean;
  id_verified: boolean;
  otp_verified: boolean;
  geofence_verified?: boolean;
  distance_meters?: number;
}

export interface VerifyResponse {
  success: boolean;
  factors: FactorResults;
  message: string;
  attendance_id?: number;
  confidence?: number;
}

export interface ResendOTPResponse {
  success: boolean;
  attempts_remaining: number;
  expires_at?: string;
  message: string;
}

export interface AttendanceRecord {
  id: number;
  student_id: number;
  student_name: string;
  student_id_card_number: string;
  timestamp: string;
  verification_status: 'verified' | 'failed';
  face_confidence?: number;
  otp_verified: boolean;
}

export interface Anomaly {
  id: number;
  student_id?: number;
  student_name?: string;
  session_id?: number;
  reason: string;
  anomaly_type: string;
  face_confidence?: number;
  timestamp: string;
  reviewed: boolean;
}

export interface AttendanceStatistics {
  total_students: number;
  verified_count: number;
  failed_count: number;
  attendance_percentage: number;
}

export interface ReportResponse {
  attendance_records: AttendanceRecord[];
  proxy_alerts: any[];
  identity_mismatch_alerts: any[];
  statistics: AttendanceStatistics;
}

// API Functions

export async function enrollStudent(data: EnrollRequest): Promise<EnrollResponse> {
  const response = await api.post<EnrollResponse>('/enroll', data);
  return response.data;
}

export async function startSession(classId: string): Promise<StartSessionResponse> {
  const response = await api.post<StartSessionResponse>(`/session/start/${classId}`);
  return response.data;
}

export async function getStudentOTP(sessionId: string, studentId: string): Promise<{ otp: string; remaining_seconds: number; student_id: string; student_name: string }> {
  const response = await api.get(`/session/${sessionId}/otp/${studentId}`);
  return response.data;
}

export async function verifyAttendance(data: VerifyRequest): Promise<VerifyResponse> {
  const response = await api.post<VerifyResponse>('/verify', data);
  return response.data;
}

export async function resendOTP(sessionId: string, studentId: string): Promise<ResendOTPResponse> {
  const response = await api.post<ResendOTPResponse>('/otp/resend', {
    session_id: sessionId,
    student_id: studentId,
  });
  return response.data;
}

export async function getReports(sessionId?: number, date?: string): Promise<ReportResponse> {
  const params = new URLSearchParams();
  if (sessionId) params.append('session_id', sessionId.toString());
  if (date) params.append('date', date);
  
  const response = await api.get<ReportResponse>(`/reports?${params.toString()}`);
  return response.data;
}

export async function getAttendanceRecords(filters?: {
  session_id?: number;
  student_id?: number;
  start_date?: string;
  end_date?: string;
  limit?: number;
}): Promise<{ records: AttendanceRecord[]; count: number }> {
  const params = new URLSearchParams();
  if (filters?.session_id) params.append('session_id', filters.session_id.toString());
  if (filters?.student_id) params.append('student_id', filters.student_id.toString());
  if (filters?.start_date) params.append('start_date', filters.start_date);
  if (filters?.end_date) params.append('end_date', filters.end_date);
  if (filters?.limit) params.append('limit', filters.limit.toString());
  
  const response = await api.get(`/reports/attendance?${params.toString()}`);
  return response.data;
}

export async function getAnomalies(filters?: {
  session_id?: number;
  anomaly_type?: string;
  unreviewed_only?: boolean;
}): Promise<{ anomalies: Anomaly[]; count: number }> {
  const params = new URLSearchParams();
  if (filters?.session_id) params.append('session_id', filters.session_id.toString());
  if (filters?.anomaly_type) params.append('anomaly_type', filters.anomaly_type);
  if (filters?.unreviewed_only) params.append('unreviewed_only', 'true');
  
  const response = await api.get(`/reports/anomalies?${params.toString()}`);
  return response.data;
}

export async function getStudents(includeImages: boolean = false): Promise<{ students: any[]; count: number }> {
  const response = await api.get('/students', {
    params: { include_images: includeImages }
  });
  return response.data;
}

export async function unlockSession(sessionKey: string, facultyId: number): Promise<{ message: string }> {
  const response = await api.post(`/sessions/${sessionKey}/unlock?faculty_id=${facultyId}`);
  return response.data;
}

export async function unlockStudentAccount(studentId: string): Promise<{ success: boolean; message: string }> {
  const response = await api.post(`/students/${studentId}/unlock`);
  return response.data;
}

export async function deleteStudent(studentId: number): Promise<{ message: string }> {
  const response = await api.delete(`/students/${studentId}`);
  return response.data;
}

// Error handler
export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail: string }>;
    return axiosError.response?.data?.detail || axiosError.message;
  }
  return 'An unexpected error occurred';
}

export default api;
