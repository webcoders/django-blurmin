
# View set members are defined by members attribute
# it is dictionary where keys are used as view_set_name to reference individual view from viewset
# and also this names are used in corresponding templates.
# each member consists from pattern and viewClass
# for example:
   class ModelViewSet(ViewSet):
    """ Use view set member name prefix to direct attribute for specific member,
    for example: to pass template_name for 'list' member, attribute must have name: 'list_template_name' """
    members={'list':('',GridViewSetMember),'change':('change',ChangeViewSetMember)}

# (MEMBER URL GENERATING)
# ViewSet combines all belonging view member url patterns under root pattern defined as viewset class name
# for example:
class MyViewSet(ModelViewSet):
    members={'list':('',GridViewSetMember),'change':('change',ChangeViewSetMember),'someother':OtherViewClass }
# # will generate the following st of patterns:
#     ^MyViewSet
#             ^/
#             ^/change
#             ^/someother

# URL helper functions:

    @classmethod
    def member_url_name(cls,name):
        return "%s_%s" % (cls.url_name(), name)

    @classmethod
    def get_member_url(cls,name):

# (HOW TO CREATE VIEWSET)

# To create view set:
    class MyViewSet(ModelViewSet):
        model = Test
        fields = ['f1','f2']
        readonly_fields = []
        list_editable = ['f1','f2']
        list_display = ['f1','f2']
        list_display_links = ['f1']
        exclude = []
        # add_form_template = None
        change_template_name = "my_change_view.html"
        list_template_name = "my_change_view.html"

# each viewset attribute will be assigned to matching viewset member attribute. So if you define 'model'
# attribute it will be used by all viewset members. But if you need to define model only for 'list' view member
# you add viewset name (key from members) prefix to it, for example:
         list_model=Test

# NOTE: list of possible attributes for the viewset members is defined in ViewSet.get_class_kwargs_names()
# if there is no attribute listed now (it needs to be fixed, how to provide ) . So you just need to add attribute
# to  ViewSet.get_class_kwargs_names() code, or use custom viewclass member for example:

# (HOW TO USE CUSTOM VIEWCLASS FOR MEMBER)

class CustomListMember(GridViewSetMember):
    custom_attr = 1

class MyViewSet(ModelViewSet):
    list_view = CustomListMember

# (VIEWSET ATTRIBUTES OVERRIDING SEQUENCE)
# It does not matter you define attributes in custom member class or viewset class definition
# (it is created only for convenience), But viewset attribute value takes precedence.


# (HOW TO CREATE CUSTOM VIEWCLASS MEMBER)

class MyCustomMember(ViewSetMemberMixin,MyViewClass):
    pass


# (HOW TO OVERRIDE VIEWCLASS MEMBER METHODS INSIDE VIEWSET)


# For example I need to add some context data to all viewset members:

class ModelViewSet(ViewSet):
#.................
    def get_context_data(self,view,**kwargs):
        ctx = view.get_context_data(_direct=1,**kwargs)
        ctx['change_view_url'] = self.get_member_url('change')
        ctx['state_name'] = self.get_menu_state_name()
        return ctx


# Then I need to override it in descendant:

class AdminPageViewSet(BaseAdminPage,ModelViewSet):
# ......................
    def get_context_data(self,view,**kwargs):
# Call ModelViewSet method
        context = super(AdminPageViewSet,self).get_context_data(view,**kwargs)
# Call BaseAdminPage method
# USE ALWAYS _direct=1 ATTRIBUTE when calling members method from viewset overriden method TO PREVENT INFINITE LOOPING)))
        context.update(view.get_context_data(_direct=1,**kwargs))
# Adding grid_view exaclty for the base view, and not for others!
        if view.view_set_name == 'base':
           context['grid_view'] = self.rendered_content(view.request, 'list')
        return context

# If you need to override method only for specific view just add its name as a prefix for the method name
# for example I need to override get_context_data only for the 'change' member:

        def change_get_context_data(self,view,**kwargs):
            # ...................
            pass

