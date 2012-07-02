from django.contrib import admin 

from .models import Vacancy, Document

class VacancyAdmin(admin.ModelAdmin):
    list_display = ('vacancy_id', 'title', 'location', 'salary', 'contact_name', 'contact_phone', 'contact_email', 'internal', 'opening_date', 'closing_date')

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'title', 'url', 'local_url', 'mimetype')

admin.site.register(Vacancy, VacancyAdmin)
admin.site.register(Document, DocumentAdmin)