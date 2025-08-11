const API_BASE = 'http://localhost:8324/api'

export const API_URLS = {
  thumbnail: (id) => `${API_BASE}/thumbnail/${id}`,
  image: (id) => `${API_BASE}/image/${id}`,
  imagePath: (path) => `${API_BASE}/image/path?file_path=${encodeURIComponent(path)}`,
  imageDetails: (id) => `${API_BASE}/image/details/${id}`
}