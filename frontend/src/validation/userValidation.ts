export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Validates email format
 */
export const validateEmail = (email: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!email) {
    errors.push('Email is required');
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      errors.push('Invalid email format');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validates password requirements:
 * - Minimum 6 characters
 * - At least one uppercase letter
 */
export const validatePassword = (password: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!password) {
    errors.push('Password is required');
  } else {
    if (password.length < 6) {
      errors.push('Password must be at least 6 characters long');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validates that passwords match
 */
export const validatePasswordMatch = (
  password: string,
  confirmPassword: string
): ValidationResult => {
  const errors: string[] = [];
  
  if (password !== confirmPassword) {
    errors.push('Passwords do not match');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validates name field (first name or last name)
 */
export const validateName = (name: string, fieldName: string): ValidationResult => {
  const errors: string[] = [];
  
  if (!name || name.trim().length === 0) {
    errors.push(`${fieldName} is required`);
  } else if (name.trim().length < 2) {
    errors.push(`${fieldName} must be at least 2 characters long`);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validates login form data
 */
export const validateLoginForm = (email: string, password: string): ValidationResult => {
  const errors: string[] = [];
  
  const emailValidation = validateEmail(email);
  const passwordValidation = validatePassword(password);
  
  errors.push(...emailValidation.errors, ...passwordValidation.errors);
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validates registration form data
 */
export const validateRegisterForm = (
  firstName: string,
  lastName: string,
  email: string,
  password: string,
  confirmPassword: string
): ValidationResult => {
  const errors: string[] = [];
  
  const firstNameValidation = validateName(firstName, 'First name');
  const lastNameValidation = validateName(lastName, 'Last name');
  const emailValidation = validateEmail(email);
  const passwordValidation = validatePassword(password);
  const passwordMatchValidation = validatePasswordMatch(password, confirmPassword);
  
  errors.push(
    ...firstNameValidation.errors,
    ...lastNameValidation.errors,
    ...emailValidation.errors,
    ...passwordValidation.errors,
    ...passwordMatchValidation.errors
  );
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

/**
 * Validates change password form data
 */
export const validateChangePasswordForm = (
  currentPassword: string,
  newPassword: string,
  confirmPassword: string
): ValidationResult => {
  const errors: string[] = [];
  
  if (!currentPassword) {
    errors.push('Current password is required');
  }
  
  const passwordValidation = validatePassword(newPassword);
  const passwordMatchValidation = validatePasswordMatch(newPassword, confirmPassword);
  
  errors.push(...passwordValidation.errors, ...passwordMatchValidation.errors);
  
  return {
    isValid: errors.length === 0,
    errors
  };
};
