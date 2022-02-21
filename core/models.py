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

class wahl_gruppe(models.TextChoices):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'

class Kategorie(models.Model):
    gruppe = models.CharField(max_length=1, choices=wahl_gruppe.choices, default=wahl_gruppe.A)

    #gruppe = models.CharField(max_length=1, blank=True, validators=[validate_letter])             #Untergruppe A, B, C, D, E um die Ansicht übersichtlicher gestalten zu können
    zeile = models.PositiveSmallIntegerField(default=0)             # entspricht der Aufgabengruppe (1 bis 35)
    name = models.CharField(max_length=20)

    slug=models.SlugField(default="", null=False)

    start_Jg = models.PositiveSmallIntegerField(default=5, verbose_name="Start in Jahrgang")
    start_SW = models.PositiveSmallIntegerField(default=1, verbose_name="Start in Schulwoche")

    eof = models.PositiveSmallIntegerField(default=25, verbose_name="Eingaben ohne Fehler")  # Aufgaben die an einem Stück richtig beantwortet werden müssen damit der Fehlerzähler zurückgesetzt wird

    def save(self, *args, **kwargs):
        self.slug=slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'

class Frage(models.Model):
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE, related_name="fragen")
    typA = models.PositiveSmallIntegerField(default=0)
    typB = models.PositiveSmallIntegerField(default=0)

    text = models.TextField(blank=True)
    aufgabe = models.CharField(blank=True,max_length=20)
    protokolltext = models.CharField(blank=True,max_length=40)

    anmerkung = models.CharField(blank=True,max_length=50)
    grafik = models.IntegerField(default=0)  # gehört eine Grafik zur Aufgabe?

    hilfe1 = models.CharField(blank=True,max_length=50)
    hilfe2 = models.CharField(blank=True,max_length=50)

    ergebnis = models.DecimalField(max_digits=15, decimal_places=5, default=0)
    loesung = models.CharField(blank=True,max_length=100)

    def __str__(self):
        return f"({self.text} {self.aufgabe})"

    class Meta:
        verbose_name = 'Frage'
        verbose_name_plural = 'Fragen'

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
    jahrgang = models.PositiveSmallIntegerField(validators=[MinValueValidator(5), MaxValueValidator(10)])

    kurs= models.CharField(max_length=1, choices=wahl_kurs.choices, default=wahl_kurs.E_KURS,)

    kurs_i = models.BooleanField(default=False, verbose_name="Förderkind", editable=False)
    kurs_E = models.BooleanField(default=True, verbose_name="E-Kurs", editable=False)

    # werden beim Erstellen eingestellt
    datum_start = models.DateField(auto_now_add=True, verbose_name="Startdatum", editable=False, )
    stufe = models.PositiveSmallIntegerField(default=0, editable=False)
    halbjahr = models.PositiveSmallIntegerField(default=0, editable=False)
    voreinst = models.IntegerField(default=1, editable=False)                               #hier könnte, mithilf von Primzahlen, Voreinstellungen gesetzt und abgefragt werden

    def save(self, *args, **kwargs):
        if self.kurs == "i":
            self.kurs_i=True
        else:
            self.kurs_i=False

        if self.kurs in ("Y", "E", "R", "A", "B"):
            self.kurs_E=True
        else:
            self.kurs_E=False

        #self.klasse=int(self.klasse)
        #self.jahrgang=(self.klasse)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"({self.vorname} {self.nachname}, {self.klasse})"

    class Meta:
        verbose_name = 'Schüler'
        verbose_name_plural = 'Schüler'

class Daten(models.Model):
    schueler = models.ForeignKey(Schueler, on_delete=models.CASCADE, related_name="daten")
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE, verbose_name="Kategorie", related_name="daten")
    typ = models.CharField(max_length=5, blank=True )
    halbjahr = models.PositiveSmallIntegerField(default=0)

    text = models.TextField(blank=True)
    aufgabe = models.CharField(max_length=20, blank=True)
    protokolltext = models.CharField(max_length=20, blank=True)

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
        return f"({self.start} {self.schueler} {Kategorie})"


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
#    category = models.ForeignKey(
 #       Kategorie, verbose_name='Kategorie', related_name='results',
  #      on_delete=models.CASCADE
   # )
    text = models.TextField('Text')
    result_unit = models.CharField('Einheit Ergebnis', max_length=20,
                                   blank=True)
    tries = models.PositiveSmallIntegerField('Versuche', default=0)
    start = models.DateTimeField('Start', auto_now_add=True)
    end = models.DateTimeField('Ende', blank=True, null=True, default=None)

    def __str__(self):
        return (f"{self.user}, Aufgabe: {self.text}, Eingabe: {self.value:.2f}")

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

