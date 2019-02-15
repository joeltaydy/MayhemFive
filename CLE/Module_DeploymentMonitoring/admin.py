from django.contrib import admin
from Module_DeploymentMonitoring.models import *

class AWSCredentialsAdmin(admin.ModelAdmin):
    # define which columns displayed in changelist
    list_display = ('account_number', 'access_key', 'secret_access_key', 'image_details')
    # add filtering by date
    #list_filter = ('date',)
    # add search field 
    #search_fields = ['email', 'firstname']
    def image_details(self,obj):
        return "\n".join([image.imageId for image in  obj.imageDetails.all()])

class ImageAdmin(admin.ModelAdmin):
    list_display = ('imageName', 'teams')

    def teams(self,obj):
        return obj.sharedAccNum

class DeploymentPackageAdmin(admin.ModelAdmin):
    list_display = ('deployment_name','deployment_link','shared_sections')

# Register your models here.
admin.site.register(AWS_Credentials,AWSCredentialsAdmin)
admin.site.register(Image_Details,ImageAdmin)
admin.site.register(Deployment_Package,DeploymentPackageAdmin)
