# Restaurant Verification Status API

## Overview
This API allows the restaurant owner to check the current verification status of their restaurant. This is typically used during the onboarding process or to check if a submitted application has been approved or rejected.

## Endpoint
`GET /restaurant/verification-status`

## Authentication
Requires a valid Bearer token for a restaurant owner.
- **Header**: `Authorization: Bearer <your_access_token>`

## Response Format

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Verification status retrieved successfully",
  "data": {
    "status": "pending",          // Enum: pending, submitted, under_review, approved, rejected
    "verification_notes": null,   // String: Reason for rejection or admin notes
    "updated_at": "2023-10-27T10:00:00" // Timestamp of last update
  }
}
```

### Error Responses

- **401 Unauthorized**: Token is missing or invalid.
- **404 Not Found**: Restaurant profile not found for the current user.

## Status Definitions
- **pending**: Initial state. The restaurant has been created but not yet submitted for verification.
- **submitted**: The owner has completed all steps and submitted the application.
- **under_review**: Admin is currently reviewing the application.
- **approved**: The restaurant is verified and can start operating.
- **rejected**: The application was rejected. Check `verification_notes` for the reason.

## Related Endpoint: Onboarding Status
For a more detailed breakdown of which steps are completed (Owner Details, Restaurant Details, Address, Cuisine, Documents), use:

`GET /restaurant/onboarding-status`

### Response Example
```json
{
  "success": true,
  "message": "Onboarding status retrieved",
  "data": {
    "owner_details_completed": true,
    "restaurant_details_completed": true,
    "address_details_completed": true,
    "cuisine_selection_completed": true,
    "document_upload_completed": false,
    "next_step": "document_upload",
    "verification_status": "pending"
  }
}
```
