from django.contrib import admin

from .models import  Kategorien, Fragen, Schulen, Lehrer,  Gruppen, Schueler, Daten
from .models import Category, Question, Result

# Register your models here.


admin.site.register(Kategorien)
admin.site.register(Fragen)

admin.site.register(Schulen)
admin.site.register(Lehrer)
admin.site.register(Schueler)
admin.site.register(Gruppen)

admin.site.register(Daten)

admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Result)
