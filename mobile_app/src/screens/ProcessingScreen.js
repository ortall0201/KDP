/**
 * Processing Screen - Real-time progress tracking with WebSocket
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../services/api';

export default function ProcessingScreen({ route, navigation }) {
  const { jobId, bookId } = route.params;
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const wsRef = useRef(null);
  const pollCleanupRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);

  useEffect(() => {
    // Store job ID for resumption after app restart
    const storeActiveJob = async () => {
      try {
        await AsyncStorage.setItem('active_job_id', jobId);
        await AsyncStorage.setItem('active_book_id', bookId);
      } catch (error) {
        console.error('Error storing active job:', error);
      }
    };
    storeActiveJob();

    // Connect to WebSocket for real-time updates
    connectWebSocket();

    // Cleanup on unmount
    return () => {
      // Clean up WebSocket
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      // Clean up polling if active
      if (pollCleanupRef.current) {
        pollCleanupRef.current();
        pollCleanupRef.current = null;
      }

      // Clear reconnect timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [jobId, bookId]);

  const connectWebSocket = () => {
    wsRef.current = api.connectWebSocket(
      jobId,
      handleStatusUpdate,
      handleWebSocketError,
      handleWebSocketClose
    );
  };

  // Handle back button/gesture - prevent accidental navigation away
  useEffect(() => {
    const unsubscribe = navigation.addListener('beforeRemove', (e) => {
      // Only intercept if job is still processing
      if (!status || status.status === 'completed' || status.status === 'failed') {
        // Job is done, allow navigation
        return;
      }

      // Prevent default behavior of leaving the screen
      e.preventDefault();

      // Show confirmation dialog
      Alert.alert(
        'Leave Processing?',
        'Your manuscript is still being processed. The job will continue in the background, but you may lose real-time updates.\n\nAre you sure you want to leave?',
        [
          {
            text: 'Stay',
            style: 'cancel',
            onPress: () => {}
          },
          {
            text: 'Leave',
            style: 'destructive',
            onPress: () => {
              // Allow navigation
              navigation.dispatch(e.data.action);
            }
          }
        ]
      );
    });

    return unsubscribe;
  }, [navigation, status]);

  const handleStatusUpdate = async (data) => {
    setStatus(data);

    // Navigate to completed screen when done
    if (data.status === 'completed') {
      // Clear stored job ID since job is complete
      try {
        await AsyncStorage.removeItem('active_job_id');
        await AsyncStorage.removeItem('active_book_id');
      } catch (error) {
        console.error('Error clearing active job:', error);
      }

      navigation.replace('Completed', {
        jobId: jobId,
        bookId: bookId,
        wordCount: data.word_count,
      });
    }
  };

  const handleWebSocketError = (error) => {
    console.error('WebSocket error:', error);
    attemptReconnection();
  };

  const handleWebSocketClose = () => {
    console.log('WebSocket closed');
    attemptReconnection();
  };

  const attemptReconnection = () => {
    const maxAttempts = 5;
    const backoffDelays = [1000, 2000, 5000, 10000, 30000]; // Exponential backoff

    if (reconnectAttemptsRef.current < maxAttempts) {
      const delay = backoffDelays[reconnectAttemptsRef.current] || 30000;
      console.log(`Attempting reconnection ${reconnectAttemptsRef.current + 1}/${maxAttempts} in ${delay}ms`);

      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectAttemptsRef.current += 1;
        connectWebSocket();
      }, delay);
    } else {
      // Max reconnection attempts reached, fallback to polling
      console.log('Max WebSocket reconnection attempts reached. Falling back to polling.');
      if (pollCleanupRef.current) {
        pollCleanupRef.current(); // Clean up any existing polling
      }
      pollCleanupRef.current = api.pollJobStatus(jobId, handleStatusUpdate, 3000);
    }
  };

  if (!status) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6366f1" />
        <Text style={styles.loadingText}>Connecting...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Overall Progress */}
        <View style={styles.progressSection}>
          <Text style={styles.sectionTitle}>Overall Progress</Text>
          <View style={styles.progressBarContainer}>
            <View
              style={[
                styles.progressBarFill,
                { width: `${status.progress}%` },
              ]}
            />
          </View>
          <Text style={styles.progressText}>{status.progress}%</Text>
        </View>

        {/* Phases */}
        <View style={styles.phasesSection}>
          <Text style={styles.sectionTitle}>Phases</Text>
          <View style={styles.phasesGrid}>
            {Object.entries(status.phase_status || {}).map(([phase, phaseStatus]) => (
              <PhaseCard
                key={phase}
                phase={phase}
                status={phaseStatus}
                isActive={status.current_phase === phase}
              />
            ))}
          </View>
        </View>

        {/* Chapter Progress */}
        {Object.keys(status.chapter_progress || {}).length > 0 && (
          <View style={styles.chaptersSection}>
            <Text style={styles.sectionTitle}>Chapter Progress</Text>
            <View style={styles.chapterStats}>
              <StatBox
                label="Completed"
                value={
                  Object.values(status.chapter_progress).filter(
                    (s) => s === 'completed'
                  ).length
                }
                color="#10b981"
              />
              <StatBox
                label="In Progress"
                value={
                  Object.values(status.chapter_progress).filter(
                    (s) => s === 'running'
                  ).length
                }
                color="#3b82f6"
              />
              <StatBox
                label="Pending"
                value={
                  Object.values(status.chapter_progress).filter(
                    (s) => s === 'pending'
                  ).length
                }
                color="#9ca3af"
              />
            </View>
          </View>
        )}

        {/* Activity Log */}
        <View style={styles.logsSection}>
          <Text style={styles.sectionTitle}>Activity Log</Text>
          <View style={styles.logsContainer}>
            {(status.logs || [])
              .slice()
              .reverse()
              .slice(0, 10)
              .map((log, index) => (
                <LogEntry key={index} log={log} />
              ))}
          </View>
        </View>

        {/* Errors */}
        {status.errors && status.errors.length > 0 && (
          <View style={styles.errorsSection}>
            <Text style={styles.sectionTitle}>⚠️ Errors</Text>
            {status.errors.map((error, index) => (
              <View key={index} style={styles.errorBox}>
                <Text style={styles.errorPhase}>{error.phase}</Text>
                <Text style={styles.errorMessage}>{error.message}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Book Info */}
        <View style={styles.infoBox}>
          <Text style={styles.infoLabel}>Book ID</Text>
          <Text style={styles.infoValue}>{bookId}</Text>
          <Text style={styles.infoLabel}>Job ID</Text>
          <Text style={styles.infoValue}>{jobId}</Text>
          <Text style={styles.infoLabel}>Status</Text>
          <Text style={styles.infoValue}>{status.status}</Text>
        </View>
      </View>
    </ScrollView>
  );
}

function PhaseCard({ phase, status, isActive }) {
  const getIcon = () => {
    if (status === 'completed') return '✅';
    if (status === 'running') return '▶️';
    if (status === 'error') return '❌';
    return '⏸️';
  };

  const getColor = () => {
    if (status === 'completed') return '#10b981';
    if (status === 'running') return '#3b82f6';
    if (status === 'error') return '#ef4444';
    return '#9ca3af';
  };

  return (
    <View
      style={[
        styles.phaseCard,
        isActive && styles.phaseCardActive,
        { borderLeftColor: getColor() },
      ]}
    >
      <Text style={styles.phaseIcon}>{getIcon()}</Text>
      <Text style={[styles.phaseName, { color: getColor() }]}>{phase}</Text>
    </View>
  );
}

function StatBox({ label, value, color }) {
  return (
    <View style={[styles.statBox, { borderColor: color }]}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

function LogEntry({ log }) {
  const getColor = () => {
    if (log.level === 'success') return '#10b981';
    if (log.level === 'error') return '#ef4444';
    if (log.level === 'warning') return '#f59e0b';
    return '#6366f1';
  };

  return (
    <View style={styles.logEntry}>
      <Text style={styles.logTimestamp}>{log.timestamp}</Text>
      <Text style={[styles.logMessage, { color: getColor() }]}>
        {log.message}
      </Text>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#666',
  },
  progressSection: {
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
  progressBarContainer: {
    height: 24,
    backgroundColor: '#e5e7eb',
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 10,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#6366f1',
    borderRadius: 12,
  },
  progressText: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#6366f1',
  },
  phasesSection: {
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
  phasesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -5,
  },
  phaseCard: {
    width: '48%',
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    padding: 15,
    margin: '1%',
    borderLeftWidth: 4,
  },
  phaseCardActive: {
    backgroundColor: '#eff6ff',
  },
  phaseIcon: {
    fontSize: 20,
    marginBottom: 5,
  },
  phaseName: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  chaptersSection: {
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
  chapterStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statBox: {
    flex: 1,
    borderWidth: 2,
    borderRadius: 8,
    padding: 15,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  logsSection: {
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
  logsContainer: {
    maxHeight: 300,
  },
  logEntry: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  logTimestamp: {
    fontSize: 12,
    color: '#9ca3af',
    marginBottom: 2,
  },
  logMessage: {
    fontSize: 14,
  },
  errorsSection: {
    backgroundColor: '#fef2f2',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#ef4444',
  },
  errorBox: {
    marginBottom: 10,
  },
  errorPhase: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#dc2626',
    marginBottom: 5,
  },
  errorMessage: {
    fontSize: 14,
    color: '#991b1b',
  },
  infoBox: {
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    padding: 20,
  },
  infoLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 10,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#111827',
    marginTop: 2,
  },
});
