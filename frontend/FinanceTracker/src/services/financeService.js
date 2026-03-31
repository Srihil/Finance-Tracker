import api from './api';
import { API_ENDPOINTS } from '../constants';


export const getCategories = async (type = null) => {
  const params = type ? { type } : {};
  const response = await api.get(API_ENDPOINTS.CATEGORIES, { params });
  return response.data;
};

export const createCategory = async (data) => {
  const response = await api.post(API_ENDPOINTS.CATEGORIES, data);
  return response.data;
};


export const getTransactions = async (filters = {}) => {
  const response = await api.get(API_ENDPOINTS.TRANSACTIONS, {
    params: filters,
  });
  return response.data;
};

export const createTransaction = async (data) => {
  const response = await api.post(API_ENDPOINTS.TRANSACTIONS, data);
  return response.data;
};

export const updateTransaction = async (id, data) => {
  const response = await api.put(`${API_ENDPOINTS.TRANSACTIONS}${id}/`, data);
  return response.data;
};

export const deleteTransaction = async (id) => {
  await api.delete(`${API_ENDPOINTS.TRANSACTIONS}${id}/`);
};

export const getFinancialSummary = async (filters = {}) => {
  const response = await api.get(API_ENDPOINTS.SUMMARY, { params: filters });
  return response.data;
};

export const getMonthlySummary = async (year = null) => {
  const params = year ? { year } : {};
  const response = await api.get(API_ENDPOINTS.MONTHLY_SUMMARY, { params });
  return response.data;
};

export const getCategorySpending = async (filters = {}) => {
  const response = await api.get(API_ENDPOINTS.CATEGORY_SPENDING, {
    params: filters,
  });
  return response.data;
};