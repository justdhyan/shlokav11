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
} from 'react-native';
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

export default function ChaptersScreen() {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchChapters();
  }, []);

  const fetchChapters = async () => {
    try {
      // Try to get from cache first
      const cached = await AsyncStorage.getItem('chapters');
      if (cached) {
        setChapters(JSON.parse(cached));
        setLoading(false);
      }

      // Fetch from API
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/chapters`);
      const data = await response.json();

      setChapters(data);
      // Cache the data
      await AsyncStorage.setItem('chapters', JSON.stringify(data));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching chapters:', error);
      setLoading(false);
    }
  };

  const handleChapterPress = (chapterNumber: number) => {
    router.push(`/chapter-detail?chapterNumber=${chapterNumber}`);
  };

  if (loading) {
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
                  <Text style={styles.title}>Bhagavad Gita</Text>
                  <Text style={styles.subtitle}>भगवद्गीता - 18 Chapters</Text>
                </View>
              </View>

              {/* Description */}
              <View style={styles.descriptionContainer}>
                <Text style={styles.descriptionText}>
                  Explore the timeless wisdom of Lord Krishna through all 18 chapters of the Bhagavad Gita
                </Text>
              </View>

              {/* Chapters List */}
              <View style={styles.chaptersContainer}>
                {chapters.map((chapter) => (
                  <TouchableOpacity
                    key={chapter._id}
                    style={styles.chapterCard}
                    onPress={() => handleChapterPress(chapter.chapter_number)}
                    activeOpacity={0.8}
                  >
                    <LinearGradient
                      colors={['#FFFFFF', '#FEFCF8']}
                      style={styles.chapterCardGradient}
                    >
                      <View style={styles.chapterNumber}>
                        <Text style={styles.chapterNumberText}>{chapter.chapter_number}</Text>
                      </View>
                      <View style={styles.chapterContent}>
                        <Text style={styles.chapterName}>{chapter.name_english}</Text>
                        <Text style={styles.chapterSanskrit}>{chapter.name_sanskrit}</Text>
                        <Text style={styles.chapterDescription} numberOfLines={2}>
                          {chapter.description}
                        </Text>
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
  header: {
    paddingTop: 24,
    paddingBottom: 24,
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
  descriptionContainer: {
    paddingHorizontal: 32,
    paddingVertical: 20,
  },
  descriptionText: {
    fontSize: 16,
    color: '#6B5D4F',
    textAlign: 'center',
    lineHeight: 24,
    fontStyle: 'italic',
  },
  chaptersContainer: {
    paddingHorizontal: 16,
    paddingTop: 8,
  },
  chapterCard: {
    marginBottom: 16,
    marginHorizontal: 8,
    borderRadius: 18,
    overflow: 'hidden',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 6,
  },
  chapterCardGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 18,
    minHeight: 120,
  },
  chapterNumber: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#D4AF37',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  chapterNumberText: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  chapterContent: {
    flex: 1,
    paddingRight: 12,
  },
  chapterName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 4,
  },
  chapterSanskrit: {
    fontSize: 15,
    color: '#8B7355',
    marginBottom: 8,
    fontWeight: '500',
  },
  chapterDescription: {
    fontSize: 14,
    color: '#6B5D4F',
    lineHeight: 20,
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
