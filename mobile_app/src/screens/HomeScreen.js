/**
 * Home Screen - Upload manuscript and check system status
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../services/api';

export default function HomeScreen({ navigation }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [checkingActiveJob, setCheckingActiveJob] = useState(true);

  useEffect(() => {
    initializeScreen();
  }, []);

  const initializeScreen = async () => {
    setLoading(true);
    setCheckingActiveJob(true);

    // Check for active job first (prevents race conditions)
    await checkForActiveJob();

    // Then check system health
    await checkSystemHealth();

    setLoading(false);
    setCheckingActiveJob(false);
  };

  const checkForActiveJob = async () => {
    try {
      const activeJobId = await AsyncStorage.getItem('active_job_id');
      const activeBookId = await AsyncStorage.getItem('active_book_id');

      if (activeJobId && activeBookId) {
        // Verify job is still running by checking status
        try {
          const jobStatus = await api.getJobStatus(activeJobId);

          // Backend uses: "queued", "processing", "completed", "failed"
          if (jobStatus.status === 'queued' || jobStatus.status === 'processing') {
            // Job is still active, offer to resume
            Alert.alert(
              'Active Job Found',
              'You have a processing job in progress. Would you like to resume?',
              [
                {
                  text: 'Cancel',
                  style: 'cancel',
                  onPress: async () => {
                    // Clear stored job if user cancels
                    await AsyncStorage.removeItem('active_job_id');
                    await AsyncStorage.removeItem('active_book_id');
                  }
                },
                {
                  text: 'Resume',
                  onPress: () => {
                    navigation.navigate('Processing', {
                      jobId: activeJobId,
                      bookId: activeBookId
                    });
                  }
                }
              ]
            );
          } else {
            // Job completed or failed, clear storage
            await AsyncStorage.removeItem('active_job_id');
            await AsyncStorage.removeItem('active_book_id');
          }
        } catch (error) {
          // Job not found or error checking status, clear storage
          await AsyncStorage.removeItem('active_job_id');
          await AsyncStorage.removeItem('active_book_id');
        }
      }
    } catch (error) {
      console.error('Error checking for active job:', error);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const healthData = await api.checkHealth();
      setHealth(healthData);
    } catch (error) {
      const errorMessage = error.response?.data?.detail ||
                          error.message ||
                          'Failed to connect to backend server. Please ensure the server is running.';

      Alert.alert('Connection Error', errorMessage);
      console.error('Health check error:', error);
    }
  };

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'text/plain',
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setSelectedFile(result.assets[0]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick document');
    }
  };

  const uploadManuscript = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a manuscript file first');
      return;
    }

    // Check for API keys
    const openaiKey = await AsyncStorage.getItem('openai_key');
    const anthropicKey = await AsyncStorage.getItem('anthropic_key');

    if (!openaiKey || !anthropicKey) {
      Alert.alert(
        'API Keys Required',
        'Please configure your OpenAI and Anthropic API keys in Settings before processing manuscripts.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Open Settings', onPress: () => navigation.navigate('Settings') }
        ]
      );
      return;
    }

    if (!health || health.status !== 'healthy') {
      Alert.alert(
        'System Not Ready',
        'Backend system is not fully configured. Please check:\n' +
        '• Redis is running\n' +
        '• ChromaDB is running'
      );
      return;
    }

    setUploading(true);

    try {
      const response = await api.uploadManuscript(selectedFile, openaiKey, anthropicKey);

      // Navigate to processing screen
      navigation.navigate('Processing', {
        jobId: response.job_id,
        bookId: response.book_id,
      });
    } catch (error) {
      // Extract error message from various error formats
      const errorMessage = error.response?.data?.detail ||
                          error.response?.data?.message ||
                          error.message ||
                          'Failed to upload manuscript. Please check your connection and try again.';

      Alert.alert('Upload Failed', errorMessage);
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const renderHealthStatus = () => {
    if (!health) {
      return (
        <View style={styles.healthContainer}>
          <ActivityIndicator size="small" color="#6366f1" />
          <Text style={styles.healthText}>Checking system status...</Text>
        </View>
      );
    }

    const isHealthy = health.status === 'healthy';

    return (
      <View style={styles.healthContainer}>
        <View style={[styles.healthIndicator, isHealthy ? styles.healthy : styles.unhealthy]} />
        <View style={styles.healthDetails}>
          <Text style={styles.healthTitle}>
            System Status: {isHealthy ? 'Ready' : 'Not Ready'}
          </Text>

          <View style={styles.healthChecks}>
            <HealthCheck
              label="Redis"
              status={health.redis_connected}
            />
            <HealthCheck
              label="ChromaDB"
              status={health.chromadb_connected}
            />
            <HealthCheck
              label="OpenAI API"
              status={health.openai_api_configured}
            />
            <HealthCheck
              label="Anthropic API"
              status={health.anthropic_api_configured}
            />
          </View>

          {!isHealthy && (
            <TouchableOpacity
              style={styles.retryButton}
              onPress={checkSystemHealth}
            >
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>📚 AI Ghostwriter</Text>
          <Text style={styles.subtitle}>
            Transform your manuscript with AI-powered multi-agent editing
          </Text>
        </View>

        {/* Settings Button */}
        <TouchableOpacity
          style={styles.settingsButton}
          onPress={() => navigation.navigate('Settings')}
        >
          <Text style={styles.settingsButtonText}>⚙️ Configure API Keys</Text>
        </TouchableOpacity>

        {/* System Health */}
        {renderHealthStatus()}

        {/* File Selection */}
        <View style={styles.uploadSection}>
          <Text style={styles.sectionTitle}>Upload Manuscript</Text>

          {selectedFile ? (
            <View style={styles.selectedFile}>
              <Text style={styles.fileName}>📄 {selectedFile.name}</Text>
              <Text style={styles.fileSize}>
                {(selectedFile.size / 1024).toFixed(1)} KB
              </Text>
            </View>
          ) : (
            <View style={styles.placeholderBox}>
              <Text style={styles.placeholderText}>No file selected</Text>
            </View>
          )}

          <TouchableOpacity
            style={styles.selectButton}
            onPress={pickDocument}
            disabled={uploading}
          >
            <Text style={styles.selectButtonText}>
              {selectedFile ? 'Change File' : 'Select .txt File'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Upload Button */}
        <TouchableOpacity
          style={[
            styles.uploadButton,
            (!selectedFile || uploading || checkingActiveJob || health?.status !== 'healthy') &&
              styles.uploadButtonDisabled,
          ]}
          onPress={uploadManuscript}
          disabled={!selectedFile || uploading || checkingActiveJob || health?.status !== 'healthy'}
        >
          {uploading || checkingActiveJob ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.uploadButtonText}>🚀 Start Processing</Text>
          )}
        </TouchableOpacity>

        {/* Info */}
        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>What happens next?</Text>
          <Text style={styles.infoText}>
            • Analysis: Strategic planning{'\n'}
            • Continuity: Build consistency database{'\n'}
            • Expansion: 22K → 47K words{'\n'}
            • Editing: Polish prose quality{'\n'}
            • QA: Quality assurance (≥8.0/10){'\n'}
            • Learning: Store patterns for future books
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

function HealthCheck({ label, status }) {
  return (
    <View style={styles.healthCheckItem}>
      <View style={[styles.checkIndicator, status ? styles.checkOk : styles.checkFail]} />
      <Text style={styles.checkLabel}>{label}</Text>
      <Text style={styles.checkStatus}>{status ? '✓' : '✗'}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
  },
  header: {
    marginBottom: 30,
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  settingsButton: {
    backgroundColor: '#6366f1',
    borderRadius: 12,
    padding: 15,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  settingsButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  healthContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  healthIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginBottom: 10,
  },
  healthy: {
    backgroundColor: '#10b981',
  },
  unhealthy: {
    backgroundColor: '#ef4444',
  },
  healthDetails: {
    marginTop: 10,
  },
  healthTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  healthText: {
    fontSize: 16,
    color: '#666',
  },
  healthChecks: {
    marginTop: 10,
  },
  healthCheckItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  checkIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 10,
  },
  checkOk: {
    backgroundColor: '#10b981',
  },
  checkFail: {
    backgroundColor: '#ef4444',
  },
  checkLabel: {
    flex: 1,
    fontSize: 14,
  },
  checkStatus: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  retryButton: {
    marginTop: 15,
    padding: 10,
    backgroundColor: '#6366f1',
    borderRadius: 8,
    alignItems: 'center',
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  uploadSection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  selectedFile: {
    backgroundColor: '#f0f9ff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
  },
  fileName: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 5,
  },
  fileSize: {
    fontSize: 14,
    color: '#666',
  },
  placeholderBox: {
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    borderStyle: 'dashed',
    padding: 30,
    marginBottom: 15,
    alignItems: 'center',
  },
  placeholderText: {
    fontSize: 14,
    color: '#9ca3af',
  },
  selectButton: {
    backgroundColor: '#6366f1',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  selectButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  uploadButton: {
    backgroundColor: '#10b981',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  uploadButtonDisabled: {
    backgroundColor: '#d1d5db',
  },
  uploadButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoBox: {
    backgroundColor: '#eff6ff',
    borderRadius: 12,
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#1e40af',
  },
  infoText: {
    fontSize: 14,
    color: '#1e3a8a',
    lineHeight: 22,
  },
});
