from django.contrib import admin
from .models import  Kategorie, Auswahl, Frage, Schueler, Protokoll, Zaehler

# Register your models here.

#class KategorieAdmin(admin.ModelAdmin):
#    prepopulated_fields = {"slug": ("name",)}

class AuswahlInline(admin.TabularInline):
    model = Auswahl
    extra = 0

class KategorieAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,   {'fields': ['gruppe', 'name', 'zeile', 'start_jg', 'start_sw']}),
                ('weitere Infos', {'fields': ['eof'], 'classes': ['collapse']}),        
    ]
    inlines = [AuswahlInline]
    
class ZaehlerAdmin(admin.ModelAdmin):
    list_filter=("user","kategorie",)
    
class ProtokollAdmin(admin.ModelAdmin):
    list_filter=("user",)

admin.site.register(Kategorie, KategorieAdmin)
#admin.site.register(Auswahl)
admin.site.register(Frage)

admin.site.register(Schueler)

admin.site.register(Protokoll, ProtokollAdmin)
admin.site.register(Zaehler, ZaehlerAdmin)

