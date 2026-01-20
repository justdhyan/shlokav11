import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
} from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface Guidance {
  _id: string;
  mood_id: string;
  title: string;
  verse_reference: string;
  sanskrit_verse: string;
  english_translation: string;
  guidance_text: string;
}

export default function BookmarksScreen() {
  const [bookmarks, setBookmarks] = useState<Guidance[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Refresh bookmarks when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      loadBookmarks();
    }, [])
  );

  const loadBookmarks = async () => {
    try {
      setLoading(true);
      const bookmarksData = await AsyncStorage.getItem('bookmarks');
      if (bookmarksData) {
        setBookmarks(JSON.parse(bookmarksData));
      } else {
        setBookmarks([]);
      }
    } catch (error) {
      console.error('Error loading bookmarks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBookmarkPress = (moodId: string) => {
    router.push(`/guidance?moodId=${moodId}`);
  };

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
          <Text style={styles.title}>Your Bookmarks</Text>
          <Text style={styles.subtitle}>आपके बुकमार्क</Text>
        </View>

        {/* Bookmarks List */}
        <View style={styles.bookmarksContainer}>
          {bookmarks.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>No bookmarks yet</Text>
              <Text style={styles.emptySubtext}>
                Save guidance that resonates with you
              </Text>
              <TouchableOpacity
                onPress={() => router.push('/')}
                style={styles.exploreButton}
              >
                <Text style={styles.exploreButtonText}>Explore Guidance</Text>
              </TouchableOpacity>
            </View>
          ) : (
            bookmarks.map((bookmark) => (
              <TouchableOpacity
                key={bookmark._id}
                style={styles.bookmarkCard}
                onPress={() => handleBookmarkPress(bookmark.mood_id)}
                activeOpacity={0.7}
              >
                <View style={styles.bookmarkContent}>
                  <Text style={styles.bookmarkTitle}>{bookmark.title}</Text>
                  <View style={styles.verseReferenceContainer}>
                    <Text style={styles.verseReference}>
                      {bookmark.verse_reference}
                    </Text>
                  </View>
                  <Text style={styles.bookmarkPreview} numberOfLines={2}>
                    {bookmark.guidance_text}
                  </Text>
                </View>
                <Text style={styles.arrow}>→</Text>
              </TouchableOpacity>
            ))
          )}
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
  bookmarksContainer: {
    paddingHorizontal: 16,
    paddingTop: 24,
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 80,
    paddingHorizontal: 32,
  },
  emptyText: {
    fontSize: 24,
    fontWeight: '600',
    color: '#8B7355',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 16,
    color: '#A0826D',
    textAlign: 'center',
    marginBottom: 32,
  },
  exploreButton: {
    backgroundColor: '#6B9BD1',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
  },
  exploreButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  bookmarkCard: {
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
  },
  bookmarkContent: {
    flex: 1,
    paddingRight: 16,
  },
  bookmarkTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#5D4E37',
    marginBottom: 12,
  },
  verseReferenceContainer: {
    backgroundColor: '#F4E4C1',
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 6,
    alignSelf: 'flex-start',
    marginBottom: 12,
  },
  verseReference: {
    fontSize: 12,
    fontWeight: '600',
    color: '#8B7355',
  },
  bookmarkPreview: {
    fontSize: 15,
    color: '#6B5D4F',
    lineHeight: 22,
  },
  arrow: {
    fontSize: 28,
    color: '#8B7355',
    fontWeight: 'bold',
  },
});
