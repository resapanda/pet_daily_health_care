# notification-service

Microservice for pushing notifications at specific times to subscribed applications.

- **create_notification** (`POST /notification`): Schedules a new notification. Supports both one-off events and periodic events.
- **delete_notification** (`DELETE/notification/<notification_id>`): Delete notification

## Webhook Receiver Setup

To receive notifications from this service, your main application must have an endpoint listening to POST requests on the http://localhost:5123/webhook.

- WEBHOOK_URL : http://localhost:5123/webhook
- Payload Structure

```
{
    "user_id" : 100,
    "type" : "PERIODIC",
    "title" : "Health Reminder",
    "message" : "Time to drink water!"
}
```

## API Endpoints

## POST /notification

### Payload (Periodic event) :

```
{
    "user_id": 100,
    "type": "PERIODIC",
    "title": "Health Reminder",
    "message": "Time to drink water!",
    "notify_at": "1772690400",
    "interval_seconds": 3600
}
```

- notify_at: unix timestamp

### Payload (Scheduled event) :

```
{
    "user_id": 200,
    "type": "ONE_OFF",
    "title": "Deadline Alert",
    "message": "The project proposal is due in 10 minutes!",
    "notify_at": "2026-03-05 09:00:00"
}
```

### Response :

```
{
    "message": "scheduled successfully!",
    "notification_id": 1
}
```

## DELETE/notification/<notification_id>

### Parameter :

- notification_id: The unique ID returned during scheduling notification.
