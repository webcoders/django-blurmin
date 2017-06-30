import datetime
import errno
import logging
import os
import shutil
import tempfile
import time
from django.conf import settings
from django.contrib.sessions.backends.base import (
    VALID_KEY_CHARS, CreateError, SessionBase,
)
from django.contrib.sessions.exceptions import InvalidSessionKey
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.utils import timezone
from django.utils.encoding import force_text
import pickle
import hashlib
from django.apps import apps
import fcntl

class SessionStore(SessionBase):
    """
    Implements a file based session store.
    """
    def __init__(self, session_key=None):
        self.storage_path = type(self)._get_storage_path()
        self.file_prefix = settings.SESSION_COOKIE_NAME
        super(SessionStore, self).__init__(session_key)

    @classmethod
    def _get_storage_path(cls):
        try:
            return cls._storage_path
        except AttributeError:
            storage_path = getattr(settings, "SESSION_FILE_PATH", None)
            if not storage_path:
                storage_path = tempfile.gettempdir()

            # Make sure the storage path is valid.
            if not os.path.isdir(storage_path):
                raise ImproperlyConfigured(
                    "The session storage path %r doesn't exist. Please set your"
                    " SESSION_FILE_PATH setting to an existing directory in which"
                    " Django can store session data." % storage_path)

            cls._storage_path = storage_path
            return storage_path

    def _key_to_file(self, session_key=None):
        """
        Get the file associated with this session key.
        """
        if session_key is None:
            session_key = self._get_or_create_session_key()

        # Make sure we're not vulnerable to directory traversal. Session keys
        # should always be md5s, so they should never contain directory
        # components.
        if not set(session_key).issubset(set(VALID_KEY_CHARS)):
            raise InvalidSessionKey(
                "Invalid characters in session key")

        return os.path.join(self.storage_path, self.file_prefix + session_key)

    def _last_modification(self):
        """
        Return the modification time of the file storing the session's content.
        """
        modification = os.stat(self._key_to_file()).st_mtime
        if settings.USE_TZ:
            modification = datetime.datetime.utcfromtimestamp(modification)
            modification = modification.replace(tzinfo=timezone.utc)
        else:
            modification = datetime.datetime.fromtimestamp(modification)
        return modification

    # def encode(self, session_dict):
    #     return pickle.loads(session_dict)
    #
    # def decode(self, session_data):
    #     return pickle.dumps(session_data)

    def load(self):
        session_data = {}
        try:
            key_to_file = self._key_to_file()
            if not os.path.exists(key_to_file):
                return {}
            for fname in os.listdir(key_to_file):
                file_name = os.path.join(key_to_file, fname)

                f = open(file_name, 'r+b')
                while True:
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except IOError as e:
                        # raise on unrelated IOErrors
                        if e.errno != errno.EAGAIN:
                            raise
                        else:
                            time.sleep(0.1)
                try:
                    file_data = f.read()
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
                    f.close()

                # Don't fail if there is no data in the session file.
                # We may have opened the empty placeholder file.
                if file_data:
                    try:
                        session_data[fname] = self.decode(file_data)
                    except (EOFError, SuspiciousOperation) as e:
                        if isinstance(e, SuspiciousOperation):
                            logger = logging.getLogger('django.security.%s' %
                                    e.__class__.__name__)
                            logger.warning(force_text(e))
                        else:
                            raise
                        self.create()

                    # Remove expired sessions.
                    expiry_age = self.get_expiry_age(
                        modification=self._last_modification(),
                        expiry=session_data.get('_session_expiry'))
                    if expiry_age < 0:
                        session_data = {}
                        self.delete()
                        self.create()
        except (IOError, SuspiciousOperation):
            self._session_key = None
        return session_data

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if self.session_key is None:
            return self.create()
        # Get the session data now, before we start messing
        # with the file it is stored within.
        session_data = self._get_session(no_load=must_create)

        if not session_data:
            return

        session_file_name = self._key_to_file()

        try:
            # Make sure the file exists.
            os.mkdir(session_file_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        dir, prefix = os.path.split(session_file_name)
        try:
            for key, value in session_data.items():
                #output_file_fd, output_file_name = tempfile.mkstemp(dir=session_file_name,
                #                                                    prefix=key + '_out_')
                file_name = os.path.join(session_file_name, key)

                f = open(file_name, 'w')
                while True:
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except IOError as e:
                        # raise on unrelated IOErrors
                        if e.errno != errno.EAGAIN:
                            raise
                        else:
                            time.sleep(0.1)
                try:
                    f.write(self.encode(value))
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
                    f.close()

        except (OSError, IOError, EOFError):
            raise

    def exists(self, session_key):
        return os.path.exists(self._key_to_file(session_key))

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            shutil.rmtree(self._key_to_file(session_key))
        except OSError:
            pass

    def clean(self):
        pass

    @classmethod
    def clear_expired(cls):
        storage_path = cls._get_storage_path()
        file_prefix = settings.SESSION_COOKIE_NAME

        for session_file in os.listdir(storage_path):
            if not session_file.startswith(file_prefix):
                continue
            session_key = session_file[len(file_prefix):]
            session = cls(session_key)
            # When an expired session is loaded, its file is removed, and a
            # new file is immediately created. Prevent this by disabling
            # the create() method.
            session.create = lambda: None
            session.load()



def save_queryset(request, queryset):
    dump = pickle.dumps({'app_label': queryset.model._meta.app_label,
                         'model_name': queryset.model._meta.model_name,
                         'query': queryset.query})
    m = hashlib.md5()
    m.update(dump)
    h = queryset.model._meta.model_name + m.hexdigest()
    if not h in request.session:
        request.session[h] = dump
    return h

def load_queryset(request, key):
    key = str(key).strip()
    d = pickle.loads(request.session[key])
    q = apps.get_model(d['app_label'], d['model_name']).objects.all()
    q.query = d['query']
    return q
