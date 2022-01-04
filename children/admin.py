from django.contrib import admin
from children import models as chmodels
admin.site.register(chmodels.LraMembersChildren)
admin.site.register(chmodels.General)
