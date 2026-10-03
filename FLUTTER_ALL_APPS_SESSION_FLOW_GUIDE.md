# Complete App-Side Session & Auth Implementation Guide for All 3 Flutter Apps

This guide contains the **complete, production-ready Flutter Dart implementation** for all 3 mobile applications:
1. 🛍️ **Customer App**
2. 🏪 **Restaurant Owner App**
3. 🛵 **Delivery Partner App**

---

## 📌 Role-to-API Endpoint Mapping Table

| App | Send OTP | Verify OTP | Refresh Token | Logout | List Devices | Logout All |
|---|---|---|---|---|---|---|
| **Customer App** | `POST /customer/auth/send-otp` | `POST /customer/auth/verify-otp` | `POST /customer/auth/refresh` | `POST /customer/auth/logout` | `GET /customer/auth/sessions` | `DELETE /customer/auth/sessions/all` |
| **Restaurant Owner App** | `POST /auth/send-otp` | `POST /auth/verify-otp` | `POST /auth/refresh` | `POST /auth/logout` | `GET /auth/sessions` | `DELETE /auth/sessions/all` |
| **Delivery Partner App** | `POST /delivery-partner/auth/send-otp` | `POST /delivery-partner/auth/verify-otp` | `POST /delivery-partner/auth/refresh` | `POST /delivery-partner/auth/logout` | `GET /delivery-partner/auth/sessions` | `DELETE /delivery-partner/auth/sessions/all` |

---

## 🛠️ Step 1: Shared Core Modules (Add to all 3 Apps)

### `pubspec.yaml`
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_secure_storage: ^9.0.0
  dio: ^5.4.0
  device_info_plus: ^10.0.0
```

---

### File 1: `lib/core/auth/auth_storage.dart`
```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthStorage {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyUserId = 'user_id';
  static const String _keyUserType = 'user_type';

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

  static Future<void> saveUserMeta({required int userId, required String userType}) async {
    await _storage.write(key: _keyUserId, value: userId.toString());
    await _storage.write(key: _keyUserType, value: userType);
  }

  static Future<void> clear() async {
    await _storage.deleteAll();
  }
}
```

---

### File 2: `lib/core/network/api_client.dart` (Auto-Refresh & Request Queueing)
```dart
import 'package:dio/dio.dart';
import '../auth/auth_storage.dart';

class ApiClient {
  final String refreshEndpoint;
  late Dio dio;
  bool _isRefreshing = false;
  final List<void Function(String newAccessToken)> _refreshSubscribers = [];

  ApiClient({
    required String baseUrl,
    required this.refreshEndpoint,
  }) {
    dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
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

          // Avoid infinite loops if refresh request itself failed
          if (reqOptions.path.contains(refreshEndpoint)) {
            await AuthStorage.clear();
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

              // Call refresh API
              final response = await dio.post(refreshEndpoint, data: {
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

              // Retry original request
              reqOptions.headers['Authorization'] = 'Bearer $newAccessToken';
              final retryResponse = await dio.fetch(reqOptions);
              return handler.resolve(retryResponse);
            } catch (e) {
              _isRefreshing = false;
              await AuthStorage.clear();
              return handler.next(error);
            }
          } else {
            // Queue concurrent requests while token is refreshing
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

## 🛍️ APP 1: Customer App Implementation

### `lib/services/customer_api_service.dart`
```dart
import '../core/network/api_client.dart';
import '../core/auth/auth_storage.dart';

class CustomerApiService {
  final ApiClient client = ApiClient(
    baseUrl: 'https://dharaidelivery.online/api/v1',
    refreshEndpoint: '/customer/auth/refresh',
  );

  // 1. Send OTP
  Future<bool> sendOtp(String phoneNumber) async {
    final response = await client.dio.post('/customer/auth/send-otp', data: {
      'phone_number': phoneNumber,
    });
    return response.data['success'] == true;
  }

  // 2. Verify OTP
  Future<Map<String, dynamic>> verifyOtp({
    required String phoneNumber,
    required String otpCode,
    String? deviceId,
    String? deviceName,
  }) async {
    final response = await client.dio.post('/customer/auth/verify-otp', data: {
      'phone_number': phoneNumber,
      'otp_code': otpCode,
      'device_id': deviceId ?? 'customer_device',
      'device_name': deviceName ?? 'Customer Mobile App',
    });

    final data = response.data;
    await AuthStorage.saveTokens(
      accessToken: data['access_token'],
      refreshToken: data['refresh_token'],
    );
    return data; // contains is_new_user & customer profile
  }

  // 3. Silent Auto-Login / Splash Check
  Future<bool> tryAutoLogin() async {
    final refreshToken = await AuthStorage.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await client.dio.post('/customer/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      await AuthStorage.saveTokens(
        accessToken: response.data['access_token'],
        refreshToken: response.data['refresh_token'],
      );
      return true;
    } catch (e) {
      await AuthStorage.clear();
      return false;
    }
  }

  // 4. Logout
  Future<void> logout() async {
    final refreshToken = await AuthStorage.getRefreshToken();
    if (refreshToken != null) {
      try {
        await client.dio.post('/customer/auth/logout', data: {
          'refresh_token': refreshToken,
        });
      } catch (_) {}
    }
    await AuthStorage.clear();
  }
}
```

---

## 🏪 APP 2: Restaurant Owner App Implementation

### `lib/services/owner_api_service.dart`
```dart
import '../core/network/api_client.dart';
import '../core/auth/auth_storage.dart';

class OwnerApiService {
  final ApiClient client = ApiClient(
    baseUrl: 'https://dharaidelivery.online/api/v1',
    refreshEndpoint: '/auth/refresh',
  );

  // 1. Send OTP
  Future<bool> sendOtp(String phoneNumber) async {
    final response = await client.dio.post('/auth/send-otp', data: {
      'phone_number': phoneNumber,
    });
    return response.data['success'] == true;
  }

  // 2. Verify OTP
  Future<Map<String, dynamic>> verifyOtp({
    required String phoneNumber,
    required String otpCode,
    String? deviceId,
    String? deviceName,
  }) async {
    final response = await client.dio.post('/auth/verify-otp', data: {
      'phone_number': phoneNumber,
      'otp_code': otpCode,
      'device_id': deviceId ?? 'owner_device',
      'device_name': deviceName ?? 'Restaurant Owner App',
    });

    final data = response.data;
    await AuthStorage.saveTokens(
      accessToken: data['access_token'],
      refreshToken: data['refresh_token'],
    );
    return data;
  }

  // 3. Silent Auto-Login
  Future<bool> tryAutoLogin() async {
    final refreshToken = await AuthStorage.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await client.dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      await AuthStorage.saveTokens(
        accessToken: response.data['access_token'],
        refreshToken: response.data['refresh_token'],
      );
      return true;
    } catch (e) {
      await AuthStorage.clear();
      return false;
    }
  }

  // 4. Logout
  Future<void> logout() async {
    final refreshToken = await AuthStorage.getRefreshToken();
    if (refreshToken != null) {
      try {
        await client.dio.post('/auth/logout', data: {
          'refresh_token': refreshToken,
        });
      } catch (_) {}
    }
    await AuthStorage.clear();
  }
}
```

---

## 🛵 APP 3: Delivery Partner App Implementation

### `lib/services/delivery_partner_api_service.dart`
```dart
import '../core/network/api_client.dart';
import '../core/auth/auth_storage.dart';

class DeliveryPartnerApiService {
  final ApiClient client = ApiClient(
    baseUrl: 'https://dharaidelivery.online/api/v1',
    refreshEndpoint: '/delivery-partner/auth/refresh',
  );

  // 1. Send OTP
  Future<bool> sendOtp(String phoneNumber) async {
    final response = await client.dio.post('/delivery-partner/auth/send-otp', data: {
      'phone_number': phoneNumber,
    });
    return response.data['success'] == true;
  }

  // 2. Verify OTP
  Future<Map<String, dynamic>> verifyOtp({
    required String phoneNumber,
    required String otpCode,
    String? deviceId,
    String? deviceName,
  }) async {
    final response = await client.dio.post('/delivery-partner/auth/verify-otp', data: {
      'phone_number': phoneNumber,
      'otp_code': otpCode,
      'device_id': deviceId ?? 'partner_device',
      'device_name': deviceName ?? 'Delivery Partner App',
    });

    final data = response.data;
    await AuthStorage.saveTokens(
      accessToken: data['access_token'],
      refreshToken: data['refresh_token'],
    );
    return data;
  }

  // 3. Complete Registration Profile (If is_new_user == true)
  Future<bool> completeRegistration({
    required String fullName,
    String? email,
    required String vehicleNumber,
  }) async {
    final response = await client.dio.post('/delivery-partner/register', data: {
      'full_name': fullName,
      'email': email,
      'vehicle_number': vehicleNumber,
    });
    return response.data['success'] == true;
  }

  // 4. Silent Auto-Login
  Future<bool> tryAutoLogin() async {
    final refreshToken = await AuthStorage.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await client.dio.post('/delivery-partner/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      await AuthStorage.saveTokens(
        accessToken: response.data['access_token'],
        refreshToken: response.data['refresh_token'],
      );
      return true;
    } catch (e) {
      await AuthStorage.clear();
      return false;
    }
  }

  // 5. Logout
  Future<void> logout() async {
    final refreshToken = await AuthStorage.getRefreshToken();
    if (refreshToken != null) {
      try {
        await client.dio.post('/delivery-partner/auth/logout', data: {
          'refresh_token': refreshToken,
        });
      } catch (_) {}
    }
    await AuthStorage.clear();
  }
}
```

---

## 📱 Standard Navigation Flow for All 3 Apps

```dart
// Example OTP Verification Logic in Screen Controller
void onVerifyOtpSubmitted(String phone, String otp) async {
  try {
    final result = await apiService.verifyOtp(
      phoneNumber: phone,
      otpCode: otp,
    );

    final bool isNewUser = result['is_new_user'] ?? false;

    if (isNewUser) {
      // Navigate to Profile Registration Screen
      Navigator.pushReplacementNamed(context, '/profile-setup');
    } else {
      // Direct access to Dashboard/Home Screen
      Navigator.pushReplacementNamed(context, '/home');
    }
  } catch (e) {
    showErrorDialog("Invalid OTP or Verification Failed");
  }
}
```
