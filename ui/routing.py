from channels.routing import route_class

from ma import notifications

channel_routing = [
    route_class(notifications.NotificationConsumer, path=r"^/notifications/"),
]
