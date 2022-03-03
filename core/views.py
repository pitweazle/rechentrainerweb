import decimal
import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from datetime import datetime

from .forms import AufgabeFormZahl, AufgabeFormStr
from .models import Kategorie, Frage, Protokoll
from .models import Schueler
from django.http import HttpResponse, HttpResponseNotFound



def ergaenzen():
    NOTES = [5, 10, 20, 50, 100]
    low = random.uniform(0.1, 99.0)
    low = decimal.Decimal(round(low, 2))
    start = 0
    while True:
        if NOTES[start] > low:
            break
        start += 1
    high = decimal.Decimal(random.choice(NOTES[start:]))
    result=high-low
    return low, high, result

def addition():
    low = random.uniform(0.1, 99.0)
    low = decimal.Decimal(round(low, 2))
    #low = round(low, 2)
    high = decimal.Decimal(round(low, 2))
    #high = (random.choice(NOTES[start:]))
    result=high+low
    return low, high, result

def subtraktion():
    zahl1 = random.uniform(0.1, 99.0)
    zahl1 = decimal.Decimal(round(zahl1, 2))
    #low = round(low, 2)
    zahl2 = random.uniform(0.1, 99.0)
    zahl2 = decimal.Decimal(round(zahl1, 2))
    #high = (random.choice(NOTES[start:]))
    result=zahl2
    return zahl1+zahl2, zahl1, result

AUFGABEN = {
    "ergaenzen": ergaenzen,
    "addition": addition,
    "subtraktion": subtraktion,
}

def make_zahl(modul_id):
    NOTES = [5, 10, 20, 50, 100]
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
    NOTES = [5, 10, 20, 50, 100]
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
    result_str=str(high-low)
    return low_str, high_str, result_str

def check_str(given, right):
    print(given + right)
    print(given==right)

    return given == right 

def check_zahl(given, right):
    return abs(given - right) < decimal.Decimal('0.001')

def get_fake_user():
    return Schueler.objects.all().first()

def index(req):
#    Protokoll.objects.filter(tries=0).delete()
    modul = Kategorie.objects.all().order_by('id')
    return render(req, 'core/index.html', {'module': modul})

def protokoll(req):
    protokoll = Protokoll.objects.all().order_by('id').reverse()
    return render(req, 'core/protokoll.html', {'module': protokoll})

def antwort(req, antwort_id):
    antwort=Protokoll.objects.all()[antwort_id]
    return render(req, 'core/antwort.html', {'module': antwort})

    #return HttpResponse(antwort)


def aufgabe(req, modul_id):
    modul = get_object_or_404(Kategorie, pk=modul_id)
    if req.method == 'POST':
        protokoll = Protokoll.objects.get(pk=req.session.get('eingabe_id'))
        protokoll.tries += 1
        form = AufgabeFormZahl(req.POST)
        right=protokoll.value
        if form.is_valid():
            if check_str(form.cleaned_data['eingabe'], right):
                protokoll.eingabe=form.cleaned_data['eingabe']
                protokoll.richtig=True
                #protokoll.end = timezone.now()
                protokoll.bearbeitungszeit=(timezone.now() - protokoll.start).total_seconds()
                protokoll.save()
                min, sec = divmod(protokoll.bearbeitungszeit, 60)
                msg = f'Zeit: {int(min)}min {int(sec)}s'
                messages.info(req, f'Richtig! Versuche: {protokoll.tries}, {msg}')
                return redirect('modul', modul_id)
        messages.info(req, 'Leider falsch.')
        protokoll.eingabe=form.cleaned_data['eingabe']
        protokoll.save()
        text = protokoll.text
    else:
        frage = Frage.objects.filter(
            kategorie=modul
        ).order_by('?').first()
        form = AufgabeFormZahl()
        low, high, result = make_zahl(modul_id)
        text = frage.text.format(low=low, high=high)

        protokoll = Protokoll.objects.create(
            user=get_fake_user(), kategorie=modul, text=text, value=result, loesung=str(result)         
        )
        req.session['eingabe_id'] = protokoll.id
    context = dict(category=modul, text=text, aufgabe=aufgabe, form=form)
    return render(req, 'core/aufgabe.html', context)
