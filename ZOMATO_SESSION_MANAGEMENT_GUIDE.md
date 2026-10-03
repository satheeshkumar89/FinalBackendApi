# Zomato-Style Session & Token Management Guide (FastAPI + Flutter)

This document provides a complete production guide for the **Zomato-style authentication & session management system** implemented in FastFoodie backend APIs.

---

## 📋 Table of Contents
1. [Overview & Architecture](#overview--architecture)
2. [Session Lifecycle Diagram](#session-lifecycle-diagram)
3. [Database Schema (`user_sessions`)](#database-schema-user_sessions)
4. [Backend API Reference](#backend-api-reference)
5. [Flutter Client Implementation (Complete Code)](#flutter-client-implementation-complete-code)
   - [Step 1: Secure Token Storage (`AuthStorage`)](#step-1-secure-token-storage-authstorage)
   - [Step 2: Dio Interceptor with Auto-Refresh & Queueing](#step-2-dio-interceptor-with-auto-refresh--queueing)
   - [Step 3: Splash Screen Auto-Login Logic](#step-3-splash-screen-auto-login-logic)
   - [Step 4: Multi-Device Session Revocation UI](#step-4-multi-device-session-revocation-ui)

---

## Overview & Architecture

### Key Features:
1. **Short-Lived Access Tokens**: Valid for **60 minutes** (used in `Authorization: Bearer <access_token>`).
2. **Long-Lived Refresh Tokens**: Valid for **30 days** (used only during `/auth/refresh`).
3. **Refresh Token Rotation**: Every call to `/auth/refresh` revokes the old refresh token and issues a **new** Access + Refresh Token pair. Reusing a revoked refresh token triggers a security alert and revokes all sessions.
4. **Multi-Device Support (`user_sessions`)**: Users can log in on multiple phones/tablets. Each device has a tracked session in the database.
5. **New User Detection**: The `verify-otp` API returns `"is_new_user": true` if the user needs profile setup/onboarding.

---

## Session Lifecycle Diagram

```
                              ┌──────────────────────────┐
                              │  User enters Phone & OTP │
                              └────────────┬─────────────┘
                                           │
                                 POST /auth/verify-otp
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │ FastAPI creates Session: │
                              │ Access Token (60 mins)   │
                              │ Refresh Token (30 days)  │
                              └────────────┬─────────────┘
                                           │
                                           ▼
                              ┌──────────────────────────┐
                              │ Store securely in        │
                              │ Flutter Secure Storage   │
                              └────────────┬─────────────┘
                                           │
             ┌─────────────────────────────┴─────────────────────────────┐
             │                                                           │
             ▼                                                           ▼
┌─────────────────────────┐                                 ┌─────────────────────────┐
│ Regular API Requests    │                                 │ App Restart / Splash    │
│ Authorization: Bearer   │                                 │ Read Tokens from        │
│ <access_token>          │                                 │ Secure Storage          │
└────────────┬────────────┘                                 └────────────┬────────────┘
             │                                                           │
             ▼                                                           │
  200 OK ? ───► Continue                                                 │
             │ (401 Unauthorized)                                        │
             ▼                                                           │
┌─────────────────────────┐                                              │
│ Flutter Dio Interceptor │                                              │
│ calls /auth/refresh     │◄─────────────────────────────────────────────┘
└────────────┬────────────┘
             │
   Success ? ┴─► YES: Store new tokens & Retry Request
             │
            NO (Revoked/Expired)
             │
             ▼
┌─────────────────────────┐
│ Clear Secure Storage &  │
│ Navigate to Login Screen│
└─────────────────────────┘
```

---

## Database Schema (`user_sessions`)

```sql
CREATE TABLE user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_type VARCHAR(50) NOT NULL, -- 'customer', 'owner', 'delivery_partner', 'admin'
    refresh_token_hash VARCHAR(255) NOT NULL UNIQUE,
    device_id VARCHAR(255) NULL,
    device_name VARCHAR(255) NULL,
    ip_address VARCHAR(50) NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    revoked_at DATETIME NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_user_type_id (user_id, user_type),
    INDEX idx_refresh_hash (refresh_token_hash)
);
```

---

## Backend API Reference

### 1. Verify OTP & Create Session
* **Customer**: `POST /customer/auth/verify-otp` (or `/customer/auth/firebase-verify`)
* **Restaurant Owner**: `POST /auth/verify-otp`
* **Delivery Partner**: `POST /delivery-partner/auth/verify-otp`

**Request Body:**
```json
{
  "phone_number": "+919876543210",
  "otp_code": "123456",
  "device_id": "unique-device-uuid",
  "device_name": "iPhone 15 Pro"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "refresh_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "expires_in": 3600,
  "is_new_user": false,
  "customer": {
    "id": 123,
    "full_name": "Kumar",
    "phone_number": "+919876543210"
  }
}
```

---

### 2. Refresh Token (Token Rotation)
* **Customer**: `POST /customer/auth/refresh`
* **Restaurant Owner**: `POST /auth/refresh`
* **Delivery Partner**: `POST /delivery-partner/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1Ni...",
  "device_id": "unique-device-uuid",
  "device_name": "iPhone 15 Pro"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...NEW",
  "refresh_token": "eyJhbGciOiJIUzI1Ni...NEW_ROTATED",
  "token_type": "bearer",
  "expires_in": 3600,
  "is_new_user": false
}
```

---

### 3. Logout (Revoke Current Session)
* **Endpoint**: `POST /customer/auth/logout` (or `/auth/logout`, `/delivery-partner/auth/logout`)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1Ni..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully and session revoked",
  "data": null
}
```

---

### 4. List Active Devices & Logout All
* **Get Devices**: `GET /customer/auth/sessions` (Headers: `Authorization: Bearer <access_token>`)
* **Logout All Devices**: `DELETE /customer/auth/sessions/all`

---

## Flutter Client Implementation (Complete Code)

### Step 1: Secure Token Storage (`AuthStorage`)

Add dependencies in `pubspec.yaml`:
```yaml
dependencies:
  flutter_secure_storage: ^9.0.0
  dio: ^5.4.0
```

Create `lib/services/auth_storage.dart`:
```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthStorage {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';

  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: _keyAccessToken, value: accessToken);
    await _storage.write(key: _keyRefreshToken, value: refreshToken);
  }

  static Future<String?> getAccessToken() async {
    return await _storage.read(key: _keyAccessToken);
  }

  static Future<String?> getRefreshToken() async {
    return await _storage.read(key: _keyRefreshToken);
  }

  static Future<void> clear() async {
    await _storage.deleteAll();
  }
}
```

---

### Step 2: Dio Interceptor with Auto-Refresh & Queueing

Create `lib/services/api_client.dart`:
```dart
import 'package:dio/dio.dart';
import 'auth_storage.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  late Dio dio;
  bool _isRefreshing = false;
  final List<void Function(String newAccessToken)> _refreshSubscribers = [];

  factory ApiClient() => _instance;

  ApiClient._internal() {
    dio = Dio(BaseOptions(
      baseUrl: 'https://dharaidelivery.online/api/v1',
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await AuthStorage.getAccessToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (DioException error, handler) async {
        if (error.response?.statusCode == 401) {
          final reqOptions = error.requestOptions;

          // Prevent infinite loop if /refresh itself returned 401
          if (reqOptions.path.contains('/auth/refresh')) {
            await AuthStorage.clear();
            // TODO: Navigate to Login Screen
            return handler.next(error);
          }

          if (!_isRefreshing) {
            _isRefreshing = true;
            try {
              final refreshToken = await AuthStorage.getRefreshToken();
              if (refreshToken == null) {
                await AuthStorage.clear();
                return handler.next(error);
              }

              final response = await dio.post('/customer/auth/refresh', data: {
                'refresh_token': refreshToken,
              });

              final newAccessToken = response.data['access_token'];
              final newRefreshToken = response.data['refresh_token'];

              await AuthStorage.saveTokens(
                accessToken: newAccessToken,
                refreshToken: newRefreshToken,
              );

              _isRefreshing = false;
              _onTokenRefreshed(newAccessToken);

              // Retry original failed request
              reqOptions.headers['Authorization'] = 'Bearer $newAccessToken';
              final retryResponse = await dio.fetch(reqOptions);
              return handler.resolve(retryResponse);
            } catch (e) {
              _isRefreshing = false;
              await AuthStorage.clear();
              // TODO: Navigate to Login Screen
              return handler.next(error);
            }
          } else {
            // Queue pending requests while token is refreshing
            return _subscribeTokenRefresh((newAccessToken) async {
              reqOptions.headers['Authorization'] = 'Bearer $newAccessToken';
              try {
                final retryResponse = await dio.fetch(reqOptions);
                handler.resolve(retryResponse);
              } catch (e) {
                handler.next(error);
              }
            });
          }
        }
        return handler.next(error);
      },
    ));
  }

  void _onTokenRefreshed(String token) {
    for (var callback in _refreshSubscribers) {
      callback(token);
    }
    _refreshSubscribers.clear();
  }

  void _subscribeTokenRefresh(void Function(String token) callback) {
    _refreshSubscribers.add(callback);
  }
}
```

---

### Step 3: Splash Screen Auto-Login Logic

Create `lib/screens/splash_screen.dart`:
```dart
import 'package:flutter/material.dart';
import '../services/auth_storage.dart';
import '../services/api_client.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    await Future.delayed(const Duration(seconds: 1)); // Splash duration

    final refreshToken = await AuthStorage.getRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      _navigateToLogin();
      return;
    }

    try {
      // Refresh token silently to verify session validity
      final response = await ApiClient().dio.post(
        '/customer/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      await AuthStorage.saveTokens(
        accessToken: response.data['access_token'],
        refreshToken: response.data['refresh_token'],
      );

      _navigateToHome();
    } catch (e) {
      await AuthStorage.clear();
      _navigateToLogin();
    }
  }

  void _navigateToHome() {
    Navigator.of(context).pushReplacementNamed('/home');
  }

  void _navigateToLogin() {
    Navigator.of(context).pushReplacementNamed('/login');
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
```
