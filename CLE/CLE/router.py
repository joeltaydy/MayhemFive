# A router to control all database operations on models in the
# Module_TeamManagement application.
class TMRouter:

    # Attempts to read Module_TeamManagement models, got to CLE_Data
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'Module_TeamManagement' or model._meta.app_label == 'Module_DeploymentMonitoring':
            return 'CLE_Data'
        return None

    # Attempts to write Module_TeamManagement models, got to CLE_Data
    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'Module_TeamManagement' or model._meta.app_label == 'Module_DeploymentMonitoring':
            return 'CLE_Data'
        return None

    # Allow relations if a model in the Module_TeamManagement app is involved
    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'Module_TeamManagement' or \
            obj2._meta.app_label == 'Module_TeamManagement' or \
             obj1._meta.app_label == 'Module_DeploymentMonitoring' or \
              obj2._meta.app_label == 'Module_DeploymentMonitoring':
            return True
        return None

    # Make sure the Module_TeamManagement app only appears in the 'CLE_Data' database
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'Module_TeamManagement' or app_label == 'Module_DeploymentMonitoring':
            return db == 'CLE_Data'
        return None
