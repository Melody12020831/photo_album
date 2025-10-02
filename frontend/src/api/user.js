import axios from 'axios'

const API_BASE = '/api/'

export function register(data) {
  return axios.post(API_BASE + 'register/', data)
}

export function login(data) {
  return axios.post(API_BASE + 'login/', data)
}
