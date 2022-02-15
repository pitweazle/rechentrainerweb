from django.contrib import admin

from .models import  Kategorie, Frage, Schueler, Daten
from .models import Category, Question, Result

# Register your models here.

class KategorieAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Kategorie, KategorieAdmin)
admin.site.register(Frage)

admin.site.register(Schueler)

admin.site.register(Daten)

admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Result)
