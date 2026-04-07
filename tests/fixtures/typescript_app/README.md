# Notification API

TypeScript Express API that sends push notifications via Firebase and emails via SendGrid.

## Architecture

- **NotificationController**: `POST /api/notifications` — validates and routes requests
- **FirebaseAdapter**: Wraps Firebase Admin SDK for push notification delivery
- **SendGridAdapter**: Wraps SendGrid SDK for transactional email

## Tech Stack

TypeScript 5, Express 4, Zod, Firebase Admin, SendGrid, Jest, Winston
