from sched import scheduler
from django.contrib.auth.models import User
from django.db import models

from django import forms
from django.db.models import IntegerField
from django.utils.text import slugify
#from django.core.exceptions import ValidationError

#from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Kategorie(models.Model):
    zeile = models.PositiveSmallIntegerField(default=0, unique=True)             # entspricht der Aufgabengruppe (1 bis 35)
    name = models.CharField(max_length=20)

    slug=models.SlugField(default="", null=False)

    start_jg = models.PositiveSmallIntegerField(default=5, verbose_name="Start in Jahrgang")
    start_sw = models.PositiveSmallIntegerField(default=1, verbose_name="Start in Schulwoche")

    eof = models.PositiveSmallIntegerField(default=25, verbose_name="Eingaben ohne Fehler")  # Aufgaben die an einem Stück richtig beantwortet werden müssen damit der Fehlerzähler zurückgesetzt wird

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'

class Auswahl(models.Model):
    kategorie = models.ForeignKey(Kategorie, null=True, on_delete=models.CASCADE)
    text = models.CharField(max_length=80, verbose_name="Text")
    bis_stufe = models.IntegerField(default=0, verbose_name="bis Stufe (ex):")
    bis_jg = models.IntegerField(default=0, verbose_name="bis Jahrgang:")

    def __str__(self):
        return self.text 

    class Meta:
        verbose_name = 'Auswahl'
        verbose_name_plural = 'Auswahl'

class wahl_kurs(models.TextChoices):
    GYMNASIUM = 'Y', 'Gymnasium'
    REALSCHULE = 'R', 'Realschule'
    HAUPTSCHULE = 'H', 'Hauptschule'
    E_KURS = 'E', 'E-Kurs'
    G_KURS = 'G', 'G-Kurs'
    A_KURS = 'A', 'A-Kurs'
    B_KURS = 'B', 'B-Kurs'
    C_KURS = 'C', 'C-Kurs'
    FOERDER = 'i', 'Förderschüler'

class Schueler(models.Model):
    nachname = models.CharField(max_length=20)
    vorname = models.CharField(max_length=20)
    
    klasse = models.CharField(max_length=10)
    jg = models.PositiveSmallIntegerField(validators=[MinValueValidator(5), MaxValueValidator(10)])

    kurs= models.CharField(max_length=1, choices=wahl_kurs.choices, default=wahl_kurs.E_KURS,)

    #rating_kurs=models.BooleanField(default=True)
    #rating_schule=models.BooleanField(default=True)
    #rating_gesamt=models.BooleanField(default=True)

    # werden beim Erstellen eingestellt
    datum_start = models.DateField(auto_now_add=True, verbose_name="Startdatum", editable=False, )
    stufe = models.PositiveSmallIntegerField(default=0) #, editable=False)
    e_kurs = models.BooleanField(default=True)
    halbjahr = models.PositiveSmallIntegerField(default=0, editable=False)
    voreinst = models.IntegerField(default=1, editable=False)                               #hier könnte, mithilf von Primzahlen, Voreinstellungen gesetzt und abgefragt werden

    def __str__(self):
        return f"({self.vorname} {self.nachname}, {self.klasse})"

    class Meta:
        verbose_name = 'Schüler'
        verbose_name_plural = 'Schüler'

class Protokoll(models.Model):
    user = models.ForeignKey(Schueler, verbose_name='Benutzer', related_name='protokolle', on_delete=models.CASCADE)
    #gewertet werden nur die Aufgaben des jeweiligen Schuljabjahres, im Januar, Juni und August, kann der user aber auch schon festlegen, dass die Aufgaben für das nächste Schulhalbjahr gelten:
    halbjahr = models.PositiveSmallIntegerField(default=0)

    kategorie = models.ForeignKey(Kategorie, verbose_name='Kategorie', related_name='protokolle', on_delete=models.CASCADE)
    typ = models.CharField(max_length=20, blank=True)
     
    aufgnr = models.PositiveSmallIntegerField(default=0) 
    
    #der Aufgabentext:
    text = models.TextField(blank=True)
    pro_text = models.CharField(max_length=25, blank=True)
    grafik = models.CharField(max_length=400, blank=True)

    #hier speichere ich die Lösung, wahlweise als zahl, u.U. auch (mehrere) Lösungen als String:
    value = models.DecimalField('Wert', max_digits=20, decimal_places=7)
    loesung = models.CharField(max_length=20, blank=True, verbose_name="Lösung")
    hilfe = models.TextField(blank=True)
    
    #die Eingabe des users:
    eingabe = models.CharField(max_length=20, blank=True, verbose_name="Eingabe")

    tries = models.PositiveSmallIntegerField('Versuche', default=0)
    #Eintrag richtig, falsch, Extrapunkte, Lösung anzeigen, Abbruch:
    wertung = models.CharField(max_length=10, blank=True, verbose_name="Wertung")

    start = models.DateTimeField('Start', auto_now_add=True)
    bearbeitungszeit=models.FloatField(default=0)

    class Meta:
        verbose_name = 'Protokoll'
        verbose_name_plural = 'Protokoll'

class Zaehler(models.Model):
    user = models.ForeignKey(Schueler, verbose_name='Benutzer', related_name='zaehler', on_delete=models.CASCADE)    
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE, related_name="zaehler")
    
    optionen_text=models.CharField(max_length=40, blank=True, default="", verbose_name="Optionen")
    
    typ_anf = models.SmallIntegerField(default=0)        
    typ_end = models.SmallIntegerField(default=0)    

    aufgnr = models.PositiveSmallIntegerField(default=0)  

    richtig = models.PositiveSmallIntegerField(default=0)    
    Extrapunkte = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    richtig_of = models.PositiveSmallIntegerField(default=0)   
    bearbeitungszeit = models.FloatField(default=0)     

    falsch = models.PositiveSmallIntegerField(default=0)    
    loesung = models.PositiveSmallIntegerField(default=0)    
    abbrechen = models.PositiveSmallIntegerField(default=0)    
    hilfe = models.PositiveSmallIntegerField(default=0) 
    
    hinweis = models.CharField(max_length=40, blank=True, verbose_name="Lösung/Hilfe")

    def __str__(self):
        return f"({self.user}, {self.kategorie}, {self.aufgnr})"
    
    def quote(self):
        gesamt = self.richtig + self.falsch
        return self.falsch / gesamt *100 if gesamt else 0

    class Meta:
        verbose_name = 'Zähler'
        verbose_name_plural = 'Zähler'   
