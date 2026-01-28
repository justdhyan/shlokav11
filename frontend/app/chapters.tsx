import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  ImageBackground,
  Animated,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Chapter {
  _id: number;
  chapter_number: number;
  name_english: string;
  name_sanskrit: string;
  description: string;
  key_teaching: string;
}

// Animated Chapter Card Component
const AnimatedChapterCard = ({ chapter, index, onPress }: { chapter: Chapter; index: number; onPress: () => void }) => {
  const [scaleAnim] = useState(new Animated.Value(1));

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.96,
      useNativeDriver: true,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      friction: 3,
      tension: 40,
      useNativeDriver: true,
    }).start();
  };

  return (
    <Animated.View style={[styles.chapterCard, { transform: [{ scale: scaleAnim }] }]}>
      <Pressable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
      >
        <View style={styles.chapterCardInner}>
          <View style={styles.chapterHeader}>
            <View style={styles.chapterBadge}>
              <Text style={styles.chapterNumber}>{chapter.chapter_number}</Text>
            </View>
            <View style={styles.chapterTitleContainer}>
              <Text style={styles.chapterTitle}>{chapter.name_english}</Text>
              <Text style={styles.chapterSanskrit}>{chapter.name_sanskrit}</Text>
            </View>
            <Text style={styles.arrow}>→</Text>
          </View>
          <Text style={styles.chapterDescription} numberOfLines={2}>
            {chapter.description}
          </Text>
        </View>
      </Pressable>
    </Animated.View>
  );
};

export default function ChaptersScreen() {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchChapters();
  }, []);

  const fetchChapters = async () => {
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
      const cached = await AsyncStorage.getItem('chapters');
      if (cached) {
        setChapters(JSON.parse(cached));
        // Don't stop loading yet - we still want to fetch fresh data
      }

      // Fetch from API
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/chapters`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();

      if (!data || data.length === 0) {
        throw new Error('No chapters data available');
      }

      setChapters(data);
      // Cache the data
      await AsyncStorage.setItem('chapters', JSON.stringify(data));
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching chapters:', error);
      setError('Unable to load chapters. Please try again.');
      setLoading(false);
      
      // If we don't have cached data, this is a real problem
      if (chapters.length === 0) {
        setError('Unable to connect to server. Please check your internet connection and try again.');
      }
    }
  };

  const handleChapterPress = (chapterNumber: number) => {
    router.push(`/chapter-detail?chapterNumber=${chapterNumber}`);
  };

  if (loading && chapters.length === 0) {
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
            <Text style={styles.loadingText}>Loading chapters...</Text>
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
                <Pressable onPress={fetchChapters} style={styles.retryButton}>
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
  if (!loading && chapters.length === 0) {
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
            <Text style={styles.emptyStateText}>📖</Text>
            <Text style={styles.emptyStateTitle}>No Chapters Available</Text>
            <Text style={styles.emptyStateMessage}>
              {error || 'Unable to load chapters. Please check your connection.'}
            </Text>
            <Pressable onPress={fetchChapters} style={styles.retryButton}>
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
                <Pressable
                  onPress={() => router.back()}
                  style={styles.backButton}
                >
                  <Text style={styles.backButtonIcon}>←</Text>
                </Pressable>
              </View>

              {/* Title Section */}
              <View style={styles.titleSection}>
                <View style={styles.titleCard}>
                  <Text style={styles.mainTitle}>Bhagavad Gita</Text>
                  <Text style={styles.subtitle}>भगवद्गीता - 18 Chapters</Text>
                </View>
                <Text style={styles.description}>
                  Explore the timeless wisdom of Lord Krishna through all 18 chapters of the Bhagavad Gita
                </Text>
              </View>

              {/* Chapters List */}
              <View style={styles.chaptersContainer}>
                {chapters.map((chapter, index) => (
                  <AnimatedChapterCard
                    key={chapter._id}
                    chapter={chapter}
                    index={index}
                    onPress={() => handleChapterPress(chapter.chapter_number)}
                  />
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
    paddingHorizontal: 20,
    paddingTop: 16,
  },
  backButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
    elevation: 4,
  },
  backButtonIcon: {
    fontSize: 24,
    color: '#8B7355',
    fontWeight: 'bold',
  },
  titleSection: {
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 16,
    alignItems: 'center',
  },
  titleCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 6,
    borderWidth: 1,
    borderColor: 'rgba(212, 175, 55, 0.2)',
  },
  mainTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#8B7355',
    fontWeight: '500',
  },
  description: {
    fontSize: 15,
    color: '#6B5D4F',
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 22,
    fontStyle: 'italic',
  },
  chaptersContainer: {
    paddingHorizontal: 20,
    paddingTop: 8,
  },
  chapterCard: {
    marginBottom: 16,
    borderRadius: 20,
    overflow: 'hidden',
  },
  chapterCardInner: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 20,
    padding: 20,
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 6,
    borderWidth: 1,
    borderColor: 'rgba(212, 175, 55, 0.15)',
  },
  chapterHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  chapterBadge: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#D4AF37',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
    shadowColor: '#D4AF37',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  chapterNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  chapterTitleContainer: {
    flex: 1,
  },
  chapterTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 4,
  },
  chapterSanskrit: {
    fontSize: 14,
    color: '#8B7355',
    fontWeight: '500',
  },
  arrow: {
    fontSize: 24,
    color: '#8B7355',
    fontWeight: 'bold',
    marginLeft: 8,
  },
  chapterDescription: {
    fontSize: 15,
    color: '#6B5D4F',
    lineHeight: 22,
  },
});
