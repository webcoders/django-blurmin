import json
import datetime

from django.db.models.fields.files import FieldFile
from django.utils.timezone import is_aware
import decimal
import uuid
from django.utils import formats

from ui.models import ImageFieldFile


class UiJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.
    """
    def default(self, o):
        from django.db import models
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            return formats.date_format(o, "SHORT_DATETIME_FORMAT")
        elif isinstance(o, datetime.date):
            return formats.date_format(o, "DATE_FORMAT")
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return float(str(o))
        elif isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, models.ImageField):
            return o.path
        elif isinstance(o, ImageFieldFile) or isinstance(o, FieldFile):
            if o:
                return o.path
            return ''
        else:
            return super(UiJSONEncoder, self).default(o)
