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

def ergaenzen(jg=5, stufe=3, typ_anf=0, typ_end=0, optionen="", init=False):
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

def addieren(jg=5, stufe=3, typ_anf=0, typ_end=0, optionen="", init=False):
    if init==True:
        typ_anf=1
        typ_end=1
        if jg>=7:
            typ_end=2
        else:
            if "mit" in optionen:
                typ_end=2
        return typ_anf, typ_end
    else:
        typ=1 
        if typ_end>1:
            typ=random.randint(typ_anf, typ_end+1)
        if typ==1:
                zahl1=random.randint(5, 45)
                zahl2=random.randint(5, 45)
        else:
                rund1 = random.randint(0,2)
                zahl1 = random.randint(5, 225)
                zahl1=zahl1/10**rund1
                rund2 = random.randint(0,2)
                zahl2 = random.randint(5, 225)
                zahl2=zahl2/10**rund2
        return typ, zahl1, zahl2, zahl1+zahl2

def subtrahieren(jg=5, stufe=3, typ_anf=0, typ_end=0, optionen="", init=False):
    if init==True:
        typ_anf=1
        typ_end=1
        if jg>=7:
            typ_end=2
        else:
            if "mit" in optionen:
                typ_end=2
        return typ_anf, typ_end
    else:
        typ=1 
        if typ_end>1:
            typ=random.randint(typ_anf, typ_end+1)
        if typ==1:
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
    return typ, zahl1, zahl2, result

AUFGABEN = {
    1: ergaenzen,
    2: addieren,
    3: subtrahieren,
}

def aufgaben(modul_id, jg=5, stufe=3, typ_anf=0, typ_end=0, optionen="", init=False):
    return AUFGABEN[modul_id](jg, stufe, typ_anf, typ_end, optionen, init)

def kontrolle(given, right):
    return given == right 

def kontrolle_zahll(given, right):
    return abs(given - right) < decimal.Decimal('0.001')

def get_fake_user():
    #return Schueler.objects.all().order_by('?').first()
    return Schueler.objects.all().first()

def kategorien(req):
    Protokoll.objects.filter(tries=0).delete()
    modul = Kategorie.objects.all().order_by('zeile')
    return render(req, 'core/kategorien.html', {'module': modul})

def uebersicht(req):
    user=get_fake_user()
    uebersicht = Zaehler.objects.filter(user=user).order_by('kategorie__zeile')
    #modul = Kategorie.objects.all()
    return render(req, 'core/uebersicht.html', {'uebersicht': uebersicht, 'user':user})

def protokoll(req):
    protokoll = Protokoll.objects.all().order_by('id').reverse()
    user=get_fake_user()    
    return render(req, 'core/protokoll.html', {'protokoll': protokoll})

def details(req, zeile_id):
    protokoll = get_object_or_404(Protokoll, pk=zeile_id)
    zaehler = Zaehler.objects.get(user=protokoll.user, kategorie=protokoll.kategorie)
    frage = Frage.objects.get(pk=protokoll.frage)
    return render(req, 'core/details.html', {'protokoll': protokoll, 'zaehler': zaehler, 'frage':frage,})

def main(req, slug):
    modul = get_object_or_404(Kategorie, slug=slug)
    user=get_fake_user()    
    zaehler = get_object_or_404(Zaehler, kategorie=modul, user=user)
    if req.method == 'POST':
        protokoll = Protokoll.objects.get(pk=req.session.get('eingabe_id'))
        protokoll.tries += 1
        zaehler=Zaehler.objects.get(pk=req.session.get('zaehler_id'))
        frage = get_object_or_404(Frage, pk=protokoll.frage)
        form = AufgabeFormZahl(req.POST)
        right=protokoll.value
        if form.is_valid():
            eingabe=form.cleaned_data['eingabe']
            print(protokoll.tries)
            if protokoll.tries==1:
                protokoll.eingabe=eingabe
            elif protokoll.tries==2:
                protokoll.eingabe=f"(1:) {protokoll.eingabe} (2:) {eingabe}"
            else:
                protokoll.eingabe=f"{protokoll.eingabe} (3:) {eingabe}"
            protokoll.save()
            if kontrolle(eingabe, right):
                richtig(protokoll.id, zaehler.id)
                quote=int(zaehler.falsch/(zaehler.richtig+zaehler.falsch)*100)
                msg=f'richtig: {zaehler.richtig}, falsch: {zaehler.falsch}, Fehlerquote: {quote}%'
                messages.info(req, f'Richtig! Versuche: {protokoll.tries}, {msg}')
                return redirect('main', slug)
            else:
                falsch(protokoll.id, zaehler.id)
                quote=int(zaehler.falsch/(zaehler.richtig+zaehler.falsch)*100)
                msg=f'falsch: {zaehler.richtig}, falsch: {zaehler.falsch}, Fehlerquote: {quote}%'
                messages.info(req, f'Leider falsch! Versuche: {protokoll.tries}, {msg}')        
                text = protokoll.text
                if protokoll.tries>=3:
                    return redirect('kategorien')
                    
    else:
        frage = Frage.objects.filter(kategorie=modul).order_by('?').first()
        frage_id=frage.id
        form = AufgabeFormZahl()
        user=get_fake_user()
        if zaehler.optionen=="":
            return redirect('optionen', slug)
        typ, zahl1, zahl2, result =aufgaben(modul.id, typ_anf=zaehler.typ_anf, typ_end=zaehler.typ_end, init=False) 
        text = frage.aufgabe.format(zahl1=zahl1, zahl2=zahl2)
        protokoll = Protokoll.objects.create(
            user=user, kategorie=modul, text=text, value=result, loesung=str(result)         
        )
        req.session['eingabe_id'] = protokoll.id    
        req.session['zaehler_id'] = zaehler.id   
        if zaehler.aufgnr==0:
            zaehler.aufgnr=1
        zaehler.save()        
        protokoll.typ=typ
        protokoll.frage=frage_id
        protokoll.aufgnr=zaehler.aufgnr
        if frage.protokolltext=="":
            protokoll.text = protokoll.text
        else:
            protokoll.text=protokoll.aufgabe
        protokoll.save()  
    context = dict(kategorie=modul, aufgnr=zaehler.aufgnr, text=text, aufgabe=main, form=form, zaehler_id=zaehler.id,)
    return render(req, 'core/aufgabe.html', context)

def optionen(req, slug):
    kategorie = get_object_or_404(Kategorie, slug=slug)
    form = AuswahlForm(kategorie=kategorie)
    user=get_fake_user()   
    zaehler = get_object_or_404(Zaehler, kategorie=kategorie, user=user)
    if req.method == 'POST':
        form = AuswahlForm(req.POST, kategorie=kategorie)
        if form.is_valid():
            optionen = ';'.join(map(str, form.cleaned_data['optionen']))
            if optionen=="":
                optionen="keine"
        else:
            optionen="keine"  
    else:
        auswahl=kategorie.auswahl_set.all().count()
        if auswahl>0:
            return render(req, 'core/optionen.html', {'kategorie': kategorie, 'auswahl_form':form})
        else:
            optionen="keine"
    zaehler.optionen=optionen        
    zaehler.save()
    typ_anf, typ_end = aufgaben(kategorie.id, jg=user.jahrgang, stufe=user.stufe, optionen=zaehler.optionen, init=True)
    zaehler.typ_anf=typ_anf
    zaehler.typ_end=typ_end
    zaehler.save()
    return redirect('main', slug)

def abbrechen(req, zaehler_id):
    zaehler = get_object_or_404(Zaehler, pk=zaehler_id)
    zaehler.aufgnr=0
    zaehler.optionen=""
    zaehler.abbrechen =zaehler.abbrechen+1
    zaehler.richtig_of =0 
    zaehler.save() 
    return redirect('kategorien')

def richtig(protokoll_id, zaehler_id):
    protokoll = Protokoll.objects.get(pk=protokoll_id)
    zaehler = Zaehler.objects.get(pk=zaehler_id)
    #protokoll.tries += 1
    protokoll.bearbeitungszeit=(timezone.now() - protokoll.start).total_seconds()
    protokoll.wertung="richtig"
    protokoll.save()
    zaehler.richtig +=1
    zaehler.richtig_of +=1
    zaehler.aufgnr +=1
    zaehler.save()
    if zaehler.aufgnr>10:
        zaehler.aufgnr=0
        zaehler.optionen=""
        zaehler.save()
        return redirect('kategorien')
    
def falsch(protokoll_id, zaehler_id):
    protokoll = Protokoll.objects.get(pk=protokoll_id)
    zaehler = Zaehler.objects.get(pk=zaehler_id)
    #protokoll.tries += 1
    protokoll.bearbeitungszeit=(timezone.now() - protokoll.start).total_seconds()
    protokoll.wertung="f"
    protokoll.save()
    zaehler.falsch +=1
    zaehler.richtig_of =0
    zaehler.save()
   
