from django import forms
from django.db import models

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

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

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    nachname = forms.CharField(max_length=20)
    vorname = forms.CharField(max_length=20)
   
    klasse = forms.CharField(max_length=10)
    #jg = forms.PositiveSmallIntegerField(validators=[MinValueValidator(5), MaxValueValidator(10)])
    jg=forms.IntegerField()    
    
    #kurs= forms.CharField(max_length=1, choices=wahl_kurs.choices, default=wahl_kurs.E_KURS,)
    
    stufe=forms.IntegerField()    

    class Meta:
        model = User
        fields = ["username", "nachname", "vorname", "klasse", "email", "password1", "password2", ]