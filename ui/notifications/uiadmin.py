from ui.adminpage import AdminPage
from ui.notifications.models import NotificationRecipient
from ui.views.gridview.filters.fields import DateFieldFilter
from ui.views.gridview.view import GridView
from ui import ui

class NotificationGridView(GridView):
    model = NotificationRecipient
    paginate_by = 25

    search_fields = ['notification__title', 'notification__message']

    list_filter = ['notification__level', (DateFieldFilter, 'notification__timestamp', 'Date')]

    list_display = [('notification__level', 'Level'), ('notification__timestamp', 'Date'),
                    ('notification__title', 'Title'), ('notification__message', 'Message')]

    list_order = ['notification__level', 'notification__timestamp', ]

    def get_queryset(self):
        return super(NotificationGridView, self).get_queryset().filter(recipient=self.request.user)


class NotificationAdminPage(AdminPage):
    template_name= 'ui/notifications.html'
    title = 'Notifications'
    icon = 'fa fa-bell-o'
    panel_title = 'All notifications'

    def get_context_data(self, **kwargs):
        context = super(NotificationAdminPage, self).get_context_data(**kwargs)
        context['grid_view'] = NotificationGridView.rendered_content(self.request)
        return context

ui.register(NotificationAdminPage)
ui.register(NotificationGridView)
