from django.contrib import admin
from .models import  Kategorie, Frage, Schueler, Protokoll, Zaehler

# Register your models here.

class KategorieAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Kategorie, KategorieAdmin)
admin.site.register(Frage)

admin.site.register(Schueler)

admin.site.register(Protokoll)
admin.site.register(Zaehler)

