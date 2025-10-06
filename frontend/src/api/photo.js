import axios from 'axios'

const API_BASE = '/api/'

export function deletePhoto(photoId, token) {
  return axios.delete(`${API_BASE}photos/${photoId}/`, {
    headers: { Authorization: `Token ${token}` }
  })
}
