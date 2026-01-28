import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  ImageBackground,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Guidance {
  _id: string;
  mood_id: string;
  title: string;
  verse_reference: string;
  sanskrit_verse: string;
  english_translation: string;
  guidance_text: string;
}

export default function GuidanceScreen() {
  const [guidance, setGuidance] = useState<Guidance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  const router = useRouter();
  const { moodId } = useLocalSearchParams();

  useEffect(() => {
    if (moodId) {
      fetchGuidance();
    }
  }, [moodId]);

  useEffect(() => {
    if (guidance) {
      checkBookmarkStatus();
    }
  }, [guidance]);

  const fetchGuidance = async (isRetry = false) => {
    try {
      if (isRetry) {
        setIsRetrying(true);
        setRetryCount(prev => prev + 1);
      } else {
        setRetryCount(0);
      }
      
      setError(null);
      
      // Check if backend URL is configured
      if (!EXPO_PUBLIC_BACKEND_URL) {
        console.error('EXPO_PUBLIC_BACKEND_URL is not defined');
        setError('Configuration error. Please check your setup.');
        setLoading(false);
        setIsRetrying(false);
        return;
      }

      // Try to get from cache first for instant display
      const cacheKey = `guidance_${moodId}`;
      const cached = await AsyncStorage.getItem(cacheKey);
      if (cached) {
        const cachedData = JSON.parse(cached);
        setGuidance(cachedData);
        // If we have cached data, we can stop loading immediately
        // and update in background
        if (isRetry) {
          setLoading(false);
          setIsRetrying(false);
        }
      }

      // Fetch from API with longer timeout for slow connections
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(
        `${EXPO_PUBLIC_BACKEND_URL}/api/guidance/${moodId}`,
        { signal: controller.signal }
      );
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        // If we have cached data and get a network error, just use cached
        if (cached && response.status >= 500) {
          console.log('Using cached data due to server error');
          setLoading(false);
          setIsRetrying(false);
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();

      if (!data || !data.title) {
        throw new Error('Invalid guidance data received');
      }

      setGuidance(data);
      // Cache the data
      await AsyncStorage.setItem(cacheKey, JSON.stringify(data));
      setLoading(false);
      setIsRetrying(false);
      setError(null);
    } catch (error: any) {
      console.error('Error fetching guidance:', error);
      
      // If we have cached data, use it and show a gentle notice
      if (guidance) {
        setError('Showing saved guidance. Network unavailable.');
        setLoading(false);
        setIsRetrying(false);
        return;
      }
      
      // More user-friendly error messages
      if (error.name === 'AbortError') {
        setError('Connection is slow. Please wait...');
        // Auto-retry once for timeouts
        if (retryCount < 1) {
          setTimeout(() => fetchGuidance(true), 1000);
        }
      } else if (error.message.includes('Failed to fetch') || error.message.includes('Network')) {
        setError('Please check your internet connection and try again.');
      } else {
        setError('Having trouble loading guidance. Please try again.');
      }
      
      setLoading(false);
      setIsRetrying(false);
    }
  };

  const checkBookmarkStatus = async () => {
    try {
      const bookmarks = await AsyncStorage.getItem('bookmarks');
      if (bookmarks) {
        const bookmarksList = JSON.parse(bookmarks);
        const isAlreadyBookmarked = bookmarksList.some(
          (b: Guidance) => b._id === guidance?._id
        );
        setIsBookmarked(isAlreadyBookmarked);
      }
    } catch (error) {
      console.error('Error checking bookmark status:', error);
    }
  };

  const toggleBookmark = async () => {
    if (!guidance) return;

    try {
      const bookmarks = await AsyncStorage.getItem('bookmarks');
      let bookmarksList: Guidance[] = bookmarks ? JSON.parse(bookmarks) : [];

      if (isBookmarked) {
        // Remove bookmark
        bookmarksList = bookmarksList.filter((b) => b._id !== guidance._id);
        setIsBookmarked(false);
        Alert.alert('Removed', 'Guidance removed from bookmarks');
      } else {
        // Add bookmark
        bookmarksList.push(guidance);
        setIsBookmarked(true);
        Alert.alert('Saved', 'Guidance saved to bookmarks');
      }

      await AsyncStorage.setItem('bookmarks', JSON.stringify(bookmarksList));
    } catch (error) {
      console.error('Error toggling bookmark:', error);
      Alert.alert('Error', 'Failed to save bookmark');
    }
  };

  if (loading && !guidance) {
    return (
      <SafeAreaView style={styles.container}>
        <ImageBackground
          source={{ uri: 'https://images.unsplash.com/photo-1718179401998-ffc309805882?w=800' }}
          style={styles.loadingBackground}
          blurRadius={3}
        >
          <LinearGradient
            colors={['rgba(250, 247, 242, 0.9)', 'rgba(244, 228, 193, 0.95)']}
            style={styles.loadingGradient}
          >
            <Text style={styles.emptyStateText}>🙏</Text>
            <ActivityIndicator size="large" color="#8B7355" />
            <Text style={styles.loadingText}>
              {isRetrying ? 'Reconnecting...' : 'Loading your guidance...'}
            </Text>
            <Text style={styles.loadingSubtext}>
              {isRetrying ? 'Please be patient' : 'Preparing sacred wisdom for you'}
            </Text>
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
                {!isRetrying && (
                  <Pressable onPress={() => fetchGuidance(true)} style={styles.retryButton}>
                    <Text style={styles.retryButtonText}>Try Again</Text>
                  </Pressable>
                )}
              </View>
            )}
          </LinearGradient>
        </ImageBackground>
      </SafeAreaView>
    );
  }

  if (!guidance) {
    return (
      <SafeAreaView style={styles.container}>
        <ImageBackground
          source={{ uri: 'https://images.unsplash.com/photo-1718179401998-ffc309805882?w=800' }}
          style={styles.loadingBackground}
          blurRadius={3}
        >
          <LinearGradient
            colors={['rgba(250, 247, 242, 0.9)', 'rgba(244, 228, 193, 0.95)']}
            style={styles.loadingGradient}
          >
            <Text style={styles.emptyStateText}>🙏</Text>
            <Text style={styles.emptyStateTitle}>Having Trouble Loading</Text>
            <Text style={styles.emptyStateMessage}>
              {error || 'We are having difficulty retrieving your guidance right now.'}
            </Text>
            <Text style={styles.helpText}>
              💡 This usually means your internet connection needs attention
            </Text>
            <Pressable onPress={() => fetchGuidance(true)} style={styles.retryButton}>
              <Text style={styles.retryButtonText}>🔄 Try Again</Text>
            </Pressable>
            <Pressable
              onPress={() => router.back()}
              style={[styles.retryButton, { marginTop: 12, backgroundColor: '#6B9BD1' }]}
            >
              <Text style={styles.retryButtonText}>← Go Back</Text>
            </Pressable>
          </LinearGradient>
        </ImageBackground>
      </SafeAreaView>
    );
  }

  return (
    <View style={styles.container}>
      <ImageBackground
        source={{ uri: 'https://images.unsplash.com/photo-1707249935951-d92bf3a65b00?w=1200' }}
        style={styles.backgroundImage}
        resizeMode="cover"
      >
        <LinearGradient
          colors={['rgba(250, 247, 242, 0.9)', 'rgba(250, 247, 242, 0.95)', 'rgba(250, 247, 242, 1)']}
          locations={[0, 0.2, 0.5]}
          style={styles.gradient}
        >
          <SafeAreaView style={styles.safeArea}>
            {error && error.includes('saved guidance') && (
              <View style={styles.notificationBanner}>
                <Text style={styles.notificationText}>📱 {error}</Text>
              </View>
            )}
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
                  <Text style={styles.backButtonText}>Back</Text>
                </TouchableOpacity>
              </View>

              {/* Content */}
              <View style={styles.content}>
                {/* Title */}
                <Text style={styles.title}>{guidance.title}</Text>

                {/* Verse Reference */}
                <View style={styles.verseReferenceContainer}>
                  <Text style={styles.verseReference}>{guidance.verse_reference}</Text>
                </View>

                {/* Sanskrit Verse */}
                <View style={styles.verseContainer}>
                  <Text style={styles.verseLabel}>श्लोक (Shloka)</Text>
                  <Text style={styles.sanskritVerse}>{guidance.sanskrit_verse}</Text>
                </View>

                {/* English Translation */}
                <View style={styles.translationContainer}>
                  <Text style={styles.translationLabel}>Translation</Text>
                  <Text style={styles.englishTranslation}>
                    {guidance.english_translation}
                  </Text>
                </View>

                {/* Guidance */}
                <View style={styles.guidanceContainer}>
                  <Text style={styles.guidanceLabel}>Guidance for You</Text>
                  <Text style={styles.guidanceText}>{guidance.guidance_text}</Text>
                </View>

                {/* Action Buttons */}
                <View style={styles.actionsContainer}>
                  <TouchableOpacity
                    onPress={toggleBookmark}
                    style={[
                      styles.bookmarkButton,
                      isBookmarked && styles.bookmarkButtonActive,
                    ]}
                  >
                    <Text
                      style={[
                        styles.bookmarkButtonText,
                        isBookmarked && styles.bookmarkButtonTextActive,
                      ]}
                    >
                      {isBookmarked ? '⭐ Bookmarked' : '☆ Bookmark'}
                    </Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    onPress={() => router.push('/')}
                    style={styles.homeButton}
                  >
                    <Text style={styles.homeButtonText}>Return Home</Text>
                  </TouchableOpacity>
                </View>
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
    backgroundColor: '#FAF7F2',
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
    fontSize: 20,
    color: '#5D4E37',
    fontWeight: '600',
    textAlign: 'center',
  },
  loadingSubtext: {
    marginTop: 8,
    fontSize: 16,
    color: '#8B7355',
    fontWeight: '400',
    textAlign: 'center',
    paddingHorizontal: 24,
  },
  helpText: {
    fontSize: 15,
    color: '#6B5D4F',
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 16,
    paddingHorizontal: 32,
    lineHeight: 22,
    fontStyle: 'italic',
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
    paddingHorizontal: 24,
    paddingBottom: 16,
  },
  backButton: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 12,
    alignSelf: 'flex-start',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
    elevation: 4,
  },
  backButtonText: {
    fontSize: 18,
    color: '#8B7355',
    fontWeight: '700',
  },
  content: {
    paddingHorizontal: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 16,
    lineHeight: 36,
  },
  verseReferenceContainer: {
    backgroundColor: '#F4E4C1',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginBottom: 24,
  },
  verseReference: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8B7355',
  },
  verseContainer: {
    backgroundColor: '#FFF8E7',
    padding: 20,
    borderRadius: 12,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: '#D4AF37',
  },
  verseLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8B7355',
    marginBottom: 12,
  },
  sanskritVerse: {
    fontSize: 18,
    color: '#5D4E37',
    lineHeight: 28,
    fontWeight: '500',
  },
  translationContainer: {
    backgroundColor: '#E8F4F8',
    padding: 20,
    borderRadius: 12,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: '#6B9BD1',
  },
  translationLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#5B7C99',
    marginBottom: 12,
  },
  englishTranslation: {
    fontSize: 17,
    color: '#3D5A73',
    lineHeight: 26,
  },
  guidanceContainer: {
    backgroundColor: '#FFFFFF',
    padding: 24,
    borderRadius: 12,
    marginBottom: 32,
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  guidanceLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#8B7355',
    marginBottom: 16,
  },
  guidanceText: {
    fontSize: 18,
    color: '#5D4E37',
    lineHeight: 28,
  },
  actionsContainer: {
    gap: 16,
  },
  bookmarkButton: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#8B7355',
    alignItems: 'center',
  },
  bookmarkButtonActive: {
    backgroundColor: '#8B7355',
    borderColor: '#8B7355',
  },
  bookmarkButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#8B7355',
  },
  bookmarkButtonTextActive: {
    color: '#FFFFFF',
  },
  homeButton: {
    backgroundColor: '#6B9BD1',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
  },
  homeButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});