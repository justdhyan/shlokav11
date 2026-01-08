import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Emotion {
  _id: string;
  name_english: string;
  name_sanskrit: string;
  description: string;
  icon: string;
}

export default function HomeScreen() {
  const [emotions, setEmotions] = useState<Emotion[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchEmotions();
  }, []);

  const fetchEmotions = async () => {
    try {
      // Try to get from cache first
      const cached = await AsyncStorage.getItem('emotions');
      if (cached) {
        setEmotions(JSON.parse(cached));
        setLoading(false);
      }

      // Fetch from API
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/emotions`);
      const data = await response.json();
      
      setEmotions(data);
      // Cache the data
      await AsyncStorage.setItem('emotions', JSON.stringify(data));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching emotions:', error);
      setLoading(false);
    }
  };

  const handleEmotionPress = (emotionId: string) => {
    router.push(`/moods?emotionId=${emotionId}`);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#8B7355" />
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.appName}>SHLOKA</Text>
          <Text style={styles.appNameSanskrit}>श्लोक</Text>
        </View>

        {/* Main Question */}
        <View style={styles.questionContainer}>
          <Text style={styles.question}>What is troubling you today?</Text>
          <Text style={styles.subQuestion}>आज आपको क्या परेशान कर रहा है?</Text>
        </View>

        {/* Emotions Grid */}
        <View style={styles.emotionsContainer}>
          {emotions.map((emotion) => (
            <TouchableOpacity
              key={emotion._id}
              style={styles.emotionCard}
              onPress={() => handleEmotionPress(emotion._id)}
              activeOpacity={0.7}
            >
              <View style={styles.emotionContent}>
                <Text style={styles.emotionName}>{emotion.name_english}</Text>
                <Text style={styles.emotionSanskrit}>{emotion.name_sanskrit}</Text>
                <Text style={styles.emotionDescription}>{emotion.description}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <TouchableOpacity
            onPress={() => router.push('/bookmarks')}
            style={styles.bookmarkButton}
          >
            <Text style={styles.bookmarkButtonText}>View Bookmarks</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FAF7F2',
  },
  scrollContent: {
    paddingBottom: 40,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 18,
    color: '#8B7355',
    fontWeight: '500',
  },
  header: {
    paddingTop: 32,
    paddingBottom: 24,
    alignItems: 'center',
    backgroundColor: '#F4E4C1',
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
  },
  appName: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#8B7355',
    letterSpacing: 2,
  },
  appNameSanskrit: {
    fontSize: 20,
    color: '#A0826D',
    marginTop: 4,
  },
  questionContainer: {
    paddingHorizontal: 24,
    paddingVertical: 32,
    alignItems: 'center',
  },
  question: {
    fontSize: 24,
    fontWeight: '600',
    color: '#5D4E37',
    textAlign: 'center',
    lineHeight: 32,
  },
  subQuestion: {
    fontSize: 18,
    color: '#8B7355',
    marginTop: 8,
    textAlign: 'center',
  },
  emotionsContainer: {
    paddingHorizontal: 16,
  },
  emotionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    marginHorizontal: 8,
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
    minHeight: 120,
  },
  emotionContent: {
    alignItems: 'flex-start',
  },
  emotionName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 4,
  },
  emotionSanskrit: {
    fontSize: 16,
    color: '#8B7355',
    marginBottom: 12,
  },
  emotionDescription: {
    fontSize: 16,
    color: '#6B5D4F',
    lineHeight: 22,
  },
  footer: {
    paddingHorizontal: 24,
    paddingTop: 24,
    alignItems: 'center',
  },
  bookmarkButton: {
    backgroundColor: '#6B9BD1',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    minWidth: 200,
    alignItems: 'center',
  },
  bookmarkButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
});
