import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  ImageBackground,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Verse {
  verse_number: string;
  sanskrit: string;
  english: string;
}

interface Chapter {
  _id: number;
  chapter_number: number;
  name_english: string;
  name_sanskrit: string;
  description: string;
  key_teaching: string;
  verses: Verse[];
}

export default function ChapterDetailScreen() {
  const [chapter, setChapter] = useState<Chapter | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { chapterNumber } = useLocalSearchParams();

  useEffect(() => {
    if (chapterNumber) {
      fetchChapter();
    }
  }, [chapterNumber]);

  const fetchChapter = async () => {
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
      const cacheKey = `chapter_${chapterNumber}`;
      const cached = await AsyncStorage.getItem(cacheKey);
      if (cached) {
        setChapter(JSON.parse(cached));
        // Don't stop loading yet - we still want to fetch fresh data
      }

      // Fetch from API
      const response = await fetch(
        `${EXPO_PUBLIC_BACKEND_URL}/api/chapters/${chapterNumber}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();

      if (!data) {
        throw new Error('Chapter not found');
      }

      setChapter(data);
      // Cache the data
      await AsyncStorage.setItem(cacheKey, JSON.stringify(data));
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching chapter:', error);
      setError('Unable to load chapter. Please try again.');
      setLoading(false);
      
      // If we don't have cached data, this is a real problem
      if (!chapter) {
        setError('Unable to connect to server. Please check your internet connection and try again.');
      }
    }
  };

  if (loading && !chapter) {
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
            <ActivityIndicator size="large" color="#8B7355" />
            <Text style={styles.loadingText}>Loading chapter...</Text>
            {error && (
              <View style={styles.errorInlineContainer}>
                <Text style={styles.errorInlineText}>{error}</Text>
                <Pressable onPress={fetchChapter} style={styles.retryButton}>
                  <Text style={styles.retryButtonText}>Retry</Text>
                </Pressable>
              </View>
            )}
          </LinearGradient>
        </ImageBackground>
      </SafeAreaView>
    );
  }

  if (!chapter) {
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
            <Text style={styles.emptyStateText}>📖</Text>
            <Text style={styles.emptyStateTitle}>Chapter Not Found</Text>
            <Text style={styles.emptyStateMessage}>
              {error || 'Unable to find this chapter.'}
            </Text>
            <Pressable onPress={fetchChapter} style={styles.retryButton}>
              <Text style={styles.retryButtonText}>Try Again</Text>
            </Pressable>
            <Pressable
              onPress={() => router.back()}
              style={[styles.retryButton, { marginTop: 12, backgroundColor: '#6B9BD1' }]}
            >
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
              </View>

              {/* Content */}
              <View style={styles.content}>
                {/* Chapter Number Badge */}
                <View style={styles.chapterBadge}>
                  <Text style={styles.chapterBadgeText}>Chapter {chapter.chapter_number}</Text>
                </View>

                {/* Title */}
                <Text style={styles.title}>{chapter.name_english}</Text>
                <Text style={styles.titleSanskrit}>{chapter.name_sanskrit}</Text>

                {/* Description */}
                <View style={styles.descriptionContainer}>
                  <Text style={styles.descriptionLabel}>About This Chapter</Text>
                  <Text style={styles.descriptionText}>{chapter.description}</Text>
                </View>

                {/* Key Teaching */}
                <View style={styles.teachingContainer}>
                  <Text style={styles.teachingLabel}>Key Teaching</Text>
                  <Text style={styles.teachingText}>{chapter.key_teaching}</Text>
                </View>

                {/* Verses */}
                {chapter.verses && chapter.verses.length > 0 && (
                  <View style={styles.versesSection}>
                    <Text style={styles.versesSectionTitle}>Sample Verses</Text>
                    {chapter.verses.map((verse, index) => (
                      <View key={index} style={styles.verseContainer}>
                        <View style={styles.verseNumberBadge}>
                          <Text style={styles.verseNumberText}>
                            Verse {verse.verse_number}
                          </Text>
                        </View>

                        <View style={styles.verseContent}>
                          <Text style={styles.verseLabel}>Sanskrit</Text>
                          <Text style={styles.sanskritVerse}>{verse.sanskrit}</Text>
                        </View>

                        <View style={styles.translationContent}>
                          <Text style={styles.translationLabel}>Translation</Text>
                          <Text style={styles.englishTranslation}>{verse.english}</Text>
                        </View>
                      </View>
                    ))}
                  </View>
                )}

                {/* Action Buttons */}
                <View style={styles.actionsContainer}>
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
  errorInlineContainer: {
    marginTop: 24,
    padding: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 12,
    marginHorizontal: 24,
    alignItems: 'center',
  },
  errorInlineText: {
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  errorText: {
    fontSize: 20,
    color: '#8B7355',
    marginBottom: 24,
  },
  errorButton: {
    backgroundColor: '#8B7355',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  errorButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
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
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  backButtonText: {
    fontSize: 18,
    color: '#8B7355',
    fontWeight: '700',
  },
  content: {
    paddingHorizontal: 24,
  },
  chapterBadge: {
    backgroundColor: '#D4AF37',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    alignSelf: 'flex-start',
    marginBottom: 16,
  },
  chapterBadgeText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 8,
    lineHeight: 36,
  },
  titleSanskrit: {
    fontSize: 20,
    color: '#8B7355',
    marginBottom: 24,
    fontWeight: '500',
  },
  descriptionContainer: {
    backgroundColor: '#FFF8E7',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#D4AF37',
  },
  descriptionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#8B7355',
    marginBottom: 12,
  },
  descriptionText: {
    fontSize: 17,
    color: '#5D4E37',
    lineHeight: 26,
  },
  teachingContainer: {
    backgroundColor: '#E8F4F8',
    padding: 20,
    borderRadius: 12,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: '#6B9BD1',
  },
  teachingLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#5B7C99',
    marginBottom: 12,
  },
  teachingText: {
    fontSize: 17,
    color: '#3D5A73',
    lineHeight: 26,
    fontWeight: '500',
  },
  versesSection: {
    marginBottom: 24,
  },
  versesSectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 16,
  },
  verseContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  verseNumberBadge: {
    backgroundColor: '#F4E4C1',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginBottom: 16,
  },
  verseNumberText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#8B7355',
  },
  verseContent: {
    marginBottom: 16,
  },
  verseLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#8B7355',
    marginBottom: 8,
  },
  sanskritVerse: {
    fontSize: 18,
    color: '#5D4E37',
    lineHeight: 28,
    fontWeight: '500',
  },
  translationContent: {
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E8E8E8',
  },
  translationLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#5B7C99',
    marginBottom: 8,
  },
  englishTranslation: {
    fontSize: 17,
    color: '#3D5A73',
    lineHeight: 26,
  },
  actionsContainer: {
    marginTop: 8,
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
