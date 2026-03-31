export const API_BASE_URL = 'http://10.0.2.2:8000/api';

export const API_ENDPOINTS = {
  REGISTER      : '/auth/register/',
  LOGIN         : '/auth/login/',
  LOGOUT        : '/auth/logout/',
  PROFILE       : '/auth/profile/',
  PROFILE_UPDATE: '/auth/profile/update/',
  TOKEN_REFRESH : '/auth/token/refresh/',

  CATEGORIES         : '/finance/categories/',
  TRANSACTIONS       : '/finance/transactions/',
  SUMMARY            : '/finance/transactions/summary/',
  MONTHLY_SUMMARY    : '/finance/transactions/monthly-summary/',
  CATEGORY_SPENDING  : '/finance/transactions/category-spending/',
};

export const COLORS = {
  primary    : '#6C63FF',    
  secondary  : '#3DDC84',    
  danger     : '#FF6B6B',    
  warning    : '#FFB347',    
  dark       : '#1A1A2E',    
  card       : '#16213E',    
  input      : '#0F3460',    
  white      : '#FFFFFF',
  lightGray  : '#F5F5F5',
  gray       : '#9E9E9E',
  border     : '#E0E0E0',
  text       : '#212121',
  textLight  : '#757575',
  income     : '#4CAF50',    
  expense    : '#F44336',    
  balance    : '#6C63FF',   
};

export const FONTS = {
  small  : 12,
  body   : 14,
  medium : 16,
  large  : 18,
  xl     : 22,
  xxl    : 28,
};

export const SPACING = {
  xs : 4,
  sm : 8,
  md : 16,
  lg : 24,
  xl : 32,
};

export const TRANSACTION_TYPES = {
  INCOME : 'income',
  EXPENSE: 'expense',
};

export const STORAGE_KEYS = {
  ACCESS_TOKEN : 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA    : 'user_data',
};