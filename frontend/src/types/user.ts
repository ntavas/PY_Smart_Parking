/**
 * user.ts - User-related Type Definitions
 *
 * Defines TypeScript interfaces for user data and form inputs.
 */

export interface User {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface ChangePasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
