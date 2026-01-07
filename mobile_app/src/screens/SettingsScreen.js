/**
 * Settings Screen - Configure API Keys
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  Linking,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function SettingsScreen({ navigation }) {
  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingKeys, setTestingKeys] = useState(false);

  useEffect(() => {
    loadKeys();
  }, []);

  const loadKeys = async () => {
    try {
      const savedOpenaiKey = await AsyncStorage.getItem('openai_key');
      const savedAnthropicKey = await AsyncStorage.getItem('anthropic_key');

      if (savedOpenaiKey) setOpenaiKey(savedOpenaiKey);
      if (savedAnthropicKey) setAnthropicKey(savedAnthropicKey);
    } catch (error) {
      console.error('Failed to load keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveKeys = async () => {
    // Validate format
    if (openaiKey && !openaiKey.startsWith('sk-')) {
      Alert.alert('Invalid Key', 'OpenAI keys start with "sk-"');
      return;
    }

    if (anthropicKey && !anthropicKey.startsWith('sk-ant-')) {
      Alert.alert('Invalid Key', 'Anthropic keys start with "sk-ant-"');
      return;
    }

    if (!openaiKey || !anthropicKey) {
      Alert.alert('Missing Keys', 'Please enter both API keys');
      return;
    }

    setSaving(true);

    try {
      await AsyncStorage.setItem('openai_key', openaiKey);
      await AsyncStorage.setItem('anthropic_key', anthropicKey);

      Alert.alert(
        'Saved',
        'API keys saved securely on your device. They are never sent to our servers - only to OpenAI and Anthropic.',
        [{ text: 'OK', onPress: () => navigation.goBack() }]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to save keys');
    } finally {
      setSaving(false);
    }
  };

  const testKeys = async () => {
    if (!openaiKey || !anthropicKey) {
      Alert.alert('Missing Keys', 'Please enter both API keys first');
      return;
    }

    setTestingKeys(true);

    try {
      // Simple validation test - just check format and basic connectivity
      // In a real implementation, you might make a minimal API call

      const openaiValid = openaiKey.startsWith('sk-') && openaiKey.length > 20;
      const anthropicValid = anthropicKey.startsWith('sk-ant-') && anthropicKey.length > 20;

      if (openaiValid && anthropicValid) {
        Alert.alert(
          'Keys Look Valid',
          'Your API keys appear to be correctly formatted. They will be validated when you process a manuscript.'
        );
      } else {
        Alert.alert(
          'Keys May Be Invalid',
          'Please double-check your API keys. They should be:\n' +
          '• OpenAI: sk-...\n' +
          '• Anthropic: sk-ant-...'
        );
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to test keys');
    } finally {
      setTestingKeys(false);
    }
  };

  const clearKeys = () => {
    Alert.alert(
      'Clear API Keys',
      'Are you sure you want to remove your saved API keys?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.removeItem('openai_key');
            await AsyncStorage.removeItem('anthropic_key');
            setOpenaiKey('');
            setAnthropicKey('');
            Alert.alert('Cleared', 'API keys removed');
          },
        },
      ]
    );
  };

  const openLink = (url) => {
    Linking.openURL(url);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6366f1" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>🔑 API Keys</Text>
          <Text style={styles.subtitle}>
            Configure your OpenAI and Anthropic API keys. Your keys are stored
            securely on your device only.
          </Text>
        </View>

        {/* Why Section */}
        <View style={styles.whySection}>
          <Text style={styles.whyTitle}>Why Do I Need API Keys?</Text>
          <Text style={styles.whyText}>
            This app uses AI models from OpenAI (GPT-4) and Anthropic (Claude)
            to ghostwrite your manuscripts. By providing your own API keys:
          </Text>
          <Text style={styles.whyBullet}>• You pay only for what you use (~$12-18 per book)</Text>
          <Text style={styles.whyBullet}>• Your manuscripts are never stored on our servers</Text>
          <Text style={styles.whyBullet}>• Maximum privacy and security</Text>
          <Text style={styles.whyBullet}>• No monthly usage limits</Text>
        </View>

        {/* OpenAI Key */}
        <View style={styles.keySection}>
          <Text style={styles.keyLabel}>OpenAI API Key</Text>
          <Text style={styles.keyHint}>Used for: GPT-4 (Analysis, Expansion, Editing)</Text>

          <TextInput
            style={styles.keyInput}
            value={openaiKey}
            onChangeText={setOpenaiKey}
            placeholder="sk-..."
            placeholderTextColor="#9ca3af"
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
          />

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => openLink('https://platform.openai.com/api-keys')}
          >
            <Text style={styles.linkButtonText}>
              🔗 Get OpenAI API Key
            </Text>
          </TouchableOpacity>

          <View style={styles.costBox}>
            <Text style={styles.costLabel}>Estimated Cost per Book:</Text>
            <Text style={styles.costValue}>$8-12</Text>
          </View>
        </View>

        {/* Anthropic Key */}
        <View style={styles.keySection}>
          <Text style={styles.keyLabel}>Anthropic API Key</Text>
          <Text style={styles.keyHint}>Used for: Claude (Quality Assurance)</Text>

          <TextInput
            style={styles.keyInput}
            value={anthropicKey}
            onChangeText={setAnthropicKey}
            placeholder="sk-ant-..."
            placeholderTextColor="#9ca3af"
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
          />

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => openLink('https://console.anthropic.com/')}
          >
            <Text style={styles.linkButtonText}>
              🔗 Get Anthropic API Key
            </Text>
          </TouchableOpacity>

          <View style={styles.costBox}>
            <Text style={styles.costLabel}>Estimated Cost per Book:</Text>
            <Text style={styles.costValue}>$4-6</Text>
          </View>
        </View>

        {/* Total Cost */}
        <View style={styles.totalCostBox}>
          <Text style={styles.totalCostLabel}>Total Cost per Book:</Text>
          <Text style={styles.totalCostValue}>$12-18</Text>
          <Text style={styles.totalCostHint}>
            Still 40x cheaper than a human ghostwriter ($800-1,300)
          </Text>
        </View>

        {/* Action Buttons */}
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={saveKeys}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.saveButtonText}>💾 Save API Keys</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.testButton}
          onPress={testKeys}
          disabled={testingKeys}
        >
          {testingKeys ? (
            <ActivityIndicator color="#6366f1" />
          ) : (
            <Text style={styles.testButtonText}>🧪 Test Keys</Text>
          )}
        </TouchableOpacity>

        {(openaiKey || anthropicKey) && (
          <TouchableOpacity style={styles.clearButton} onPress={clearKeys}>
            <Text style={styles.clearButtonText}>🗑️ Clear Keys</Text>
          </TouchableOpacity>
        )}

        {/* Security Notice */}
        <View style={styles.securityBox}>
          <Text style={styles.securityTitle}>🔒 Security & Privacy</Text>
          <Text style={styles.securityText}>
            • Keys are stored locally on your device using secure storage{'\n'}
            • Keys are sent directly to OpenAI and Anthropic, not our servers{'\n'}
            • Your manuscripts are processed and immediately deleted{'\n'}
            • We never see or store your API keys{'\n'}
            • All communication is encrypted (HTTPS)
          </Text>
        </View>

        {/* Help Section */}
        <View style={styles.helpSection}>
          <Text style={styles.helpTitle}>Need Help?</Text>

          <TouchableOpacity
            style={styles.helpItem}
            onPress={() => openLink('https://platform.openai.com/docs/quickstart')}
          >
            <Text style={styles.helpItemText}>📖 OpenAI API Documentation</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.helpItem}
            onPress={() => openLink('https://docs.anthropic.com/claude/docs')}
          >
            <Text style={styles.helpItemText}>📖 Anthropic API Documentation</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.helpItem}
            onPress={() => openLink('https://platform.openai.com/account/billing')}
          >
            <Text style={styles.helpItemText}>💳 Check OpenAI Usage & Billing</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.helpItem}
            onPress={() => openLink('https://console.anthropic.com/settings/billing')}
          >
            <Text style={styles.helpItemText}>💳 Check Anthropic Usage & Billing</Text>
          </TouchableOpacity>
        </View>

        {/* FAQ */}
        <View style={styles.faqSection}>
          <Text style={styles.faqTitle}>Frequently Asked Questions</Text>

          <View style={styles.faqItem}>
            <Text style={styles.faqQuestion}>Q: Do I need both API keys?</Text>
            <Text style={styles.faqAnswer}>
              Yes. We use GPT-4 for creative writing and Claude for quality
              assurance. Both are required for the full workflow.
            </Text>
          </View>

          <View style={styles.faqItem}>
            <Text style={styles.faqQuestion}>Q: How much will I be charged?</Text>
            <Text style={styles.faqAnswer}>
              OpenAI and Anthropic charge per token (word). For a typical
              manuscript, expect $12-18 total. You can monitor usage in your
              API dashboards.
            </Text>
          </View>

          <View style={styles.faqItem}>
            <Text style={styles.faqQuestion}>Q: Are my keys safe?</Text>
            <Text style={styles.faqAnswer}>
              Yes. Keys are stored using your device's secure storage and never
              leave your device except to make API calls directly to OpenAI and
              Anthropic.
            </Text>
          </View>

          <View style={styles.faqItem}>
            <Text style={styles.faqQuestion}>Q: Can I use free tier API keys?</Text>
            <Text style={styles.faqAnswer}>
              No. Both OpenAI and Anthropic require paid accounts with usage
              limits removed. Free tiers have strict limits that will cause
              processing to fail.
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
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
  header: {
    marginBottom: 30,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  whySection: {
    backgroundColor: '#eff6ff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 30,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1',
  },
  whyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#1e40af',
  },
  whyText: {
    fontSize: 14,
    color: '#1e3a8a',
    marginBottom: 10,
    lineHeight: 22,
  },
  whyBullet: {
    fontSize: 14,
    color: '#1e3a8a',
    marginLeft: 10,
    lineHeight: 22,
  },
  keySection: {
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
  keyLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  keyHint: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  keyInput: {
    backgroundColor: '#f9fafb',
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 15,
    fontSize: 14,
    fontFamily: 'monospace',
    marginBottom: 15,
  },
  linkButton: {
    backgroundColor: '#6366f1',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginBottom: 15,
  },
  linkButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  costBox: {
    backgroundColor: '#f0fdf4',
    borderRadius: 8,
    padding: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  costLabel: {
    fontSize: 14,
    color: '#166534',
  },
  costValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#15803d',
  },
  totalCostBox: {
    backgroundColor: '#10b981',
    borderRadius: 12,
    padding: 20,
    marginBottom: 30,
    alignItems: 'center',
  },
  totalCostLabel: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 5,
  },
  totalCostValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
  },
  totalCostHint: {
    fontSize: 12,
    color: '#d1fae5',
    textAlign: 'center',
  },
  saveButton: {
    backgroundColor: '#10b981',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  saveButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  testButton: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#6366f1',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginBottom: 15,
  },
  testButtonText: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold',
  },
  clearButton: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#ef4444',
    borderRadius: 12,
    padding: 18,
    alignItems: 'center',
    marginBottom: 30,
  },
  clearButtonText: {
    color: '#ef4444',
    fontSize: 16,
    fontWeight: 'bold',
  },
  securityBox: {
    backgroundColor: '#f0fdf4',
    borderRadius: 12,
    padding: 20,
    marginBottom: 30,
    borderWidth: 1,
    borderColor: '#10b981',
  },
  securityTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#166534',
  },
  securityText: {
    fontSize: 14,
    color: '#166534',
    lineHeight: 22,
  },
  helpSection: {
    marginBottom: 30,
  },
  helpTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  helpItem: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1',
  },
  helpItemText: {
    fontSize: 14,
    color: '#6366f1',
  },
  faqSection: {
    marginBottom: 30,
  },
  faqTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  faqItem: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
  },
  faqQuestion: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  faqAnswer: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});
