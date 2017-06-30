import os
from channels.asgi import get_channel_layer
import sys

# sys.path.append('./old_admin')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

channel_layer = get_channel_layer()
