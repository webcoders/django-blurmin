from myapp.models import Person
from ui.views.gridview.filters.fields import DateFieldFilter
from ui.views.viewset import AdminPageViewSet
from ui import ui

class PersonExampleAdmin(AdminPageViewSet):
    model = Person
    base_url = 'person'
    state_name = 'person'
    paginate_by = 5
    render_form = True
    list_display = ['id', 'first_name', 'last_name', 'date', 'email', 'age', 'sex', 'revenue']
    list_filter = ['first_name', 'last_name', 'sex', (DateFieldFilter, 'date'), ]
    list_display_links = ['last_name']
    list_editable = ['first_name','date']
    title = 'Person example'
    icon = 'fa fa-tasks'
    panel_title = 'Person example'
    use_menu_template = 'state'


ui.register(PersonExampleAdmin)
