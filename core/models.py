from django.contrib.auth.models import User
from django.db import models

from django import forms
from django.db.models import IntegerField
from django.utils.text import slugify

#from django.contrib.postgres.fields import ArrayField
#from django.core import validators
#from django.core.validators import MinValueValidator, MaxValueValidator

class Kategorie(models.Model):
    gruppe = models.CharField(max_length=1, blank=True)             #Untergruppe A, B, C, D, E um die Ansicht übersichtlicher gestalten zu können
    zeile = models.PositiveSmallIntegerField(default=0)             # entspricht der Aufgabengruppe (1 bis 35)
    name = models.CharField(max_length=20)

    slug=models.SlugField(default="", null=False)

    start_Jg = models.PositiveSmallIntegerField(default=5, verbose_name="Start in Jahrgang")
    start_SW = models.PositiveSmallIntegerField(default=1, verbose_name="Start in Schulwoche")

    eof = models.PositiveSmallIntegerField(default=25, verbose_name="Eingaben ohne Fehler")  # Aufgaben die an einem Stück richtig beantwortet werden müssen damit der Fehlerzähler zurückgesetzt wird

    def __str__(self):
        return f"({self.name})"

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'

class Frage(models.Model):
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE, related_name="Fragen")
    typA = models.PositiveSmallIntegerField(default=0)
    typB = models.PositiveSmallIntegerField(default=0)
    anz = models.PositiveSmallIntegerField(default=10, verbose_name="Anzahl Aufgaben")      #Aufgaben die am Stück gerechnet werden müssen

    text = models.CharField(max_length=40)
    aufgabe = models.CharField(max_length=20)
    protokolltext = models.CharField(max_length=20)

    anmerkung = models.CharField(max_length=20)
    grafik = models.IntegerField(default=0)  # gehört eine Grafik zur Aufgabe?

    hilfe1 = models.CharField(max_length=25)
    hilfe2 = models.CharField(max_length=25)

    ergebnis = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    loesung = models.CharField(max_length=100)

    def __str__(self):
        return f"({self.text})"

    class Meta:
        verbose_name = 'Frage'
        verbose_name_plural = 'Fragen'

class Schueler(models.Model):
    nachname = models.CharField(max_length=20)
    vorname = models.CharField(max_length=20)
    klasse = models.CharField(max_length=10)
    jahrgang = models.PositiveSmallIntegerField(default=0)
    kurs = models.CharField(max_length=1, default="E")
    kurs_i = models.BooleanField(default=False, verbose_name="Förderkind", editable=False)
    kurs_E = models.BooleanField(default=True, verbose_name="E-Kurs", editable=False)

    # werden beim Erstellen eingestellt
    datum_start = models.DateField(auto_now_add=True, verbose_name="Startdatum", editable=False, )
    stufe = models.PositiveSmallIntegerField(default=0, editable=False)
    halbjahr = models.PositiveSmallIntegerField(default=0, editable=False)
    voreinst = models.IntegerField(default=1)                               #hier könnte, mithilf von Primzahlen, Voreinstellungen gesetzt und abgefragt werden

    zaehler_EoF = models.PositiveSmallIntegerField(default=0,  editable=False)  # je nach Einstellung LoeOF in Aufgaben wird der Fehlerzähler gelöscht
    zaehler_Fehler = models.PositiveSmallIntegerField(default=0,  editable=False)  # und hier wird dann, für jede Kategorie, der Zähler auf Null gesetzt

    def __str__(self):
        return f"({self.vorname} {self.nachname}, {self.klasse})"

    class Meta:
        verbose_name = 'Schüler'
        verbose_name_plural = 'Schüler'

class Daten(models.Model):
    schueler = models.ForeignKey(Schueler, on_delete=models.CASCADE, related_name="Daten")
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE, verbose_name="Kategorie", related_name="Daten")
    typ = models.CharField(max_length=5, blank=True )
    halbjahr = models.PositiveSmallIntegerField(default=0)

    text = models.CharField(max_length=30, blank=True, verbose_name="Aufgabentext")
    aufgabe = models.CharField(max_length=20, blank=True, verbose_name="Aufgaben")
    eingabe = models.CharField(max_length=20, blank=True, verbose_name="Eingabe")
    loesung = models.CharField(max_length=20, blank=True, verbose_name="Lösung")

    start = models.DateTimeField('Start', auto_now_add=True)
    ende = models.DateTimeField('Ende', blank=True, null=True, default=None)
    bearbeitungszeit=models.DateTimeField(blank=True, null=True, default=None)

    richtig = models.PositiveSmallIntegerField(default=0)
    zusatz = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    falsch = models.PositiveSmallIntegerField(default=0)

    zaehler_falsch = models.PositiveSmallIntegerField(default=0)

    abbrechen = models.PositiveSmallIntegerField(default=0)
    hilfe = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'Daten'
        verbose_name_plural = 'Daten'

    def __str__(self):
        return f"({self.aufgabe}={self.eingabe}?)"







class Category(models.Model):
    name = models.CharField('Name', max_length=100)
    description = models.TextField('Beschreibung', blank=True)
    hint = models.TextField('Hinweis', blank=True)
    slug=models.SlugField(default="", null=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name)
        super().save(*args, **kwargs)

class Result(models.Model):
    user = models.ForeignKey(User, verbose_name='Benutzer',
                             related_name='results', on_delete=models.CASCADE)
    value = models.DecimalField('Wert', max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, verbose_name='Kategorie', related_name='results',
        on_delete=models.CASCADE
    )
    text = models.TextField('Text')
    result_unit = models.CharField('Einheit Ergebnis', max_length=20,
                                   blank=True)
    tries = models.PositiveSmallIntegerField('Versuche', default=0)
    start = models.DateTimeField('Start', auto_now_add=True)
    end = models.DateTimeField('Ende', blank=True, null=True, default=None)

    def __str__(self):
        return f'Ergebnis {self.value:.2f}'

    @property
    def duration(self):
        if not self.end:
            return 0
        return (self.end - self.start).total_seconds()

class Question(models.Model):
    category = models.ForeignKey(
        Category, verbose_name='Kategorie', related_name='questions',
        on_delete=models.CASCADE
    )
    text = models.TextField('Text')

    def __str__(self):
        return self.text[:100]

