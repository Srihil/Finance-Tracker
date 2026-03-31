import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_ENDPOINTS, STORAGE_KEYS } from '../constants';

export const registerUser = async (userData) => {
  const response = await api.post(API_ENDPOINTS.REGISTER, userData);
  return response.data;
};

export const loginUser = async (email, password) => {
  const response = await api.post(API_ENDPOINTS.LOGIN, { email, password });
  const { tokens, user } = response.data;

  await AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN,  tokens.access);
  await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh);
  await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA,     JSON.stringify(user));

  return response.data;
};

export const logoutUser = async () => {
  try {
    const refreshToken = await AsyncStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    await api.post(API_ENDPOINTS.LOGOUT, { refresh: refreshToken });
  } catch (error) {
    console.log('Logout API error (safe to ignore):', error);
  } finally {
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.ACCESS_TOKEN,
      STORAGE_KEYS.REFRESH_TOKEN,
      STORAGE_KEYS.USER_DATA,
    ]);
  }
};

export const getProfile = async () => {
  const response = await api.get(API_ENDPOINTS.PROFILE);
  return response.data;
};

export const updateProfile = async (data) => {
  const response = await api.put(API_ENDPOINTS.PROFILE_UPDATE, data);
  return response.data;
};

export const isLoggedIn = async () => {
  const token = await AsyncStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  return !!token;
};

export const getStoredUser = async () => {
  const userData = await AsyncStorage.getItem(STORAGE_KEYS.USER_DATA);
  return userData ? JSON.parse(userData) : null;
};