from django.core.exceptions import FieldDoesNotExist
from django.db.models.constants import LOOKUP_SEP


def get_model_field_from_path(model, path):
    field = None
    relation_parts = []

    for part in path.split(LOOKUP_SEP):
        try:
            field = model._meta.get_field(part)
        except FieldDoesNotExist:
            # Lookups on non-existent fields are ok, since they're ignored
            # later.
            break

        if not getattr(field, 'get_path_info', None):
            # This is not a relational field, so further parts
            # must be transforms.
            break
        model = field.get_path_info()[-1].to_opts.model
    return field