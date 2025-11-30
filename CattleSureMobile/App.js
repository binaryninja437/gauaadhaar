import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Image, ActivityIndicator, Alert, SafeAreaView, TextInput, KeyboardAvoidingView, Platform } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as Location from 'expo-location';
import axios from 'axios';

// API Configuration
// REPLACE WITH YOUR COMPUTER'S LOCAL IP ADDRESS
const API_URL = 'http://192.168.1.103:8000';

export default function App() {
  const [view, setView] = useState('HOME'); // HOME, REGISTER, IDENTIFY, RESULT
  const [permission, requestPermission] = useCameraPermissions();
  const [locationPermission, requestLocationPermission] = Location.useForegroundPermissions();
  const [cameraRef, setCameraRef] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [mode, setMode] = useState(null); // 'REGISTER' or 'IDENTIFY'
  const [cowName, setCowName] = useState('');

  useEffect(() => {
    (async () => {
      if (!permission?.granted) await requestPermission();
      if (!locationPermission?.granted) await requestLocationPermission();
    })();
  }, []);

  if (!permission || !locationPermission) {
    return <View style={styles.container}><Text>Requesting permissions...</Text></View>;
  }

  if (!permission.granted || !locationPermission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>We need Camera and Location permissions to proceed.</Text>
        <TouchableOpacity style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Grant Permissions</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const takePicture = async () => {
    if (cameraRef) {
      try {
        setLoading(true);
        const photo = await cameraRef.takePictureAsync({ quality: 0.7 });

        // Get Location
        const location = await Location.getCurrentPositionAsync({});
        const { latitude, longitude } = location.coords;

        await processImage(photo, latitude, longitude);
      } catch (error) {
        Alert.alert("Error", "Failed to capture photo or location.");
        setLoading(false);
      }
    }
  };

  const processImage = async (photo, lat, lon) => {
    const formData = new FormData();
    formData.append('file', {
      uri: photo.uri,
      type: 'image/jpeg',
      name: 'photo.jpg',
    });

    try {
      let endpoint = '';
      if (mode === 'REGISTER') {
        endpoint = '/register';
        formData.append('cow_name', cowName || `Bessie_${Math.floor(Math.random() * 1000)}`);
        formData.append('latitude', String(lat));
        formData.append('longitude', String(lon));
      } else {
        endpoint = '/identify';
        formData.append('current_lat', String(lat));
        formData.append('current_lon', String(lon));
      }

      console.log(`Sending to ${API_URL}${endpoint}...`);
      const response = await axios.post(`${API_URL}${endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setResultData(response.data);
      setView('RESULT');
    } catch (error) {
      console.error(error);
      Alert.alert("API Error", "Failed to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  // --- VIEWS ---

  const renderHome = () => (
    <View style={styles.homeContainer}>
      <Text style={styles.title}>🐮 CattleSure</Text>
      <Text style={styles.subtitle}>Field Agent App</Text>

      <TouchableOpacity
        style={[styles.bigButton, { backgroundColor: '#2E7D32' }]}
        onPress={() => { setMode('REGISTER'); setView('ENTER_NAME'); setCowName(''); }}
      >
        <Text style={styles.bigButtonText}>📝 Register New Cow</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.bigButton, { backgroundColor: '#1565C0' }]}
        onPress={() => { setMode('IDENTIFY'); setView('CAMERA'); }}
      >
        <Text style={styles.bigButtonText}>🔍 Identify Cow</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>Connected to: {API_URL}</Text>
    </View>
  );

  const renderEnterName = () => (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={styles.homeContainer}
    >
      <Text style={styles.title}>📝 Cow Name</Text>
      <Text style={styles.subtitle}>Enter a name for this cow</Text>

      <TextInput
        style={styles.input}
        placeholder="e.g. Daisy"
        value={cowName}
        onChangeText={setCowName}
        autoFocus={true}
      />

      <TouchableOpacity
        style={[styles.bigButton, { backgroundColor: '#2E7D32', marginTop: 20 }]}
        onPress={() => {
          if (!cowName.trim()) {
            Alert.alert("Required", "Please enter a name.");
            return;
          }
          setView('CAMERA');
        }}
      >
        <Text style={styles.bigButtonText}>Next: Take Photo 📸</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.cancelButton} onPress={() => setView('HOME')}>
        <Text style={styles.cancelButtonText}>Cancel</Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );

  const renderCamera = () => (
    <View style={styles.cameraContainer}>
      <CameraView style={styles.camera} ref={(ref) => setCameraRef(ref)}>
        <View style={styles.cameraOverlay}>
          <Text style={styles.overlayText}>
            {mode === 'REGISTER' ? "Capture Muzzle to Register" : "Capture Muzzle to Identify"}
          </Text>
          <TouchableOpacity style={styles.closeButton} onPress={() => setView('HOME')}>
            <Text style={styles.closeButtonText}>✕</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.controls}>
          {loading ? (
            <ActivityIndicator size="large" color="#fff" />
          ) : (
            <TouchableOpacity style={styles.shutterButton} onPress={takePicture} />
          )}
        </View>
      </CameraView>
    </View>
  );

  const renderResult = () => {
    if (!resultData) return null;

    let bgColor = '#fff';
    let statusText = '';
    let icon = '';

    if (mode === 'REGISTER') {
      bgColor = '#C8E6C9'; // Green
      statusText = 'REGISTRATION SUCCESSFUL';
      icon = '✅';
    } else {
      // Identify Mode
      const status = resultData.status;
      if (status === 'APPROVED') {
        bgColor = '#C8E6C9'; // Green
        statusText = 'MATCH APPROVED';
        icon = '✅';
      } else if (status === 'MANUAL_REVIEW') {
        bgColor = '#FFF9C4'; // Yellow
        statusText = 'MANUAL REVIEW';
        icon = '⚠️';
      } else if (status === 'LOCATION_MISMATCH') {
        bgColor = '#FFCDD2'; // Red
        statusText = 'LOCATION MISMATCH';
        icon = '❌';
      } else {
        bgColor = '#FFCDD2'; // Red
        statusText = 'REJECTED';
        icon = '❌';
      }
    }

    return (
      <View style={[styles.resultContainer, { backgroundColor: bgColor }]}>
        <Text style={styles.resultIcon}>{icon}</Text>
        <Text style={styles.resultTitle}>{statusText}</Text>

        <View style={styles.card}>
          {mode === 'REGISTER' ? (
            <>
              <Text style={styles.label}>Cow Name:</Text>
              <Text style={styles.value}>{resultData.cow_name}</Text>
              <Text style={styles.label}>Cow ID:</Text>
              <Text style={styles.value}>{resultData.cow_id}</Text>
            </>
          ) : (
            <>
              <Text style={styles.label}>Identified As:</Text>
              <Text style={styles.value}>{resultData.cow_name || "Unknown"}</Text>

              <Text style={styles.label}>Confidence:</Text>
              <Text style={styles.value}>{resultData.confidence ? resultData.confidence.toFixed(2) + '%' : 'N/A'}</Text>

              <Text style={styles.label}>Distance:</Text>
              <Text style={styles.value}>{resultData.distance_km ? resultData.distance_km.toFixed(2) + ' km' : 'N/A'}</Text>

              <Text style={styles.message}>{resultData.message}</Text>
            </>
          )}
        </View>

        <TouchableOpacity style={styles.doneButton} onPress={() => setView('HOME')}>
          <Text style={styles.doneButtonText}>Done</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      {view === 'HOME' && renderHome()}
      {view === 'ENTER_NAME' && renderEnterName()}
      {view === 'CAMERA' && renderCamera()}
      {view === 'RESULT' && renderResult()}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  text: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
  // Home Styles
  homeContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginBottom: 50,
  },
  bigButton: {
    width: '100%',
    padding: 20,
    borderRadius: 15,
    marginBottom: 20,
    alignItems: 'center',
    elevation: 5,
  },
  bigButtonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    color: '#999',
    fontSize: 12,
  },
  // Camera Styles
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    position: 'absolute',
    top: 50,
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 10,
  },
  overlayText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 10,
    borderRadius: 5,
  },
  closeButton: {
    position: 'absolute',
    top: 0,
    right: 20,
    padding: 10,
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  controls: {
    position: 'absolute',
    bottom: 50,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  shutterButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#fff',
    borderWidth: 5,
    borderColor: '#ccc',
  },
  // Result Styles
  resultContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  resultIcon: {
    fontSize: 80,
    marginBottom: 20,
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
    color: '#333',
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.9)',
    padding: 20,
    borderRadius: 15,
    width: '100%',
    marginBottom: 30,
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginTop: 10,
  },
  value: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  message: {
    marginTop: 20,
    fontSize: 16,
    fontStyle: 'italic',
    textAlign: 'center',
    color: '#444',
  },
  doneButton: {
    backgroundColor: '#333',
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 30,
  },
  doneButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },

  input: {
    width: '100%',
    padding: 15,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 10,
    fontSize: 18,
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  cancelButton: {
    marginTop: 20,
    padding: 10,
  },
  cancelButtonText: {
    color: '#666',
    fontSize: 16,
  },
});
