import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  ImageBackground,
  Dimensions,
  Animated,
  Pressable,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import Reanimated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  withSequence,
  Easing,
  withDelay,
} from 'react-native-reanimated';

const { width, height } = Dimensions.get('window');
const isWeb = Platform.OS === 'web';
const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Emotion {
  _id: string;
  name_english: string;
  name_sanskrit: string;
  description: string;
  icon: string;
}

// Enhanced Floating Blur Orb Component with Slow, Calming Animations
const FloatingBlurOrb = ({ 
  size = 200, 
  delay = 0, 
  duration = 25000,
  xRange = 60,
  yRange = 80,
  color = 'rgba(212, 175, 55, 0.2)',
  initialX = 0,
  initialY = 0,
  rotate = false,
}: {
  size?: number;
  delay?: number;
  duration?: number;
  xRange?: number;
  yRange?: number;
  color?: string;
  initialX?: number;
  initialY?: number;
  rotate?: boolean;
}) => {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);
  const scale = useSharedValue(1);
  const opacity = useSharedValue(0.6);
  const rotation = useSharedValue(0);

  useEffect(() => {
    // Gentle horizontal wave movement - using sine-wave-like pattern
    translateX.value = withDelay(
      delay,
      withRepeat(
        withSequence(
          withTiming(xRange, { 
            duration: duration, 
            easing: Easing.bezier(0.45, 0.05, 0.55, 0.95) // Smooth sine-like easing
          }),
          withTiming(-xRange * 0.7, { 
            duration: duration, 
            easing: Easing.bezier(0.45, 0.05, 0.55, 0.95) 
          }),
          withTiming(0, { 
            duration: duration * 0.5, 
            easing: Easing.bezier(0.45, 0.05, 0.55, 0.95) 
          })
        ),
        -1,
        false
      )
    );

    // Gentle vertical flow - slower and more meditative
    translateY.value = withDelay(
      delay,
      withRepeat(
        withSequence(
          withTiming(yRange, { 
            duration: duration * 1.5, 
            easing: Easing.bezier(0.42, 0, 0.58, 1) // Smooth flow
          }),
          withTiming(-yRange * 0.5, { 
            duration: duration * 1.5, 
            easing: Easing.bezier(0.42, 0, 0.58, 1) 
          })
        ),
        -1,
        true
      )
    );

    // Subtle breathing/pulsing effect - very gentle
    scale.value = withDelay(
      delay,
      withRepeat(
        withSequence(
          withTiming(1.12, { 
            duration: duration * 1.2, 
            easing: Easing.bezier(0.37, 0, 0.63, 1) // Smooth breathing
          }),
          withTiming(0.95, { 
            duration: duration * 1.2, 
            easing: Easing.bezier(0.37, 0, 0.63, 1) 
          })
        ),
        -1,
        true
      )
    );

    // Gentle opacity fade for ethereal effect
    opacity.value = withDelay(
      delay,
      withRepeat(
        withSequence(
          withTiming(0.7, { 
            duration: duration * 0.9, 
            easing: Easing.bezier(0.4, 0, 0.6, 1) 
          }),
          withTiming(0.5, { 
            duration: duration * 0.9, 
            easing: Easing.bezier(0.4, 0, 0.6, 1) 
          })
        ),
        -1,
        true
      )
    );

    // Optional slow rotation for organic, flowing feel
    if (rotate) {
      rotation.value = withDelay(
        delay,
        withRepeat(
          withTiming(360, { 
            duration: duration * 3, 
            easing: Easing.linear 
          }),
          -1,
          false
        )
      );
    }
  }, [delay, duration, xRange, yRange, rotate]);

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [
        { translateX: translateX.value },
        { translateY: translateY.value },
        { scale: scale.value },
        ...(rotate ? [{ rotate: `${rotation.value}deg` }] : []),
      ],
      opacity: opacity.value,
    };
  });

  // For web, use a CSS-based blur approach with enhanced visibility
  if (isWeb) {
    return (
      <Reanimated.View
        style={[
          {
            position: 'absolute',
            left: initialX,
            top: initialY,
            width: size,
            height: size,
            borderRadius: size / 2,
            backgroundColor: color,
            // @ts-ignore - web-specific properties
            filter: 'blur(60px)',
            mixBlendMode: 'normal',
            pointerEvents: 'none',
          },
          animatedStyle,
        ]}
      />
    );
  }

  // For native, use BlurView with enhanced blur
  return (
    <Reanimated.View
      style={[
        {
          position: 'absolute',
          left: initialX,
          top: initialY,
          width: size,
          height: size,
          borderRadius: size / 2,
          backgroundColor: color,
          overflow: 'hidden',
        },
        animatedStyle,
      ]}
    >
      <BlurView intensity={50} tint="light" style={{ flex: 1, borderRadius: size / 2 }} />
    </Reanimated.View>
  );
};

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
  const [scaleAnim] = useState(new Animated.Value(1));

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
  joy: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800',
  doubt: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800',
  pride: 'https://images.unsplash.com/photo-1519834785169-98be25ec3f84?w=800',
  desire: 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800',
  envy: 'https://images.unsplash.com/photo-1516414447565-b14be0adf13e?w=800',
  despair: 'https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=800',
};

export default function HomeScreen() {
  const [emotions, setEmotions] = useState<Emotion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchEmotions();
  }, []);

  const fetchEmotions = async () => {
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
      const cached = await AsyncStorage.getItem('emotions');
      if (cached) {
        setEmotions(JSON.parse(cached));
        // Don't stop loading yet - we still want to fetch fresh data
      }

      // Fetch from API
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/emotions`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data || data.length === 0) {
        throw new Error('No emotions data available');
      }
      
      setEmotions(data);
      // Cache the data
      await AsyncStorage.setItem('emotions', JSON.stringify(data));
      setLoading(false);
      setError(null);
    } catch (error) {
      console.error('Error fetching emotions:', error);
      setError('Unable to load emotions. Please try again.');
      setLoading(false);
      
      // If we don't have cached data, this is a real problem
      if (emotions.length === 0) {
        setError('Unable to connect to server. Please check your internet connection and try again.');
      }
    }
  };

  const handleEmotionPress = (emotionId: string) => {
    router.push(`/moods?emotionId=${emotionId}`);
  };

  if (loading && emotions.length === 0) {
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
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
                <Pressable onPress={fetchEmotions} style={styles.retryButton}>
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
  if (!loading && emotions.length === 0) {
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
            <Text style={styles.emptyStateText}>😔</Text>
            <Text style={styles.emptyStateTitle}>No Content Available</Text>
            <Text style={styles.emptyStateMessage}>
              {error || 'Unable to load emotions. Please check your connection.'}
            </Text>
            <Pressable onPress={fetchEmotions} style={styles.retryButton}>
              <Text style={styles.retryButtonText}>Try Again</Text>
            </Pressable>
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
        {/* Slow Flowing Blur Animations - Calm & Meditative */}
        <View style={styles.blurOrbsContainer}>
          {/* Large golden orb - top left, slow and graceful */}
          <FloatingBlurOrb
            size={280}
            delay={0}
            duration={28000}
            xRange={40}
            yRange={70}
            color="rgba(212, 175, 55, 0.45)"
            initialX={-100}
            initialY={80}
            rotate={true}
          />
          
          {/* Warm brown orb - top right, gentle flow */}
          <FloatingBlurOrb
            size={200}
            delay={3000}
            duration={32000}
            xRange={50}
            yRange={60}
            color="rgba(139, 115, 85, 0.40)"
            initialX={width - 80}
            initialY={150}
            rotate={false}
          />
          
          {/* Soft beige orb - center, very slow breathing */}
          <FloatingBlurOrb
            size={240}
            delay={6000}
            duration={35000}
            xRange={35}
            yRange={80}
            color="rgba(244, 228, 193, 0.50)"
            initialX={width / 2 - 120}
            initialY={height * 0.4}
            rotate={true}
          />
          
          {/* Small golden orb - lower left, delicate movement */}
          <FloatingBlurOrb
            size={170}
            delay={9000}
            duration={30000}
            xRange={45}
            yRange={55}
            color="rgba(212, 175, 55, 0.42)"
            initialX={width * 0.15}
            initialY={height - 350}
            rotate={false}
          />
          
          {/* Medium brown orb - lower right, calm drift */}
          <FloatingBlurOrb
            size={210}
            delay={12000}
            duration={26000}
            xRange={40}
            yRange={65}
            color="rgba(139, 115, 85, 0.38)"
            initialX={width - 130}
            initialY={height - 420}
            rotate={true}
          />
          
          {/* Soft saffron orb - mid left, spiritual glow */}
          <FloatingBlurOrb
            size={190}
            delay={4000}
            duration={29000}
            xRange={38}
            yRange={58}
            color="rgba(255, 140, 0, 0.35)"
            initialX={-60}
            initialY={height * 0.5}
            rotate={false}
          />
          
          {/* Light cream orb - mid right, ethereal presence */}
          <FloatingBlurOrb
            size={220}
            delay={8000}
            duration={33000}
            xRange={42}
            yRange={72}
            color="rgba(250, 247, 242, 0.48)"
            initialX={width - 110}
            initialY={height * 0.6}
            rotate={true}
          />
        </View>

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
  blurOrbsContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 0,
  },
  gradient: {
    flex: 1,
    zIndex: 1,
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
    boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.2)',
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
    textShadow: '0px 2px 4px rgba(0, 0, 0, 0.3)',
  },
  appNameSanskrit: {
    fontSize: 28,
    color: '#FFFFFF',
    marginTop: 8,
    textShadow: '0px 1px 3px rgba(0, 0, 0, 0.3)',
  },
  tagline: {
    fontSize: 16,
    color: '#F4E4C1',
    marginTop: 12,
    fontStyle: 'italic',
    textShadow: '0px 1px 2px rgba(0, 0, 0, 0.3)',
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
    boxShadow: '0px 4px 12px rgba(139, 115, 85, 0.2)',
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
    boxShadow: '0px 6px 16px rgba(139, 115, 85, 0.3)',
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
