import { Stack } from 'expo-router';
import { useEffect } from 'react';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Keep the splash screen visible while we fetch resources
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    // Add custom fonts here if needed
  });

  useEffect(() => {
    if (loaded || error) {
      SplashScreen.hideAsync();
    }
  }, [loaded, error]);

  if (!loaded && !error) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <Stack
        screenOptions={{
          headerShown: false,
          animation: 'fade_from_bottom',
          animationDuration: 300,
          contentStyle: { backgroundColor: '#FAF7F2' },
        }}
      >
        <Stack.Screen 
          name="index" 
          options={{
            animation: 'fade',
          }}
        />
        <Stack.Screen 
          name="moods" 
          options={{
            animation: 'slide_from_right',
          }}
        />
        <Stack.Screen 
          name="guidance" 
          options={{
            animation: 'slide_from_right',
          }}
        />
        <Stack.Screen 
          name="bookmarks" 
          options={{
            animation: 'slide_from_bottom',
          }}
        />
        <Stack.Screen 
          name="chapters" 
          options={{
            animation: 'slide_from_bottom',
          }}
        />
        <Stack.Screen 
          name="chapter-detail" 
          options={{
            animation: 'slide_from_right',
          }}
        />
      </Stack>
    </SafeAreaProvider>
  );
}
