import decimal
import random
from token import NOTEQUAL

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from datetime import datetime

from .forms import AufgabeFormZahl, AufgabeFormStr
from .forms import AuswahlForm
from .models import Kategorie, Frage, Protokoll, Zaehler
from .models import Schueler
from .models import Auswahl
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

def addieren(jg, stufe):
    if jg==5:
        zahl1=random.randint(5, 45)
        zahl2=random.randint(5, 45)
    else:
        rund1 = random.randint(0,2)
        zahl1 = random.randint(5, 225)
        zahl1=zahl1/10**rund1
        rund2 = random.randint(0,2)
        zahl2 = random.randint(5, 225)
        zahl2=zahl2/10**rund2
    return zahl1, zahl2, zahl1+zahl2

def subtrahieren(jg, stufe):
    if jg==5:
        zahl2=random.randint(1, 99)
        result=random.randint(1, 49)
        zahl1=result+zahl2
    else:
        rund1 = random.randint(0,2)
        zahl2 = random.randint(1, 99)
        zahl2=zahl2/10**rund1
        rund2 = random.randint(0,2)
        result = random.randint(1, 99)
        result=result/10**rund2
        zahl1=zahl2+result
        zahl1=round(zahl1,(max(rund1, rund2)))
    return zahl1, zahl2, result

AUFGABEN = {
    1: ergaenzen,
    2: addieren,
    3: subtrahieren,
}

def aufgabenstellung(modul_id, jg):
    return AUFGABEN[modul_id](jg, 3)

def kontrolle(given, right):
    return given == right 

def kontrolle_zahll(given, right):
    return abs(given - right) < decimal.Decimal('0.001')

def get_fake_user():
    #return Schueler.objects.all().order_by('?').first()
    return Schueler.objects.all().first()


def aufgabe(req, modul_id):
    modul = get_object_or_404(Kategorie, pk=modul_id)
    if req.method == 'POST':
        protokoll = Protokoll.objects.get(pk=req.session.get('eingabe_id'))
        protokoll.tries += 1

        zaehler=Zaehler.objects.get(pk=req.session.get('zaehler_id'))
        form = AufgabeFormZahl(req.POST)
        right=protokoll.value
        if form.is_valid():
            if kontrolle(form.cleaned_data['eingabe'], right):
                protokoll.eingabe=form.cleaned_data['eingabe']
                protokoll.bearbeitungszeit=(timezone.now() - protokoll.start).total_seconds()
                protokoll.wertung="richtig"
                protokoll.save()
                zaehler.aufgnr +=1
                zaehler.richtig +=1
                zaehler.richtig_of +=1
                zaehler.save()
                min, sec = divmod(protokoll.bearbeitungszeit, 60)
                msg = f'Zeit: {int(min)}min {int(sec)}s'
                messages.info(req, f'Richtig! Versuche: {protokoll.tries}, {msg}')
                if zaehler.aufgnr>=3:
                    zaehler.aufgnr=1
                    zaehler.save()
                    return redirect('index')
                else:
                    return redirect('aufgabe', modul_id)
        messages.info(req, 'Leider falsch.')
        protokoll.eingabe=form.cleaned_data['eingabe']
        protokoll.wertung="f"
        protokoll.save()
        zaehler.falsch +=1
        zaehler.richtig_of =0
        zaehler.save()
        text = protokoll.text
        if protokoll.tries>=3:
            return redirect('index')
    else:
        frage = Frage.objects.filter(
            kategorie=modul
        ).order_by('?').first()
        form = AufgabeFormZahl()
        user=get_fake_user()
        zahl1, zahl2, result =aufgabenstellung(modul_id, user.jahrgang) 
        text = frage.aufgabe.format(zahl1=zahl1, zahl2=zahl2)
        protokoll = Protokoll.objects.create(
            user=user, kategorie=modul, text=text, value=result, loesung=str(result)         
        )
        req.session['eingabe_id'] = protokoll.id    
        zaehler, created = Zaehler.objects.get_or_create(
            user=user,
            kategorie=modul,            
        )
        req.session['zaehler_id'] = zaehler.id       
    context = dict(category=modul, aufgnr=zaehler.aufgnr, text=text, aufgabe=aufgabe, form=form)
    return render(req, 'core/aufgabe.html', context)

def index(req):
    Protokoll.objects.filter(tries=0).delete()
    modul = Kategorie.objects.all().order_by('id')
    return render(req, 'core/index.html', {'module': modul})

def protokoll(req):
    protokoll = Protokoll.objects.all().order_by('id').reverse()
    return render(req, 'core/protokoll.html', {'protokoll': protokoll})

def details(req, zeile_id):
    protokoll = get_object_or_404(Protokoll, pk=zeile_id)
    zaehler = Zaehler.objects.get(user=protokoll.user, kategorie=protokoll.kategorie)
    return render(req, 'core/details.html', {'protokoll': protokoll, 'zaehler': zaehler})

#def auswahl(req, kategorie_id):
def auswahl(req):
    if req.method=='POST':
        filled_form=AuswahlForm(req.POST)
        if filled_form.is_valid():
            note="OK! Du willst %s rechnen" %(filled_form.cleaned_data['auswahl'])
            return HttpResponse(note)
            new_form=AuswahlForm()
            return render(req, 'core/auswahl.html', {'auswahl':new_form, 'note':note})
    else:
        form=AuswahlForm()
        return render(req, 'core/auswahl.html', {'auswahl':form})

    # kategorie = get_object_or_404(Kategorie, pk=kategorie_id)
    # if (kategorie.auswahl_set.all().count())>0:
    #     user=get_fake_user()
    #     return render(req, 'core/auswahl.html', {'kategorie': kategorie})
    # else:
    #     return HttpResponse("keine Optionen")

def wahl(request, kategorie_id):
    return HttpResponse(kategorie_id)
    #kategorie = get_object_or_404(Kategorie, pk=kategorie_id)
    #selected_choice = kategorie.auswahl_set.get(pk=request.POST['wahl'])
