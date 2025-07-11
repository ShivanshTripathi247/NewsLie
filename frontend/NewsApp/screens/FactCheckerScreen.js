import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  StatusBar,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import newsAPI from '../services/api';

const FactCheckerScreen = () => {
  const [inputText, setInputText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);

  // Message template functions
  const getNotTrustedMessage = (analysisDetails) => {
    return {
      mainMessage: "⚠️ MISINFORMATION DETECTED",
      subtitle: "This content shows multiple warning signs of false information",
      details: [
        "🚨 High Risk: Strong indicators of misinformation detected",
        "🔍 AI Analysis: Content patterns match known false information",
        "📊 Confidence: Low credibility across multiple verification layers",
        "🛡️ Recommendation: Do not trust, share, or act on this information"
      ],
      actionAdvice: {
        title: "💡 What You Should Do:",
        actions: [
          "❌ Do not share this content on social media",
          "🔍 Verify claims with trusted news sources",
          "📚 Check fact-checkers like Snopes or PolitiFact",
          "🗣️ Warn others if you see this content being shared"
        ]
      },
      warningNote: "⚡ Remember: Sharing false information can harm others and damage your credibility"
    };
  };

  const getUncertainMessage = (analysisDetails) => {
    return {
      mainMessage: "⚠️ PROCEED WITH CAUTION",
      subtitle: "This content has mixed credibility signals",
      details: [
        "🤔 Mixed Signals: Some credible elements, but concerns detected",
        "🔍 AI Analysis: Uncertain classification with moderate confidence",
        "📊 Verification: Partial confirmation from reliable sources",
        "🛡️ Recommendation: Verify before sharing or acting on this information"
      ],
      actionAdvice: {
        title: "💡 What You Should Do:",
        actions: [
          "🔍 Cross-check with 2-3 trusted news sources",
          "📰 Look for coverage in mainstream media outlets",
          "⏰ Wait for updates - developing stories may lack complete information",
          "🤝 Share responsibly - add context if you must share"
        ]
      },
      warningNote: "📝 Tip: When in doubt, it's better to wait for more information than to spread uncertainty"
    };
  };

  const getTrustedMessage = (analysisDetails) => {
    return {
      mainMessage: "✅ CREDIBLE INFORMATION",
      subtitle: "This content appears reliable and trustworthy",
      details: [
        "🛡️ High Credibility: Strong indicators of legitimate information",
        "🔍 AI Analysis: Content patterns match verified news sources",
        "📊 Verification: Confirmed by multiple reliable sources",
        "✅ Recommendation: Generally safe to trust and share"
      ],
      actionAdvice: {
        title: "💡 What You Should Do:",
        actions: [
          "✅ Safe to share with proper attribution",
          "📰 Check original source for complete context",
          "🔗 Share responsibly - include source links when possible",
          "📚 Stay informed - follow up on developing stories"
        ]
      },
      warningNote: "🌟 Remember: Even credible information can evolve - stay updated on developing stories"
    };
  };

  // Enhanced message rendering function (moved inside component)
  const renderEnhancedMessage = (analysisResult) => {
    const score = analysisResult.credibility_score;
    let messageTemplate;

    if (score >= 70) {
      messageTemplate = getTrustedMessage(analysisResult);
    } else if (score >= 40) {
      messageTemplate = getUncertainMessage(analysisResult);
    } else {
      messageTemplate = getNotTrustedMessage(analysisResult);
    }

    return (
      <View style={styles.enhancedMessageContainer}>
        {/* Main Message Header */}
        <View style={styles.messageHeader}>
          <Text style={styles.mainMessage}>{messageTemplate.mainMessage}</Text>
          <Text style={styles.messageSubtitle}>{messageTemplate.subtitle}</Text>
        </View>

        {/* Analysis Details */}
        <View style={styles.detailsSection}>
          <Text style={styles.sectionTitle}>📋 Analysis Summary</Text>
          {messageTemplate.details.map((detail, index) => (
            <Text key={index} style={styles.detailItem}>{detail}</Text>
          ))}
        </View>

        {/* Action Advice */}
        <View style={styles.adviceSection}>
          <Text style={styles.sectionTitle}>{messageTemplate.actionAdvice.title}</Text>
          {messageTemplate.actionAdvice.actions.map((action, index) => (
            <Text key={index} style={styles.actionItem}>{action}</Text>
          ))}
        </View>

        {/* Warning/Tip Note */}
        <View style={styles.warningSection}>
          <Text style={styles.warningText}>{messageTemplate.warningNote}</Text>
        </View>
      </View>
    );
  };

  const analyzeNews = async () => {
    if (!inputText.trim()) {
      Alert.alert('Input Required', 'Please enter a news headline or article to analyze.');
      return;
    }

    if (inputText.length < 20) {
      Alert.alert('Text Too Short', 'Please enter at least 20 characters for accurate analysis.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      console.log('🔄 Starting analysis...');
      const response = await newsAPI.analyzeNews(inputText.trim());
      console.log('✅ API Response received:', response);
      
      setAnalysisResult(response);
      console.log('📊 Analysis result set in state');
      
      // Add to history
      const historyItem = {
        id: Date.now(),
        text: inputText.trim(),
        result: response,
        timestamp: new Date().toISOString(),
      };
      setAnalysisHistory(prev => [historyItem, ...prev.slice(0, 4)]);
      
    } catch (error) {
      console.error('❌ Analysis error:', error);
      Alert.alert('Analysis Failed', 'Unable to analyze the news. Please try again.');
    } finally {
      setIsAnalyzing(false);
      console.log('🏁 Analysis completed');
    }
  };

  const clearInput = () => {
    setInputText('');
    setAnalysisResult(null);
  };

  const getTrustIndicator = (score) => {
    if (score >= 70) {
      return {
        icon: 'shield-checkmark',
        color: '#27ae60',
        label: 'TRUSTED',
        bgColor: '#d5f4e6'
      };
    } else if (score >= 40) {
      return {
        icon: 'shield',
        color: '#f39c12',
        label: 'UNCERTAIN',
        bgColor: '#fef9e7'
      };
    } else {
      return {
        icon: 'shield-outline',
        color: '#e74c3c',
        label: 'NOT TRUSTED',
        bgColor: '#fadbd8'
      };
    }
  };

  const renderAnalysisResult = () => {
    console.log('🎨 renderAnalysisResult called');
    console.log('📊 analysisResult:', analysisResult);

    if (!analysisResult) {
      console.log('❌ No analysis result, returning null');
      return null;
    }

    console.log('✅ Analysis result exists, rendering...');
    const trustInfo = getTrustIndicator(analysisResult.credibility_score);

    return (
      <View style={styles.resultContainer}>
        <View style={[styles.trustIndicator, { backgroundColor: trustInfo.bgColor }]}>
          <Ionicons name={trustInfo.icon} size={32} color={trustInfo.color} />
          <Text style={[styles.trustLabel, { color: trustInfo.color }]}>
            {trustInfo.label}
          </Text>
        </View>

        <View style={styles.scoreContainer}>
          <Text style={styles.scoreLabel}>Credibility Score</Text>
          <Text style={[styles.scoreValue, { color: trustInfo.color }]}>
            {analysisResult.credibility_score}/100
          </Text>
        </View>

        {renderEnhancedMessage(analysisResult)}

        <View style={styles.detailsContainer}>
          <Text style={styles.detailsTitle}>Technical Analysis:</Text>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>AI Prediction:</Text>
            <Text style={styles.detailValue}>
              {analysisResult.ml_analysis?.prediction || 'N/A'}
            </Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Confidence:</Text>
            <Text style={styles.detailValue}>
              {analysisResult.ml_analysis?.confidence || 'N/A'}%
            </Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Risk Level:</Text>
            <Text style={styles.detailValue}>{analysisResult.risk_level}</Text>
          </View>
        </View>

        <Text style={styles.recommendation}>
          💡 {analysisResult.recommendation}
        </Text>
      </View>
    );
  };

  const renderHistoryItem = (item) => {
    const trustInfo = getTrustIndicator(item.result.credibility_score);
    
    return (
      <TouchableOpacity 
        key={item.id} 
        style={styles.historyItem}
        onPress={() => {
          setInputText(item.text);
          setAnalysisResult(item.result);
        }}
      >
        <View style={styles.historyHeader}>
          <Ionicons name={trustInfo.icon} size={20} color={trustInfo.color} />
          <Text style={[styles.historyScore, { color: trustInfo.color }]}>
            {item.result.credibility_score}/100
          </Text>
        </View>
        <Text style={styles.historyText} numberOfLines={2}>
          {item.text}
        </Text>
        <Text style={styles.historyTime}>
          {new Date(item.timestamp).toLocaleTimeString()}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🔍 Fact Checker</Text>
        <Text style={styles.headerSubtitle}>Verify news credibility with AI</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Input Section */}
        <View style={styles.inputSection}>
          <Text style={styles.inputLabel}>Enter news headline or article:</Text>
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.textInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder="Paste or type the news content you want to verify..."
              multiline
              maxLength={1000}
              textAlignVertical="top"
            />
            {inputText.length > 0 && (
              <TouchableOpacity style={styles.clearButton} onPress={clearInput}>
                <Ionicons name="close-circle" size={20} color="#95a5a6" />
              </TouchableOpacity>
            )}
          </View>
          <Text style={styles.charCount}>{inputText.length}/1000 characters</Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionContainer}>
          <TouchableOpacity 
            style={[
              styles.analyzeButton, 
              (!inputText.trim() || isAnalyzing) && styles.analyzeButtonDisabled
            ]}
            onPress={analyzeNews}
            disabled={!inputText.trim() || isAnalyzing}
          >
            {isAnalyzing ? (
              <Text style={styles.analyzeButtonText}>🔄 Analyzing...</Text>
            ) : (
              <Text style={styles.analyzeButtonText}>🔍 Check Credibility</Text>
            )}
          </TouchableOpacity>
        </View>

        {/* Analysis Result */}
        {renderAnalysisResult()}

        {/* Recent Analysis History */}
        {analysisHistory.length > 0 && (
          <View style={styles.historySection}>
            <Text style={styles.historyTitle}>Recent Checks</Text>
            {analysisHistory.map(renderHistoryItem)}
          </View>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#7f8c8d',
  },
  content: {
    flex: 1,
  },
  inputSection: {
    backgroundColor: 'white',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 12,
  },
  inputContainer: {
    position: 'relative',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ecf0f1',
    borderRadius: 8,
    padding: 12,
    minHeight: 120,
    fontSize: 16,
    lineHeight: 22,
    backgroundColor: '#fafafa',
  },
  clearButton: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  charCount: {
    fontSize: 12,
    color: '#95a5a6',
    textAlign: 'right',
    marginTop: 4,
  },
  actionContainer: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  analyzeButton: {
    backgroundColor: '#3498db',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  analyzeButtonDisabled: {
    backgroundColor: '#bdc3c7',
  },
  analyzeButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  resultContainer: {
    backgroundColor: 'white',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  trustIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  trustLabel: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 12,
  },
  scoreContainer: {
    alignItems: 'center',
    marginBottom: 16,
  },
  scoreLabel: {
    fontSize: 14,
    color: '#7f8c8d',
    marginBottom: 4,
  },
  scoreValue: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  detailsContainer: {
    marginBottom: 16,
  },
  detailsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 8,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  detailLabel: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#2c3e50',
  },
  recommendation: {
    fontSize: 14,
    color: '#34495e',
    fontStyle: 'italic',
    textAlign: 'center',
    lineHeight: 20,
  },
  historySection: {
    margin: 16,
  },
  historyTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 12,
  },
  historyItem: {
    backgroundColor: 'white',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  historyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  historyScore: {
    fontSize: 12,
    fontWeight: 'bold',
    marginLeft: 6,
  },
  historyText: {
    fontSize: 14,
    color: '#2c3e50',
    marginBottom: 4,
  },
  historyTime: {
    fontSize: 12,
    color: '#95a5a6',
  },
  // Enhanced message styles
  enhancedMessageContainer: {
    backgroundColor: '#f8f9fa',
    padding: 20,
    borderRadius: 12,
    marginVertical: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#3498db',
  },
  messageHeader: {
    marginBottom: 16,
    alignItems: 'center',
  },
  mainMessage: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
    marginBottom: 8,
  },
  messageSubtitle: {
    fontSize: 16,
    color: '#34495e',
    textAlign: 'center',
    lineHeight: 22,
  },
  detailsSection: {
    marginBottom: 16,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
  },
  adviceSection: {
    marginBottom: 16,
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 12,
  },
  detailItem: {
    fontSize: 14,
    color: '#34495e',
    lineHeight: 20,
    marginBottom: 6,
  },
  actionItem: {
    fontSize: 14,
    color: '#34495e',
    lineHeight: 20,
    marginBottom: 6,
  },
  warningSection: {
    backgroundColor: '#e8f4fd',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#3498db',
  },
  warningText: {
    fontSize: 13,
    color: '#2c3e50',
    fontStyle: 'italic',
    lineHeight: 18,
  },
});

export default FactCheckerScreen;
