export interface NotificationRequest {
  userId: string;
  channel: 'push' | 'email';
  message: string;
}

export interface NotificationResponse {
  queued: boolean;
  notificationId?: string;
}
