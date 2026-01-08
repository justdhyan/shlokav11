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
import { useRouter, useLocalSearchParams } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Mood {
  _id: string;
  emotion_id: string;
  name: string;
  description: string;
}

export default function MoodsScreen() {
  const [moods, setMoods] = useState<Mood[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { emotionId } = useLocalSearchParams();

  useEffect(() => {
    if (emotionId) {
      fetchMoods();
    }
  }, [emotionId]);

  const fetchMoods = async () => {
    try {
      // Try to get from cache first
      const cacheKey = `moods_${emotionId}`;
      const cached = await AsyncStorage.getItem(cacheKey);
      if (cached) {
        setMoods(JSON.parse(cached));
        setLoading(false);
      }

      // Fetch from API
      const response = await fetch(
        `${EXPO_PUBLIC_BACKEND_URL}/api/moods/${emotionId}`
      );
      const data = await response.json();

      setMoods(data);
      // Cache the data
      await AsyncStorage.setItem(cacheKey, JSON.stringify(data));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching moods:', error);
      setLoading(false);
    }
  };

  const handleMoodPress = (moodId: string) => {
    router.push(`/guidance?moodId=${moodId}`);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#8B7355" />
          <Text style={styles.loadingText}>Loading moods...</Text>
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
          <TouchableOpacity
            onPress={() => router.back()}
            style={styles.backButton}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>How do you feel?</Text>
          <Text style={styles.subtitle}>आप कैसा महसूस करते हैं?</Text>
        </View>

        {/* Moods List */}
        <View style={styles.moodsContainer}>
          {moods.map((mood) => (
            <TouchableOpacity
              key={mood._id}
              style={styles.moodCard}
              onPress={() => handleMoodPress(mood._id)}
              activeOpacity={0.7}
            >
              <View style={styles.moodContent}>
                <Text style={styles.moodName}>{mood.name}</Text>
                <Text style={styles.moodDescription}>{mood.description}</Text>
              </View>
              <Text style={styles.arrow}>→</Text>
            </TouchableOpacity>
          ))}
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
    paddingTop: 24,
    paddingBottom: 32,
    paddingHorizontal: 24,
    backgroundColor: '#F4E4C1',
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
  },
  backButton: {
    marginBottom: 16,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  backButtonText: {
    fontSize: 18,
    color: '#8B7355',
    fontWeight: '600',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#5D4E37',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#8B7355',
    textAlign: 'center',
  },
  moodsContainer: {
    paddingHorizontal: 16,
    paddingTop: 24,
  },
  moodCard: {
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 100,
  },
  moodContent: {
    flex: 1,
    paddingRight: 16,
  },
  moodName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 8,
  },
  moodDescription: {
    fontSize: 16,
    color: '#6B5D4F',
    lineHeight: 22,
  },
  arrow: {
    fontSize: 28,
    color: '#8B7355',
    fontWeight: 'bold',
  },
});
