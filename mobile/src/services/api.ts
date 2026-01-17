/**
 * API Client Service
 * Handles all HTTP requests to the ISAVS backend
 */
import axios, {AxiosInstance, AxiosError, AxiosRequestConfig} from 'axios';
import {
  SensorVerificationRequest,
  SensorVerificationResponse,
  OTPResponse,
  SessionResponse,
  APIError,
} from '../types';

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      timeout: 30000, // 30 seconds for sensor data upload
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(
          `[API] ${config.method?.toUpperCase()} ${config.url}`,
        );
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(error);
      },
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(
          `[API] Response ${response.status} ${response.config.url}`,
        );
        return response;
      },
      (error: AxiosError) => {
        console.error('[API] Response error:', error.message);
        
        // Transform error to APIError
        const apiError: APIError = {
          message: error.message,
          status: error.response?.status,
          details: error.response?.data,
        };
        
        return Promise.reject(apiError);
      },
    );
  }

  /**
   * Verify attendance with sensor data
   */
  async verifyAttendance(
    request: SensorVerificationRequest,
  ): Promise<SensorVerificationResponse> {
    try {
      const response = await this.client.post<SensorVerificationResponse>(
        '/api/v1/verify',
        request,
      );
      return response.data;
    } catch (error) {
      console.error('[API] Verify attendance error:', error);
      throw error;
    }
  }

  /**
   * Get OTP for a student
   */
  async getOTP(sessionId: string, studentId: string): Promise<OTPResponse> {
    try {
      const response = await this.client.get<OTPResponse>(
        `/api/v1/session/${sessionId}/otp/${studentId}`,
      );
      return response.data;
    } catch (error) {
      console.error('[API] Get OTP error:', error);
      throw error;
    }
  }

  /**
   * Resend OTP
   */
  async resendOTP(sessionId: string, studentId: string): Promise<void> {
    try {
      await this.client.post('/api/v1/otp/resend', {
        session_id: sessionId,
        student_id: studentId,
      });
    } catch (error) {
      console.error('[API] Resend OTP error:', error);
      throw error;
    }
  }

  /**
   * Start attendance session (Teacher)
   */
  async startSession(classId: string): Promise<SessionResponse> {
    try {
      const response = await this.client.post<SessionResponse>(
        `/api/v1/session/start/${classId}`,
      );
      return response.data;
    } catch (error) {
      console.error('[API] Start session error:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('[API] Health check error:', error);
      return false;
    }
  }

  /**
   * Update base URL (for configuration changes)
   */
  updateBaseURL(newBaseURL: string): void {
    this.baseURL = newBaseURL;
    this.client.defaults.baseURL = newBaseURL;
    console.log(`[API] Base URL updated to: ${newBaseURL}`);
  }

  /**
   * Get current base URL
   */
  getBaseURL(): string {
    return this.baseURL;
  }
}

// Singleton instance
// Default to localhost for development
// Update this in production or via configuration
const apiClient = new APIClient('http://localhost:8000');

export default apiClient;
