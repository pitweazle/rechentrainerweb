import decimal
import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from datetime import datetime

from .forms import AufgabeFormZahl, AufgabeFormStr
from .models import Kategorie, Frage, Daten
from .models import Schueler
from django.http import HttpResponse, HttpResponseNotFound

NOTES = [5, 10, 20, 50, 100]
def make_zahl(modul_id):
    print(modul_id)
    low = random.uniform(0.1, 99.0)
    low = decimal.Decimal(round(low, 2))
    #low = round(low, 2)
    start = 0
    while True:
        if NOTES[start] > low:
            break
        start += 1
    high = decimal.Decimal(random.choice(NOTES[start:]))
    #high = (random.choice(NOTES[start:]))
    if modul_id==2:
        result=high+low
    else:
        result=high-low
    return low, high, result

def make_str():
    low = random.uniform(0.1, 99.0)
    low = round(low, 2)
    low_str=str(low)
    start = 0
    while True:
        if NOTES[start] > low:
            break
        start += 1
    high = (random.choice(NOTES[start:]))
    high_str=str(high)
    return str(low), str(high), high - low


def check_str(given, right):
    print(given + right)
    print(given==right)

    return given == right 

def check_zahl(given, right):
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
    zahl=True
    if req.method == 'POST':
        daten = Daten.objects.get(pk=req.session.get('eingabe_id'))
        daten.tries += 1
        if zahl:
            form = AufgabeFormZahl(req.POST)
            right=daten.value
        else:
            form = AufgabeFormStr(req.POST)
            right=daten.loesung
        if form.is_valid():
            if check_str(form.cleaned_data['eingabe'], right):
                daten.eingabe=form.cleaned_data['eingabe']
                daten.richtig=True
                #daten.end = timezone.now()
                daten.bearbeitungszeit=(timezone.now() - daten.start).total_seconds()
                daten.save()
                min, sec = divmod(daten.bearbeitungszeit, 60)
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
        if zahl:
            form = AufgabeFormZahl()
            # 2 Zufallszahlen erzeugen und Ergebnis ausrechnen
            low, high, result = make_zahl(modul_id)
        else:
            form = AufgabeFormStr()
            low, high, result = make_str()

        text = frage.text.format(low=low, high=high)
        daten = Daten.objects.create(
            user=get_fake_user(), value=result, loesung=str(result), kategorie=modul,
            text=text
        )
        req.session['eingabe_id'] = daten.id

    context = dict(category=modul, text=text, aufgabe=aufgabe, form=form)
    return render(req, 'core/aufgabe.html', context)
