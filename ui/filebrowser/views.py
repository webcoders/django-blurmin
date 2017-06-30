import os

from django.http.response import HttpResponse, HttpResponseForbidden
from django.utils.dateparse import parse_date
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from mezzanine.utils.importing import import_dotted_path

from ui.adminpage import AdminPage
from ui import ui
from ui.filebrowser.functions import get_directory, get_file_icon, get_url, get_file_type
from django.utils.translation import ugettext as _
from django.contrib import messages
from datetime import datetime
from ui.views.gridview.filters.fields import DateFieldFilter
from ui.views.gridview.view import GridView
from operator import itemgetter
from django.utils import formats
from dateutil import relativedelta
from django.conf import settings
import shutil

filter_re = []

LIST = 0
NEW_FOLDER = 1
UPLOAD = 2
RENAME = 3
REMOVE = 4


def file_filter(request, action, dir, file):
    if hasattr(settings, 'FILEBROWSER_FILTER'):
        _filter = import_dotted_path(settings.FILEBROWSER_FILTER)
        return _filter(request, action, dir, file)
    return True

class FileQuerySet(object):
    def __init__(self, request, file_list):
        self.file_list = file_list
        self.request = request

    def ordered(self):
        return True
    ordered = property(ordered)

    def __getitem__(self, i):
        return self.file_list[i]

    def __len__(self):
        return len(self.file_list)

    def get_queryset(self):
        return self.file_list

    def order_by(self, *sort):
        if not sort:
            sort = ['-is_dir']
        items = self.get_queryset()
        comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else
                      (itemgetter(col.strip()), 1)) for col in sort]

        def comparer(left, right):
            for fn, mult in comparers:
                result = cmp(fn(left), fn(right))
                if result:
                    return mult * result
            else:
                return 0

        return sorted(items, cmp=comparer)

    def values(self, *args, **kwargs):
        return self.get_queryset()


class FileBrowserGridView(GridView):
    template_name= 'ui/filebrowser/grid.html'

    list_display = [({'checker': ['is_dir', 'url_path']}, ''),
                    ({'_is_dir': ['is_dir', 'file', 'url_path']}, 'File / Folder'),
                    ({'_file': ['is_dir', 'file', 'url_path']}, 'File Name'),
                    ('date', 'Date'), ('size', 'Size'), ({'rename': ['file', 'url_path']}, ''),
                    ({'remove': ['file', 'url_path']}, '')]
    paginate_by = 10
    search_fields = ['file']
    list_filter = [(DateFieldFilter, 'date', 'Date')]

    list_order = ['file', 'date']

    ordering = []

    def _file(self, is_dir, file, url_path):
        if not is_dir:
            return """<a href="%s">%s</a>""" % (get_url() + url_path, file)
        return file

    def rename(self, file, url_path):
        if file!='..':
            return """
    <a href ng-click="renameFileFolderDialog('%s')" class="text-left"><span class="fa fa-pencil"/></a>
""" % (file)

    def remove(self, file, url_path):
            if file != '..':
                return """
        <a href ng-click="removeFileFolderDialog('%s')" class="text-left"><span class="fa fa-times"/></a>
""" % (file)

    def checker(self, is_dir, url_path):
        if not is_dir:
            css_class = 'fa fa-check-circle-o fa-lg'
            return """<a href ng-click="ok('%s');"><span class="%s"/></a>""" % (
                get_url() + url_path, css_class)
        return ''

    def _is_dir(self, is_dir, file, url_path):
        extension = os.path.splitext(file)[1]
        if file == '..':
            extension = file
        css_class = get_file_icon(extension)
        if is_dir:
            return """
                    <a href ng-click="data.extra_data.dir = '%s'; getData(1, undefined)"><span class="%s"/></a>""" % (
                url_path, css_class)
        elif get_file_type(extension) == "Image":
            return '<span class="%s popup-tooltip"><span><img style="width:100%%" class="callout" src="%s" /></span></span>' % (css_class,
                                                                                                        get_url() + url_path)
        return '<span class="%s"></span>' % (css_class)

    def get_search_results(self, queryset, search_string):
        results = []
        for row in queryset:
            found = False
            for field in self.search_fields:
                if unicode(search_string).lower() in row[field].decode('utf-8').lower():
                    if not found:
                        results.append(row)
                        found = True
        return results

    def get_filter_results(self, queryset, condition):
        date = None
        date_from = None
        date_to = None
        if condition.name == "Today":
            date = formats.date_format(datetime.now())
        if condition.name == "This Week":
            date_from = formats.date_format(datetime.now() + relativedelta.relativedelta(weeks=-1))
        if condition.name == "This Month":
            date_from = formats.date_format(datetime.now() + relativedelta.relativedelta(months=-1))
        if condition.name == "This Year":
            date_from = formats.date_format(datetime.now() + relativedelta.relativedelta(years=-1))
        if condition.name == "Choice Date":
            date = condition.values['date']
        if date_from:
            date_to = formats.date_format(datetime.now())
        if condition.name == "Date Range":
            date_from = condition.values['date_from']
            date_to = condition.values['date_to']

        results = []

        if date:
            date = parse_date(date)

        if date_from:
            date_from = parse_date(date_from)

        if date_to:
            date_to = parse_date(date_to)

        for row in queryset:
            row_date = parse_date(row['date'])
            if date_from:
                if date_from <= row_date <= date_to:
                    results.append(row)
            else:
                if date == row_date:
                    results.append(row)
        return results

    def get_queryset(self):
        queryset = FileQuerySet(self.request, self.file_queryset())
        for cond in self.conditions:
            queryset = FileQuerySet(self.request, self.get_filter_results(queryset, cond))
        if 'search' in self.request.GET:
            search_string = self.request.GET['search']
            if search_string:
                queryset = FileQuerySet(self.request, self.get_search_results(queryset, search_string))

        if 'sort' in self.request.GET:
            sort = self.deserialize(self.request.GET['sort'])
            return queryset.order_by(*sort)
        return queryset


    def file_queryset(self):
        extra = self.request.GET.get('extra', '')
        path = ''
        if extra:
            extra = self.deserialize(extra)
            path = extra['dir']

        directory = get_directory()

        abs_path = os.path.join(directory, path)
        if '.' in path or '~' in path or path.startswith('/'):
            msg = _('The requested Folder does not exist.')
            messages.add_message(self.request, messages.ERROR, msg)
            return []
        file_list = os.listdir(abs_path)
        files = []
        for file in file_list:
            if file.startswith('.'):
                continue

            if not file_filter(self.request, LIST, abs_path, file):
                continue

            full_path = os.path.join(abs_path, file)
            fileobject = {'is_dir': os.path.isdir(full_path),
                          'file': file,
                          'date': formats.date_format(datetime.fromtimestamp(os.path.getmtime(full_path))),
                          'url_path': os.path.join(path, file),
                          'size': '%sKb' % (os.path.getsize(full_path) / 1024)}
            files.append(fileobject)
        if path:
            fileobject = {'is_dir': True,
                          'file': '..',
                          'date': '',
                          'url_path': os.path.dirname(path),
                          'size': ''}
            files.insert(0, fileobject)
        return files


class FileBrowserAdminPage(AdminPage):
    title = 'File Browser'
    icon = 'fa fa-folder-open-o'
    panel_title = 'Browse Your Files & Directories.'
    template_name= 'ui/filebrowser/index.html'

    def get_context_data(self, **kwargs):
        context = super(FileBrowserAdminPage, self).get_context_data(**kwargs)
        if not self.request.is_ajax():
            context['grid_view'] = FileBrowserGridView.rendered_content(self.request)
        return context

class FileBrowserDialog(FileBrowserAdminPage):
    template_name= 'ui/filebrowser/modal_dialog.html'

class FileBrowserNewFolderDialog(FileBrowserAdminPage):

    template_name= 'ui/filebrowser/new_folder_dialog.html'

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            if 'folder_name' in self.request.GET:
                new_folder = self.request.GET['folder_name']
                dir = self.request.GET.get('dir', '')
                if dir.startswith('/'):
                    dir = dir[1:]
                dir = os.path.join(get_directory(), dir)
                if not file_filter(self.request, NEW_FOLDER, dir, new_folder):
                    return self.serialize(['Permissions denied'])
                final_dir = os.path.join(dir, new_folder)
                if not os.path.exists(final_dir):
                    os.mkdir(final_dir)
                return HttpResponse(self.serialize(['created']))
        return super(FileBrowserNewFolderDialog, self).render_to_response(context, **response_kwargs)


class FileBrowserRenameDialog(FileBrowserAdminPage):
    template_name= 'ui/filebrowser/rename_dialog.html'

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            if 'new_file_name' in self.request.GET:
                new_file_name = self.request.GET['new_file_name']
                old_file_name = self.request.GET['old_file_name']
                dir = self.request.GET.get('dir', '')
                if dir.startswith('/'):
                    dir = dir[1:]
                dir = os.path.join(get_directory(), dir)
                if not file_filter(self.request, RENAME, dir, [old_file_name, new_file_name]):
                    return self.serialize(['Permissions denied'])
                new_file_name = os.path.join(dir, new_file_name)
                old_file_name = os.path.join(dir, old_file_name)
                if os.path.exists(old_file_name):
                    os.rename(old_file_name, new_file_name)
                return HttpResponse(self.serialize(['renamed']))
        return super(FileBrowserRenameDialog, self).render_to_response(context, **response_kwargs)

class FileBrowserRemoveDialog(FileBrowserAdminPage):

    template_name= 'ui/filebrowser/remove_dialog.html'

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            if 'file_name' in self.request.GET:
                file_name = self.request.GET['file_name']
                dir = self.request.GET.get('dir', '')
                if dir.startswith('/'):
                    dir = dir[1:]
                dir = os.path.join(get_directory(), dir)
                if not file_filter(self.request, REMOVE, dir, file_name):
                    return self.serialize(['Permissions denied'])
                file_name = os.path.join(dir, file_name)
                if os.path.exists(file_name):
                    if os.path.isdir(file_name):
                        shutil.rmtree(file_name)
                    else:
                        os.remove(file_name)
                return HttpResponse(self.serialize(['renamed']))
        return super(FileBrowserRemoveDialog, self).render_to_response(context, **response_kwargs)


class FileBrowserUploadDialog(FileBrowserAdminPage):
    template_name= 'ui/filebrowser/upload_dialog.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(FileBrowserUploadDialog, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        dir = self.request.GET.get('dir', '')
        if dir == 'undefined':
            dir = ''
        dir = os.path.join(get_directory(), dir)
        file = request.FILES['file']
        if not file_filter(self.request, UPLOAD, dir, file.name):
            return self.serialize({'answer': 'Permissions denied'})
        f = open(os.path.join(dir, file.name), 'wb')
        f.write(file.read())
        f.close()
        return self.serialize({'answer': 'success'})

ui.register(FileBrowserGridView)
ui.register(FileBrowserDialog)
ui.register(FileBrowserUploadDialog)
ui.register(FileBrowserNewFolderDialog)
ui.register(FileBrowserRenameDialog)
ui.register(FileBrowserRemoveDialog)
