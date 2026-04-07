import express from 'express';
import { z } from 'zod';
import winston from 'winston';

const log = winston.createLogger({
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});

const app = express();
app.use(express.json());

const NotificationSchema = z.object({
  userId: z.string(),
  channel: z.enum(['push', 'email']),
  message: z.string().max(500),
});

app.post('/api/notifications', (req, res) => {
  const parsed = NotificationSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ errors: parsed.error.errors });
  }
  log.info('notification_received', {
    userId: parsed.data.userId,
    channel: parsed.data.channel,
  });
  res.json({ queued: true });
});

app.listen(3000, () => log.info('server_started', { port: 3000 }));
