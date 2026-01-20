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
  Dimensions,
  Animated,
  Pressable,
} from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

const { width, height } = Dimensions.get('window');
const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Emotion {
  _id: string;
  name_english: string;
  name_sanskrit: string;
  description: string;
  icon: string;
}

// Animated Card Component
const AnimatedEmotionCard = ({ emotion, index, onPress }: { emotion: Emotion; index: number; onPress: () => void }) => {
  const [scaleAnim] = useState(new Animated.Value(1));
  const [fadeAnim] = useState(new Animated.Value(1)); // Start at 1 for immediate visibility

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.95,
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
    <Animated.View style={[styles.emotionCardWrapper, { transform: [{ scale: scaleAnim }] }]}>
      <Pressable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
      >
        <ImageBackground
          source={{ uri: emotionImages[emotion._id as keyof typeof emotionImages] }}
          style={styles.emotionCardBackground}
          imageStyle={styles.emotionCardImage}
        >
          <LinearGradient
            colors={['rgba(255, 255, 255, 0.88)', 'rgba(255, 255, 255, 0.96)']}
            style={styles.emotionCardGradient}
          >
            <View style={styles.emotionContent}>
              <View style={styles.emotionHeader}>
                <View style={styles.emotionIconContainer}>
                  <Text style={styles.emotionIndex}>{index + 1}</Text>
                </View>
                <View style={styles.emotionTextContainer}>
                  <Text style={styles.emotionName}>{emotion.name_english}</Text>
                  <Text style={styles.emotionSanskrit}>{emotion.name_sanskrit}</Text>
                </View>
              </View>
              <Text style={styles.emotionDescription}>{emotion.description}</Text>
              <View style={styles.emotionArrow}>
                <Text style={styles.arrowText}>→</Text>
              </View>
            </View>
          </LinearGradient>
        </ImageBackground>
      </Pressable>
    </Animated.View>
  );
};

// Animated Button Component
const AnimatedButton = ({ onPress, icon, text, style }: { onPress: () => void; icon: string; text: string; style: any }) => {
  const scaleAnim = new Animated.Value(1);

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.92,
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
    <Animated.View style={{ flex: 1, transform: [{ scale: scaleAnim }] }}>
      <Pressable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        style={[styles.actionButton, style]}
      >
        <Text style={styles.buttonIcon}>{icon}</Text>
        <Text style={styles.buttonText}>{text}</Text>
      </Pressable>
    </Animated.View>
  );
};

// Emotion-specific imagery
const emotionImages = {
  fear: 'https://images.unsplash.com/photo-1596723328596-b929cef665a9?w=800',
  anger: 'https://images.unsplash.com/photo-1712917699335-51dd4318eac5?w=800',
  grief: 'https://images.unsplash.com/photo-1591757311543-5fa5af831901?w=800',
  confusion: 'https://images.unsplash.com/photo-1718179401998-ffc309805882?w=800',
  detachment: 'https://images.unsplash.com/photo-1706005528007-8f660674a83f?w=800',
};

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
        <ImageBackground
          source={{ uri: 'https://images.unsplash.com/photo-1707249935951-d92bf3a65b00?w=800' }}
          style={styles.loadingBackground}
          blurRadius={3}
        >
          <LinearGradient
            colors={['rgba(250, 247, 242, 0.9)', 'rgba(244, 228, 193, 0.95)']}
            style={styles.loadingGradient}
          >
            <ActivityIndicator size="large" color="#8B7355" />
            <Text style={styles.loadingText}>Loading wisdom...</Text>
          </LinearGradient>
        </ImageBackground>
      </SafeAreaView>
    );
  }

  return (
    <View style={styles.container}>
      <ImageBackground
        source={{ uri: 'https://images.unsplash.com/photo-1660933195480-16e7eab330bb?w=1200' }}
        style={styles.heroBackground}
        resizeMode="cover"
      >
        <LinearGradient
          colors={['rgba(139, 115, 85, 0.7)', 'rgba(250, 247, 242, 0.95)', 'rgba(250, 247, 242, 1)']}
          locations={[0, 0.4, 0.7]}
          style={styles.gradient}
        >
          <SafeAreaView style={styles.safeArea}>
            <ScrollView 
              contentContainerStyle={styles.scrollContent}
              showsVerticalScrollIndicator={false}
            >
              {/* Hero Section */}
              <View style={styles.heroSection}>
                <View style={styles.heroContent}>
                  <Text style={styles.appName}>SHLOKA</Text>
                  <Text style={styles.appNameSanskrit}>श्लोक</Text>
                  <Text style={styles.tagline}>Wisdom from the Bhagavad Gita</Text>
                </View>
              </View>

              {/* Main Question with Lotus Decoration */}
              <View style={styles.questionSection}>
                <View style={styles.questionCard}>
                  <View style={styles.decorativeLine} />
                  <Text style={styles.question}>What is troubling you today?</Text>
                  <Text style={styles.subQuestion}>आज आपको क्या परेशान कर रहा है?</Text>
                  <View style={styles.decorativeLine} />
                </View>
                <Text style={styles.instructionText}>
                  Select an emotion to receive guidance from Lord Krishna
                </Text>
              </View>

              {/* Emotions Grid with Images */}
              <View style={styles.emotionsContainer}>
                {emotions.map((emotion, index) => (
                  <AnimatedEmotionCard
                    key={emotion._id}
                    emotion={emotion}
                    index={index}
                    onPress={() => handleEmotionPress(emotion._id)}
                  />
                ))}
              </View>

              {/* Footer with Divine Quote */}
              <View style={styles.footer}>
                <View style={styles.quoteContainer}>
                  <Text style={styles.quoteText}>
                    "योगस्थः कुरु कर्माणि"
                  </Text>
                  <Text style={styles.quoteTranslation}>
                    "Perform your duty with a steady mind" - Bhagavad Gita 2.48
                  </Text>
                </View>
                
                <View style={styles.buttonRow}>
                  <AnimatedButton
                    onPress={() => router.push('/chapters')}
                    icon="📖"
                    text="Chapter wise"
                    style={styles.chaptersButton}
                  />
                  <AnimatedButton
                    onPress={() => router.push('/bookmarks')}
                    icon="⭐"
                    text="Saved Guidance"
                    style={styles.bookmarksButton}
                  />
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
  heroBackground: {
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
  heroSection: {
    paddingTop: 40,
    paddingBottom: 20,
    alignItems: 'center',
  },
  heroContent: {
    alignItems: 'center',
  },
  appName: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#FFFFFF',
    letterSpacing: 4,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  appNameSanskrit: {
    fontSize: 28,
    color: '#FFFFFF',
    marginTop: 8,
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  tagline: {
    fontSize: 16,
    color: '#F4E4C1',
    marginTop: 12,
    fontStyle: 'italic',
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  questionSection: {
    paddingHorizontal: 20,
    paddingVertical: 32,
    alignItems: 'center',
  },
  questionCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
    borderWidth: 1,
    borderColor: 'rgba(212, 175, 55, 0.3)',
  },
  decorativeLine: {
    width: 60,
    height: 3,
    backgroundColor: '#D4AF37',
    borderRadius: 2,
    marginVertical: 12,
  },
  question: {
    fontSize: 26,
    fontWeight: '700',
    color: '#5D4E37',
    textAlign: 'center',
    lineHeight: 34,
  },
  subQuestion: {
    fontSize: 19,
    color: '#8B7355',
    marginTop: 8,
    textAlign: 'center',
    fontWeight: '500',
  },
  instructionText: {
    fontSize: 15,
    color: '#8B7355',
    marginTop: 20,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  emotionsContainer: {
    paddingHorizontal: 16,
  },
  emotionCardWrapper: {
    marginBottom: 20,
    marginHorizontal: 8,
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 10,
  },
  emotionCardBackground: {
    width: '100%',
    minHeight: 170,
  },
  emotionCardImage: {
    borderRadius: 24,
  },
  emotionCardGradient: {
    flex: 1,
    padding: 24,
    borderRadius: 24,
  },
  emotionContent: {
    flex: 1,
    justifyContent: 'space-between',
  },
  emotionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  emotionIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#D4AF37',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  emotionIndex: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  emotionTextContainer: {
    flex: 1,
  },
  emotionName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 2,
  },
  emotionSanskrit: {
    fontSize: 16,
    color: '#8B7355',
    fontWeight: '500',
  },
  emotionDescription: {
    fontSize: 16,
    color: '#6B5D4F',
    lineHeight: 24,
    marginBottom: 8,
  },
  emotionArrow: {
    alignSelf: 'flex-end',
  },
  arrowText: {
    fontSize: 32,
    color: '#8B7355',
    fontWeight: 'bold',
  },
  footer: {
    paddingHorizontal: 24,
    paddingTop: 32,
    alignItems: 'center',
  },
  quoteContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    borderLeftWidth: 4,
    borderLeftColor: '#D4AF37',
    shadowColor: '#8B7355',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  quoteText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#5D4E37',
    textAlign: 'center',
    marginBottom: 8,
  },
  quoteTranslation: {
    fontSize: 14,
    color: '#8B7355',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
    width: '100%',
  },
  actionButton: {
    flex: 1,
    paddingVertical: 18,
    paddingHorizontal: 16,
    borderRadius: 16,
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
    minHeight: 90,
  },
  chaptersButton: {
    backgroundColor: '#8B7355',
  },
  bookmarksButton: {
    backgroundColor: '#6B9BD1',
  },
  buttonIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
    textAlign: 'center',
  },
});
