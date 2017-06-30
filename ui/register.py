from ui import ui
from ui.dashboard.todo import ToDoListView
from ui.views.auth import LoginView
from ui.views.module import DashboardMenuView

ui.register(LoginView)
ui.register(DashboardMenuView)
# ui.register(CompanyFileBrowserAdminPage)
ui.register(ToDoListView)
