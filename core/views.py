import decimal
import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from datetime import datetime

from .forms import AufgabeForm
from .models import Kategorie, Frage, Daten
from .models import Schueler
from django.http import HttpResponse, HttpResponseNotFound

NOTES = [5, 10, 20, 50, 100]


def make_task():
    low = random.uniform(0.1, 99.0)
    low = decimal.Decimal(round(low, 2))
    start = 0
    while True:
        if NOTES[start] > low:
            break
        start += 1
    high = decimal.Decimal(random.choice(NOTES[start:]))
    return low, high, high - low


def check_daten(given, right):
    return abs(given - right) < decimal.Decimal('0.001')

def get_fake_user():
    return Schueler.objects.all().first()

def index(req):
    Daten.objects.filter(tries=0).delete()
    modul = Kategorie.objects.all().order_by('id')
    return render(req, 'core/index.html', {'module': modul})

def protokoll(req):
    daten = Daten.objects.all().order_by('id').reverse()
    return render(req, 'core/protokoll.html', {'module': daten})

def antwort(req, antwort_id):
    antwort=Daten.objects.all()[antwort_id]
    return render(req, 'core/antwort.html', {'module': antwort})

    #return HttpResponse(antwort)


def aufgabe(req, modul_id):
    modul = get_object_or_404(Kategorie, pk=modul_id)
    if req.method == 'POST':
        form = AufgabeForm(req.POST)
        daten = Daten.objects.get(pk=req.session.get('eingabe_id'))
        #antwort = Daten.objects.get(pk=req.session.get('antwort_id'))
        daten.tries += 1
        if form.is_valid():
            if check_daten(form.cleaned_data['eingabe'], daten.value):
                daten.eingabe=form.cleaned_data['eingabe']
                daten.richtig=True
                daten.end = timezone.now()
                daten.save()
                min, sec = divmod(daten.duration, 60)
                msg = f'Zeit: {int(min)}min {int(sec)}s'
                messages.info(req, f'Richtig! Versuche: {daten.tries}, {msg}')
                return redirect('modul', modul_id)

        messages.info(req, 'Leider falsch.')
        daten.eingabe=form.cleaned_data['eingabe']
        daten.save()
        text = daten.text
    else:
        frage = Frage.objects.filter(
            kategorie=modul
        ).order_by('?').first()

        # 2 Zufallszahlen erzeugen und Ergebnis ausrechnen
        low, high, daten = make_task()

        text = frage.text.format(low=low, high=high)
        daten = Daten.objects.create(
            user=get_fake_user(), value=daten, kategorie=modul,
            text=text
        )
        req.session['eingabe_id'] = daten.id
        form = AufgabeForm()
    context = dict(category=modul, text=text, aufgabe=aufgabe, form=form)
    return render(req, 'core/aufgabe.html', context)
