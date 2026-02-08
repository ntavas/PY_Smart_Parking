/**
 * authService.ts - Authentication API Service
 *
 * Handles API calls for user authentication:
 * - Login, Register, Change Password
 */

import type { User, LoginFormData, RegisterFormData } from '../types/user';

const API_BASE_URL = 'http://localhost:8000'; // Update with your backend URL
const USER_STORAGE_KEY = 'smart_parking_user';

export const authService = {
  getAuthHeaders(): HeadersInit {
    const stored = localStorage.getItem(USER_STORAGE_KEY);
    let token = '';
    if (stored) {
      try {
        const user = JSON.parse(stored);
        token = user.token || '';
      } catch (e) { console.error('Error parsing user for token', e); }
    }
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
  },

  /**
   * Login user with email and password
   */
  async login(data: LoginFormData): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/users/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const resData = await response.json();
    // Backend returns { access_token, token_type, user }
    // We merge token into user object
    const userWithToken: User = { ...resData.user, token: resData.access_token };
    return userWithToken;
  },

  /**
   * Register a new user
   */
  async register(data: RegisterFormData): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/users/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: data.email,
        password: data.password,
        full_name: `${data.firstName} ${data.lastName}`,
      }),
    });

    if (!response.ok) {
      // ... error handling
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    // Registration returns just the user (no token yet usually, unless I changed it)
    // My backend `create_user` returns `UserResponse` (no token).
    // So user still needs to login, or I could auto-login.
    // For now, return user.
    return response.json();
  },

  /**
   * Change user password
   */
  async changePassword(
    userId: number,
    _currentPassword: string,
    newPassword: string
  ): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        password: newPassword,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Password change failed');
    }

    return response.json();
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem(USER_STORAGE_KEY);
  },
};
