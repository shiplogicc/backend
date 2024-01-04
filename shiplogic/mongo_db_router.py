class ScadiRTDBRouter(object):

    def db_for_read(self, model, **hints):

        app_list = ('smsapp','api_status_update')

        if model._meta.app_label in app_list:
            return 'scadirt'
        return None

    def db_for_write(self, model, **hints):

        app_list = ('smsapp','api_status_update')

        if model._meta.app_label in app_list:
            return 'scadirt'
        return None

    def allow_relation(self, obj1, obj2, **hints):

        app_list = ('smsapp','api_status_update')

        if obj1._state.db in app_list and obj2._state.db in app_list:
            return 'scadirt'
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):

        app_list = ('smsapp','api_status_update')

        if self._meta.app_label in app_list:
            return 'scadirt'
        return None
