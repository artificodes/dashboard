from django.contrib import admin
from members import models as gmodels
admin.site.register(gmodels.CgccPrograms)
admin.site.register(gmodels.CgccProgramsRegistration)
admin.site.register(gmodels.LraMembersBiodata)
admin.site.register(gmodels.Source)
admin.site.register(gmodels.ReportCategory)
admin.site.register(gmodels.Department)
admin.site.register(gmodels.Report)
admin.site.register(gmodels.ProgramRecord)
admin.site.register(gmodels.CgccProgram)
admin.site.register(gmodels.ApprovedUser)

admin.site.register(gmodels.Incident)
