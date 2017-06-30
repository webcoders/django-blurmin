import os
from django.conf import settings
from time import gmtime, strftime, localtime, time

DEFAULT_SETTINGS = {
    'DIRECTORY': 'uploads/',
    'EXTENSIONS': {
        'Parent Folder': ['..'],
        'Folder': [''],
        'Image': ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff', '.svg'],
        'Video': ['.mov', '.wmv', '.mpeg', '.mpg', '.avi', '.rm'],
        'Document': ['.pdf', '.doc', '.rtf', '.txt', '.xls', '.csv'],
        'Audio': ['.mp3', '.mp4', '.wav', '.aiff', '.midi', '.m4p'],
        'Code': ['.html', '.py', '.js', '.css'],
        'Archive': ['.zip', '.gz', '.rar', '.7z', 'bz2']
    },
    'DEFAULT_SORTING_BY': "date",
    'DEFAULT_SORTING_ORDER': "desc",
    'LIST_PER_PAGE': 50,
}

def get_file_type(ext):
    for type, ext_list in get_setting('EXTENSIONS').items():
        if ext in ext_list:
            return type
    return None

def get_file_icon(ext):
    type = get_file_type(ext)
    if type == 'Folder':
        return 'fa fa-folder-o fa-lg'
    if type == 'Parent Folder':
        return 'fa fa-folder-open-o fa-lg'
    elif type == 'Image':
        return 'fa fa-file-image-o fa-lg'
    elif type == 'Video':
        return 'fa fa-file-video-o fa-lg'
    elif type == 'Document':
        return 'fa fa-file-text-o fa-lg'
    elif type == 'Audio':
        return 'fa fa-file-audio-o fa-lg'
    elif type == 'Code':
        return 'fa fa-file-code-o fa-lg'
    elif type == 'Archive':
        return 'fa fa-file-archive-o fa-lg'
    else:
        return 'fa fa-file-o fa-lg'

def get_setting(key):
    _settings = getattr(settings, 'FILE_BROWSER', DEFAULT_SETTINGS)
    return _settings.get(key, DEFAULT_SETTINGS[key])

def get_directory():
    dirname = get_setting('DIRECTORY')
    fullpath = os.path.join(settings.MEDIA_ROOT, dirname)
    if not os.path.isdir(fullpath):
        os.makedirs(fullpath)
    return fullpath

def get_url():
    dirname = get_setting('DIRECTORY')
    path = settings.MEDIA_URL + dirname
    return path
