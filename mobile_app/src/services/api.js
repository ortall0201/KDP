/**
 * API Service for communicating with FastAPI backend
 */

import axios from 'axios';

// Configure your backend server URL
// For local development: http://localhost:8080
// For production: your deployed server URL
const API_BASE_URL = 'http://localhost:8080';

/**
 * Backend Status Values:
 * - Job Status: "queued", "processing", "completed", "failed"
 * - Phase Status: "pending", "running", "completed", "error"
 */

class GhostwriterAPI {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Check if backend is healthy
   */
  async checkHealth() {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  /**
   * Upload manuscript file
   * @param {Object} file - File object with uri, name, type
   * @param {string} openaiKey - OpenAI API key
   * @param {string} anthropicKey - Anthropic API key
   * @returns {Promise} - Job ID and book ID
   */
  async uploadManuscript(file, openaiKey, anthropicKey) {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: file.uri,
        name: file.name,
        type: 'text/plain',
      });

      const response = await this.api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-OpenAI-Key': openaiKey,
          'X-Anthropic-Key': anthropicKey,
        },
      });

      return response.data; // { job_id, book_id, message }
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    }
  }

  /**
   * Get job status
   * @param {string} jobId
   */
  async getJobStatus(jobId) {
    try {
      const response = await this.api.get(`/status/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get job status:', error);
      throw error;
    }
  }

  /**
   * Get download URL for completed manuscript
   * @param {string} jobId
   */
  getDownloadUrl(jobId) {
    return `${API_BASE_URL}/download/${jobId}`;
  }

  /**
   * Create WebSocket connection for real-time updates
   * @param {string} jobId
   * @param {Function} onMessage - Callback for messages
   * @param {Function} onError - Callback for errors
   * @param {Function} onClose - Callback for connection close
   */
  connectWebSocket(jobId, onMessage, onError, onClose) {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + `/ws/${jobId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
      if (onClose) onClose();
    };

    return ws;
  }

  /**
   * Poll for job status (alternative to WebSocket)
   * @param {string} jobId
   * @param {Function} callback
   * @param {number} interval - Poll interval in ms
   * @returns {Function} Cleanup function to stop polling
   */
  pollJobStatus(jobId, callback, interval = 2000) {
    let timeoutId = null;
    let isCancelled = false;

    const poll = async () => {
      if (isCancelled) return;

      try {
        const status = await this.getJobStatus(jobId);

        if (isCancelled) return;

        callback(status);

        // Continue polling if not completed or failed (backend uses: "queued", "processing")
        if ((status.status === 'queued' || status.status === 'processing') && !isCancelled) {
          timeoutId = setTimeout(poll, interval);
        }
      } catch (error) {
        console.error('Polling failed:', error);
        if (!isCancelled) {
          callback({ error: error.message });
        }
      }
    };

    poll();

    // Return cleanup function
    return () => {
      isCancelled = true;
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
    };
  }
}

export default new GhostwriterAPI();
