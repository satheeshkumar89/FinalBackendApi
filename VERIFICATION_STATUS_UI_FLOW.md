# Verification Status Screen - API Integration Guide

This guide details how to implement the "Verification Status" screen design using the existing backend APIs.

## 1. API Endpoints

### Primary Endpoint (Load Data)
**GET** `/restaurant/verification-status`

Use this to populate the screen initially.

**Response:**
```json
{
  "success": true,
  "message": "Verification status retrieved successfully",
  "data": {
    "status": "under_review",      // pending, submitted, under_review, approved, rejected
    "verification_notes": null,    // Contains rejection reason if status is 'rejected'
    "updated_at": "2023-12-04T10:00:00"
  }
}
```

### Refresh Action
**GET** `/restaurant/refresh-status`

Call this when the user taps the "Refresh Status" button.

**Response:** Same structure as above.

---

## 2. UI State Mapping

Map the `data.status` field to your UI elements as follows:

### A. Main Status Card (Top)

| Backend Status | UI Title | UI Color | UI Description | Icon |
| :--- | :--- | :--- | :--- | :--- |
| `submitted` | **Submitted** | Blue | "Your application has been submitted and is waiting for review." | 📤 |
| `under_review` | **Under Review** | Orange | "Your documents are being reviewed by our team. This usually takes 24-48 hours." | ⏳ |
| `approved` | **Verified** | Green | "Congratulations! Your restaurant is now live." | ✅ |
| `rejected` | **Action Required** | Red | "Some documents were rejected. Please check the notes below." | ⚠️ |

**Note on Rejection:**
If `status == 'rejected'`, display the `data.verification_notes` text in the description area so the user knows what to fix.

### B. Verification Progress (Bottom Stepper)

The stepper logic is derived from the single `status` field.

#### Step 1: Documents Submitted
- **State**: Completed (Green Check)
- **Condition**: `status` is NOT `pending` (i.e., it is submitted, under_review, approved, or rejected).

#### Step 2: Under Review
- **State**:
    - **Active (Orange/Loading)**: If `status` is `submitted` or `under_review`.
    - **Completed (Green Check)**: If `status` is `approved` or `rejected`.
- **Condition**: Represents the admin looking at the docs.

#### Step 3: Verification Complete
- **State**:
    - **Completed (Green Check)**: If `status` is `approved`.
    - **Error (Red X)**: If `status` is `rejected`.
    - **Inactive (Grey)**: If `status` is `submitted` or `under_review`.

---

## 3. Flutter Implementation Logic

```dart
// 1. Call API
final response = await api.get('/restaurant/verification-status');
final status = response['data']['status']; // e.g., "under_review"

// 2. Determine Stepper State
bool isSubmitted = status != 'pending';
bool isReviewing = ['submitted', 'under_review'].contains(status);
bool isReviewDone = ['approved', 'rejected'].contains(status);
bool isApproved = status == 'approved';

// 3. Build UI
return Column(
  children: [
    // Top Card
    StatusCard(
      title: getTitle(status),
      color: getColor(status),
      description: status == 'rejected' 
          ? response['data']['verification_notes'] 
          : getDescription(status),
      onRefresh: () => api.get('/restaurant/refresh-status'),
    ),
    
    // Stepper
    StepperItem(
      title: "Documents Submitted",
      isActive: isSubmitted,
      isCompleted: isSubmitted,
    ),
    StepperItem(
      title: "Under Review",
      isActive: isReviewing,
      isCompleted: isReviewDone,
    ),
    StepperItem(
      title: "Verification Complete",
      isActive: isApproved,
      isCompleted: isApproved,
      isError: status == 'rejected',
    ),
  ],
);
```
