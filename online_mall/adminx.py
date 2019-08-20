import xadmin
from xadmin import views


@xadmin.sites.register(views.CommAdminView)
class GlobalSettings(object):
    site_title = 'Online Mall 后台'
    site_footer = '2019 Ghosque, Inc. All rights reserved.'
    # menu_style = 'accordion'


@xadmin.sites.register(views.BaseAdminView)
class BaseSetting:
    enable_themes = True
    use_bootswatch = True
