from django.contrib import admin

from .models import  Kategorie, Frage, Schueler, Daten
from .models import Category, Question, Result

# Register your models here.


admin.site.register(Kategorie)
admin.site.register(Frage)

admin.site.register(Schueler)

admin.site.register(Daten)

admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Result)
