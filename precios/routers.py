class PreciosRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    route_app_labels = {'precios','dj_shop_cart','precios_articulos'}
   
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
     
        if model._meta.app_label in self.route_app_labels:
            return 'precios'


        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """

        if model._meta.app_label in self.route_app_labels:
            return 'precios'


        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        #print('Precios->', model._meta.app_label)
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True

        # print('Precios_relleation: None')
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """

        if app_label in self.route_app_labels:
            return db == 'precios'

        return None

class MembersRouter:

    route_app_labels = {
        'members',
        'admin',
        'auth',
        'django_celery_beat',
        'django_celery_results',
        'contenttypes',
        'sessions',
    }
        # 'messages','humanize','staticfiles','auth_group' ,'auth_group_permissions' ,'auth_permission' ,'auth_user' ,'auth_user_groups' ,'auth_user_user_permissions' ,'address_address' ,'address_country' ,'address_locality' ,'address_state' ,'django_admin_log' ,'django_celery_beat_clockedschedule' ,'django_celery_beat_crontabschedule' ,'django_celery_beat_intervalschedule' ,'django_celery_beat_periodictask django_celery_beat_periodictasks' ,'django_celery_beat_solarschedule','django_celery_results_chordcounter' ,'django_celery_results_groupresult' ,'django_celery_results_taskresult' ,'django_content_type' ,'django_migrations' ,'django_session' }
    

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        # print(model._meta.app_label)
        if model._meta.app_label in self.route_app_labels:
            return 'members'

        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """

        if model._meta.app_label in self.route_app_labels:
            return 'members'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """

        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """

        if app_label in self.route_app_labels:
            return db == 'members'
        return None

