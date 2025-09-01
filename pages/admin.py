from django.contrib import admin
from .models import CustomUser, ActivationToken, PasswordResetToken, Category, Project, ProjectImage, Comment, Donation, Rating, Report

admin.site.register(CustomUser)
admin.site.register(ActivationToken)
admin.site.register(PasswordResetToken)
admin.site.register(Category)
admin.site.register(Project)
admin.site.register(ProjectImage)
admin.site.register(Comment)
admin.site.register(Donation)
admin.site.register(Rating)
admin.site.register(Report)
