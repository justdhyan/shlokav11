import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  SafeAreaView,
  ImageBackground,
  Pressable,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

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
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { emotionId } = useLocalSearchParams();

  useEffect(() => {
    if (emotionId) {
      fetchMoods();
    }
  }, [emotionId]);

  const fetchMoods = async () => {
    try {
      setError(null);
      
      // Check if backend URL is configured
      if (!EXPO_PUBLIC_BACKEND_URL) {
        console.error('EXPO_PUBLIC_BACKEND_URL is not defined');
        setError('Configuration error. Please check your setup.');
        setLoading(false);
        return;
      }

      // Try to get from cache first for instant display
      const cacheKey = `moods_${emotionId}`;
      const cached = await AsyncStorage.getItem(cacheKey);
      if (cached) {
        setMoods(JSON.parse(cached));
        // Don't stop loading yet - we still want to fetch fresh data
      }

      // Fetch from API
      const response = await fetch(
        `${EXPO_PUBLIC_BACKEND_URL}/api/moods/${emotionId}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();

      if (!data || data.length === 0) {
        throw new Error('No moods found for this emotion');
      }

      setMoods(data);
      // Cache the data
      await AsyncStorage.setItem(cacheKey, JSON.stringify(data));
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching moods:', error);
      setError('Unable to load moods. Please try again.');
      setLoading(false);
      
      // If we don't have cached data, this is a real problem
      if (moods.length === 0) {
        setError('Unable to connect to server. Please check your internet connection and try again.');
      }
    }
  };

  const handleMoodPress = (moodId: string) => {
    router.push(`/guidance?moodId=${moodId}`);
  };

  if (loading && moods.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <ImageBackground
          source={{ uri: 'https://images.unsplash.com/photo-1608509643848-5e00349cf077?w=800' }}
          style={styles.loadingBackground}
          blurRadius={3}
        >
          <LinearGradient
            colors={['rgba(250, 247, 242, 0.9)', 'rgba(244, 228, 193, 0.95)']}
            style={styles.loadingGradient}
          >
            <ActivityIndicator size="large" color="#8B7355" />
            <Text style={styles.loadingText}>Loading moods...</Text>
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
                <Pressable onPress={fetchMoods} style={styles.retryButton}>
                  <Text style={styles.retryButtonText}>Retry</Text>
                </Pressable>
              </View>
            )}
          </LinearGradient>
        </ImageBackground>
      </SafeAreaView>
    );
  }

  // Show empty state if no data available
  if (!loading && moods.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <ImageBackground
          source={{ uri: 'https://images.unsplash.com/photo-1608509643848-5e00349cf077?w=800' }}
          style={styles.loadingBackground}
          blurRadius={3}
        >
          <LinearGradient
            colors={['rgba(250, 247, 242, 0.9)', 'rgba(244, 228, 193, 0.95)']}
            style={styles.loadingGradient}
          >
            <Text style={styles.emptyStateText}>🤔</Text>
            <Text style={styles.emptyStateTitle}>No Moods Available</Text>
            <Text style={styles.emptyStateMessage}>
              {error || 'Unable to find moods for this emotion.'}
            </Text>
            <Pressable onPress={fetchMoods} style={styles.retryButton}>
              <Text style={styles.retryButtonText}>Try Again</Text>
            </Pressable>
            <Pressable onPress={() => router.back()} style={[styles.retryButton, { marginTop: 12, backgroundColor: '#6B9BD1' }]}>
              <Text style={styles.retryButtonText}>Go Back</Text>
            </Pressable>
          </LinearGradient>
        </ImageBackground>
      </SafeAreaView>
    );
  }

  return (
    <View style={styles.container}>
      <ImageBackground
        source={{ uri: 'https://images.unsplash.com/photo-1591757311543-5fa5af831901?w=1200' }}
        style={styles.backgroundImage}
        resizeMode="cover"
      >
        <LinearGradient
          colors={['rgba(250, 247, 242, 0.85)', 'rgba(250, 247, 242, 0.95)', 'rgba(250, 247, 242, 1)']}
          locations={[0, 0.3, 0.7]}
          style={styles.gradient}
        >
          <SafeAreaView style={styles.safeArea}>
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
                <View style={styles.titleContainer}>
                  <Text style={styles.title}>How do you feel?</Text>
                  <Text style={styles.subtitle}>आप कैसा महसूस करते हैं?</Text>
                </View>
              </View>

              {/* Moods List */}
              <View style={styles.moodsContainer}>
                {moods.map((mood, index) => (
                  <TouchableOpacity
                    key={mood._id}
                    style={styles.moodCard}
                    onPress={() => handleMoodPress(mood._id)}
                    activeOpacity={0.8}
                  >
                    <LinearGradient
                      colors={['#FFFFFF', '#FEFCF8']}
                      style={styles.moodCardGradient}
                    >
                      <View style={styles.moodNumber}>
                        <Text style={styles.moodNumberText}>{index + 1}</Text>
                      </View>
                      <View style={styles.moodContent}>
                        <Text style={styles.moodName}>{mood.name}</Text>
                        <Text style={styles.moodDescription}>{mood.description}</Text>
                      </View>
                      <View style={styles.arrowContainer}>
                        <Text style={styles.arrow}>→</Text>
                      </View>
                    </LinearGradient>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>
          </SafeAreaView>
        </LinearGradient>
      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  gradient: {
    flex: 1,
  },
  safeArea: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  loadingBackground: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingGradient: {
    flex: 1,
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 18,
    color: '#8B7355',
    fontWeight: '500',
  },
  errorContainer: {
    marginTop: 24,
    padding: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 12,
    marginHorizontal: 24,
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#B33A3A',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 24,
  },
  retryButton: {
    backgroundColor: '#8B7355',
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  emptyStateText: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyStateTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 12,
    textAlign: 'center',
  },
  emptyStateMessage: {
    fontSize: 16,
    color: '#8B7355',
    textAlign: 'center',
    marginBottom: 24,
    paddingHorizontal: 24,
    lineHeight: 24,
  },
  header: {
    paddingTop: 24,
    paddingBottom: 32,
    paddingHorizontal: 24,
  },
  backButton: {
    marginBottom: 20,
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 12,
    alignSelf: 'flex-start',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  backButtonText: {
    fontSize: 18,
    color: '#8B7355',
    fontWeight: '700',
  },
  titleContainer: {
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingVertical: 20,
    paddingHorizontal: 24,
    borderRadius: 16,
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 5,
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
    fontWeight: '500',
  },
  moodsContainer: {
    paddingHorizontal: 16,
    paddingTop: 24,
  },
  moodCard: {
    marginBottom: 18,
    marginHorizontal: 8,
    borderRadius: 18,
    overflow: 'hidden',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 6,
  },
  moodCardGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    minHeight: 110,
  },
  moodNumber: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#D4AF37',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  moodNumberText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  moodContent: {
    flex: 1,
    paddingRight: 12,
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
  arrowContainer: {
    justifyContent: 'center',
  },
  arrow: {
    fontSize: 32,
    color: '#8B7355',
    fontWeight: 'bold',
  },
});