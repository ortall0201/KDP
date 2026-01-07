/**
 * Completed Screen - Download finished manuscript
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import api from '../services/api';

export default function CompletedScreen({ route, navigation }) {
  const { jobId, bookId, wordCount } = route.params;
  const [downloading, setDownloading] = useState(false);

  const downloadManuscript = async () => {
    setDownloading(true);

    try {
      const downloadUrl = api.getDownloadUrl(jobId);
      const fileName = `ghostwritten_${bookId}.txt`;
      const fileUri = FileSystem.documentDirectory + fileName;

      // Download the file
      const downloadResult = await FileSystem.downloadAsync(
        downloadUrl,
        fileUri
      );

      if (downloadResult.status === 200) {
        // Check if sharing is available
        const canShare = await Sharing.isAvailableAsync();

        if (canShare) {
          // Share the file
          await Sharing.shareAsync(downloadResult.uri, {
            mimeType: 'text/plain',
            dialogTitle: 'Save Manuscript',
            UTI: 'public.plain-text',
          });

          Alert.alert(
            'Success',
            'Manuscript downloaded successfully! You can now save it to your preferred location.'
          );
        } else {
          Alert.alert(
            'Downloaded',
            `Manuscript saved to: ${fileUri}\n\nYou can find it in your device's file manager.`
          );
        }
      } else {
        throw new Error('Download failed');
      }
    } catch (error) {
      console.error('Download error:', error);
      Alert.alert(
        'Download Failed',
        'Failed to download manuscript. Please try again.'
      );
    } finally {
      setDownloading(false);
    }
  };

  const startNew = () => {
    navigation.navigate('Home');
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        {/* Success Icon */}
        <View style={styles.iconContainer}>
          <Text style={styles.successIcon}>✅</Text>
        </View>

        {/* Title */}
        <Text style={styles.title}>Processing Complete!</Text>
        <Text style={styles.subtitle}>
          Your manuscript has been ghostwritten and is ready to download.
        </Text>

        {/* Stats */}
        <View style={styles.statsContainer}>
          <StatCard
            icon="📚"
            label="Word Count"
            value={wordCount ? `${wordCount.toLocaleString()} words` : 'N/A'}
          />
          <StatCard icon="🆔" label="Book ID" value={bookId} />
        </View>

        {/* Download Button */}
        <TouchableOpacity
          style={[styles.downloadButton, downloading && styles.downloadButtonDisabled]}
          onPress={downloadManuscript}
          disabled={downloading}
        >
          {downloading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Text style={styles.downloadButtonText}>⬇️ Download Manuscript</Text>
            </>
          )}
        </TouchableOpacity>

        {/* Info Box */}
        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>What's Next?</Text>
          <Text style={styles.infoText}>
            • Review the ghostwritten manuscript{'\n'}
            • Make any final adjustments{'\n'}
            • Format for Kindle Direct Publishing{'\n'}
            • Upload to KDP and publish!
          </Text>
        </View>

        {/* New Manuscript Button */}
        <TouchableOpacity
          style={styles.newManuscriptButton}
          onPress={startNew}
        >
          <Text style={styles.newManuscriptButtonText}>
            📝 Process Another Manuscript
          </Text>
        </TouchableOpacity>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Processed by CrewAI Multi-Agent System
          </Text>
          <Text style={styles.footerSubtext}>Version 1.0.0</Text>
        </View>
      </View>
    </View>
  );
}

function StatCard({ icon, label, value }) {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statIcon}>{icon}</Text>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    marginBottom: 20,
  },
  successIcon: {
    fontSize: 80,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
    paddingHorizontal: 20,
  },
  statsContainer: {
    width: '100%',
    marginBottom: 30,
  },
  statCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  downloadButton: {
    backgroundColor: '#10b981',
    borderRadius: 12,
    paddingVertical: 18,
    paddingHorizontal: 40,
    width: '100%',
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  downloadButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  downloadButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoBox: {
    backgroundColor: '#eff6ff',
    borderRadius: 12,
    padding: 20,
    width: '100%',
    marginBottom: 20,
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
  newManuscriptButton: {
    backgroundColor: '#6366f1',
    borderRadius: 12,
    paddingVertical: 15,
    paddingHorizontal: 30,
    width: '100%',
    alignItems: 'center',
    marginBottom: 30,
  },
  newManuscriptButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  footer: {
    alignItems: 'center',
  },
  footerText: {
    fontSize: 12,
    color: '#9ca3af',
    marginBottom: 5,
  },
  footerSubtext: {
    fontSize: 10,
    color: '#d1d5db',
  },
});
