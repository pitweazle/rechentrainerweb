import decimal
import random
from token import NOTEQUAL
from unittest.util import strclass

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from datetime import datetime

from .forms import AufgabeFormZahl, AufgabeFormStr
from .forms import AuswahlForm

from .models import Kategorie, Protokoll, Zaehler
from .models import Schueler
from .models import Auswahl

from django.http import HttpResponse, HttpResponseNotFound

def format_number(value, precision=2, trailing_zeros=True):
    text = f"{value:.{precision}f}".replace(".", ",")
    return text.rstrip(",0") if not trailing_zeros and "," in text else text

def ergaenzen(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 1 
        typ_end = 3
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ = 5 + stufe%2                               #6 für E-Kurs
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)        
        if typ == 1 :                                        #Wechselgeld
            NOTES = [2, 5, 10, 20, 50, 100]
            zahl1 = random.randint(5, 5950)/100
            start = 0
            while True:
                if NOTES[start] > zahl1:
                    break
                start += 1
            zahl2 = (random.choice(NOTES[start:]))
            if zahl2 != 2:
                art = "Schein"
            else:
                art = "Stück"
            text = (
                f"Du hast für {format_number(zahl1,2)}€ eingekauft und"
                f" bezahlst mit einem {format_number(zahl2,0)}€ {art}."
                f"<br> Wieviel Wechselgeld erhälst du?")  
            pro_text = (
                f"Wechselgeld: {format_number(zahl2,0)}€"
                f"- {format_number(zahl1,2,True)}€")
            lsg = f"{format_number(zahl2-zahl1)}€"
            typ = "(Wechselgeld)"
        elif typ <= 3:                                               #ganze Zahlen
            exp = random.randint(2,4)
            zahl2 = 10**exp
            zahl1 = random.randint(1,zahl2-1)
            text = pro_text = f"ergänze {zahl1} zu {zahl2}"
            lsg = str(zahl2 - zahl1)
        else:                                                       #Zahlen kleiner 0
            if typ == 4:
                exp = random.randint(0, 2)
                zahl2 = 10**(-1*exp)
                zahl1 = random.randint(1,9)*zahl2/10
                exp2 = 1
            else:
                exp = random.randint(0, 1)
                zahl2 = 10**(-1*exp)
                zahl1 = random.randint(1,99)*zahl2/100
                exp2 = 2
            text = pro_text(
                f"ergänze {format_number(zahl1, exp+exp2,)}"
                f" zu {format_number(zahl2, exp)}")
            lsg = f"{format_number(zahl2-zahl1,exp+exp2)}"
        return typ, text, pro_text, lsg,  zahl2-zahl1

def addieren(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 2
        return typ_anf, typ_end
    else:
        faktor = stufe%2+1                                  #2 für E-Kurs, 1 für G-Kurs und i
        if typ_end>1:
            typ = random.randint(typ_anf, typ_end+1)
    # hier wird die Aufgabe erstellt:
        if typ == 1:
                zahl1 = random.randint(5, faktor*45)
                zahl2 = random.randint(5, faktor*45)
                text = pro_text = (str(zahl1)) + " + " + (str(zahl2)) 
                lsg = str(zahl1 + zahl2)
        else:
                rund1 = random.randint(0,faktor)
                zahl1 = random.randint(5,faktor*112)
                zahl1 = zahl1/10**rund1
                rund2 = random.randint(0,faktor)
                zahl2 = random.randint(5, faktor*112)
                zahl2 = zahl2/10**rund2
                text = pro_text = (
                    f"{format_number(zahl1,rund1)} + {format_number(zahl2,rund2)}") 
                lsg = f"{format_number(zahl1+zahl2,max(rund1,rund2))}"
        return typ, text, pro_text, lsg, zahl1+zahl2

def subtrahieren(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 2
        return typ_anf, typ_end
    else:
        faktor = stufe%2+1                                  #2 für E-Kurs, 1 für G-Kurs und i
        if typ_end>1:
            typ = random.randint(typ_anf, typ_end+1)
    # hier wird die Aufgabe erstellt:
        if typ == 0:
            zahl2 = random.randint(1, 99)
            result = random.randint(1, 49)
            zahl1 = result+zahl2
            text = pro_text = (str(zahl1)) + " - " + (str(zahl2)) 
            lsg = str(zahl1 + zahl2)
        else:
            rund1 = random.randint(0,1)
            zahl2 = random.randint(1, 99)
            zahl2 = zahl2/10**rund1
            rund2 = random.randint(0,1)
            result = random.randint(1, 99)
            result = result/10**rund2
            zahl1 = zahl2+result
            text = pro_text = f"{format_number(zahl1,max(rund1,rund2),False)} - {format_number(zahl2,rund1,False)}"
            lsg =   f"{format_number(result,max(rund1,rund2),False)}"          
    return typ, text, pro_text, lsg, result

def verdoppeln(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    pass
	# if aControl.state=0 then
	# 	typ=vonbis (0, 4)
   	# 	if typ < 4 then		
	# 		zahl1=vonbis (6, 60)
	# 	else
	# 		zahl1=vonbis (2, 30)
	# 	endif	
	# else
	# 	do 	
	# 		typ=vonbis (-2, 2)				
	# 		zahl2=vonbis (4, 60)
	# 		zahl1=zahl2*10^typ
	# 	loop while (zahl1 mod 10=0)			
	# endif
	# if typ<4 then
   	# 	Titel="Verdoppeln"      	
    #        Aufgabe="Was ist das Doppelte von " & format(zahl1,"0.###")
    #        gleich="?"
    #        erg=zahl1*2
    #        Loesung="2 mal " & format(zahl1,"0.###") & " ist " & erg
    #        Hilfe1="Verdoppeln muss man im Schlaf können!" 
    #     else
    #        Titel="Mal 4" 
    #        Aufgabe="4 mal " & format(zahl1,"0.###")
    #        gleich="="
    #        erg=zahl1*4
    #        Loesung="4 mal " & format(zahl1,"0.###") & "=" & erg
    #        Hilfe1="Hier musst du zweimal nacheinander verdoppeln!"
	# endif

AUFGABEN = {
    1: ergaenzen,
    2: addieren,
    3: subtrahieren,
    4: verdoppeln,
}

def aufgaben(kategorie_id, jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    return AUFGABEN[kategorie_id](jg, stufe, typ_anf, typ_end, optionen)

def kontrolle(given, right):
    return given == right 

def kontrolle_zahll(given, right):
    return abs(given - right) < decimal.Decimal('0.001')

def get_fake_user():
    #return Schueler.objects.all().order_by('?').first()
    return Schueler.objects.all().first()

def kategorien(req):
    Protokoll.objects.filter(eingabe = "").delete()
    kategorie = Kategorie.objects.all().order_by('zeile')
    return render(req, 'core/kategorien.html', {'kategorie': kategorie})

def uebersicht(req):
    user = get_fake_user()
    kategorien = []
    for kategorie in Kategorie.objects.all():
        zaehler = Zaehler.objects.filter(user=user, kategorie=kategorie).first()
        kategorien.append((kategorie, zaehler))
    return render(req, 'core/uebersicht.html', {'kategorien': kategorien, 'user':user})

def protokoll(req):
    protokoll = Protokoll.objects.all().order_by('id').reverse()
    user = get_fake_user()    
    return render(req, 'core/protokoll.html', {'protokoll': protokoll})

def details(req, zeile_id):
    protokoll = get_object_or_404(Protokoll, pk = zeile_id)
    zaehler = Zaehler.objects.get(user = protokoll.user, kategorie = protokoll.kategorie)
    #frage = Frage.objects.get(pk = protokoll.frage_id)
    return render(req, 'core/details.html', {'protokoll': protokoll, 'zaehler': zaehler})

def main(req, slug):                                                        #hier läuft alles zusammen
    kategorie = get_object_or_404(Kategorie, slug = slug)
    kategorie_id = kategorie.id
    user = get_fake_user()    
    zaehler = get_object_or_404(Zaehler, kategorie = kategorie, user = user)
    if req.method == 'POST':       
        protokoll = Protokoll.objects.get(pk = req.session.get('eingabe_id'))
        protokoll.tries += 1
        zaehler = Zaehler.objects.get(pk = req.session.get('zaehler_id'))
        zaehler.hinweis = ""
        form = AufgabeFormZahl(req.POST)
        right = protokoll.value
        if form.is_valid():                                                 #Aufgabe beantwortet
            eingabe = form.cleaned_data['eingabe']
            if protokoll.tries == 1:
                protokoll.eingabe = eingabe
            elif protokoll.tries == 2:
                protokoll.eingabe = f"(1:) {protokoll.eingabe} (2:) {eingabe}"
            else:
                protokoll.eingabe = f"{protokoll.eingabe} (3:) {eingabe}"
            protokoll.bearbeitungszeit = (timezone.now() - protokoll.start).total_seconds()
            protokoll.save()
            if kontrolle(eingabe, right):                                   #Anwort richtig
                protokoll.wertung = "richtig"
                protokoll.save()
                zaehler.richtig += 1
                zaehler.richtig_of +=1
                zaehler.aufgnr += 1
                zaehler.save()
                if zaehler.aufgnr > 10:
                    if zaehler.optionen_text not in ["", "keine",]:         #setzt eventuell Stufe hoch wenn eine Option angekreuzt wurde
                        max_stufe = 3
                        for auswahl in Auswahl.objects.filter(
                            kategorie=kategorie_id,
                            text__in=zaehler.optionen_text.split(";"),
                            ).all():
                                if(auswahl.bis_stufe) > user.stufe:
                                    user.stufe = auswahl.bis_stufe+1
                                    if user.e_kurs:
                                        user.stufe += 1
                                    user.save()
                    zaehler.optionen_text = ""
                    zaehler.hinweis = ""
                    zaehler.aufgnr = 0
                    zaehler.save()
                    return redirect('kategorien')
                quote = int(zaehler.falsch/(zaehler.richtig+zaehler.falsch)*100)
                msg = f'<br>richtig: {zaehler.richtig}, falsch: {zaehler.falsch}, Fehlerquote: {quote}%, EoF: {zaehler.richtig_of}/{kategorie.eof}'
                messages.info(req, f'Richtig! {msg}')
                return redirect('main', slug)
            else:                                                           #Antwort falsch
                protokoll.wertung = "f"
                protokoll.save()
                zaehler.falsch += 1
                zaehler.richtig_of  = 0
                zaehler.save()
                quote = int(zaehler.falsch/(zaehler.richtig+zaehler.falsch)*100)
                msg = f'<br>richtig: {zaehler.richtig}, falsch: {zaehler.falsch}, Fehlerquote: {quote}%, EoF: {zaehler.richtig_of}/{kategorie.eof}'
                messages.info(req, f'Leider falsch! Versuche: {protokoll.tries}, {msg}')        
                text = protokoll.text
                if protokoll.tries >= 3:                                    #3 mal falsch
                    return redirect('kategorien')
    else:                                                                   #Aufgabenstellung
        form = AufgabeFormZahl()
        user = get_fake_user()
        if zaehler.optionen_text == "":                                     #Aufgaben Einstellung
            return redirect('optionen', slug)
        typ, text, pro_text, lsg, result = aufgaben(kategorie.id, jg = user.jg, stufe = user.stufe, typ_anf = zaehler.typ_anf, typ_end = zaehler.typ_end, optionen = "") 
        protokoll = Protokoll.objects.create(
            user = user, kategorie = kategorie, text = pro_text, value = result, loesung = lsg        
        )                                                                   #Protokoll wird erstellt
        req.session['eingabe_id'] = protokoll.id    
        req.session['zaehler_id'] = zaehler.id   
        if zaehler.aufgnr == 0:
            zaehler.aufgnr = 1
        zaehler.save()        
        protokoll.typ = typ
        protokoll.aufgnr = zaehler.aufgnr
        protokoll.save()  
        if zaehler.hinweis!= "":
            messages.info(req, f'Lösung: {zaehler.hinweis}')    
    context = dict(kategorie = kategorie, typ = typ, aufgnr = zaehler.aufgnr, text = text, form = form, zaehler_id = zaehler.id,)
    return render(req, 'core/aufgabe.html', context)

def optionen(req, slug):
    kategorie = get_object_or_404(Kategorie, slug = slug)
    form = AuswahlForm(kategorie = kategorie)
    user = get_fake_user()   
    zaehler = get_object_or_404(Zaehler, kategorie = kategorie, user = user)
    if req.method == 'POST':
        form = AuswahlForm(req.POST, kategorie = kategorie)
        if form.is_valid():
            #zaehler.optionen.set(form.cleaned_data['optionen'])
            optionen_text = ';'.join(map(str, form.cleaned_data['optionen']))
            if optionen_text == "":
                optionen_text = "keine"
        else:
            optionen_text = "keine"  
    else:
        anzahl = kategorie.auswahl_set.all().count()
        if anzahl>0:
            anzahl = Auswahl.objects.filter(bis_jg__gt = user.jg, bis_stufe__gt = user.stufe,kategorie = kategorie).count()
            if anzahl>1:
                return render(req, 'core/optionen.html', {'kategorie': kategorie, 'auswahl_form':form})
            else:
                optionen_text = "keine"    
        else:
            optionen_text = "keine"
    zaehler.optionen_text = optionen_text        
    zaehler.save()
    typ_anf, typ_end = aufgaben(kategorie.id, jg = user.jg, stufe = user.stufe, optionen = zaehler.optionen_text)
    zaehler.typ_anf = typ_anf
    zaehler.typ_end = typ_end
    zaehler.save()
    return redirect('main', slug)

def abbrechen(req, zaehler_id):
    zaehler = get_object_or_404(Zaehler, pk = zaehler_id)
    zaehler.aufgnr = 0
    zaehler.optionen_text = ""
    zaehler.abbrechen = zaehler.abbrechen+1
    zaehler.richtig_of = 0 
    zaehler.hinweis = ""
    zaehler.save() 
    protokoll = Protokoll.objects.filter(user = zaehler.user).order_by('-id').first()
    protokoll.eingabe = "abbr."
    protokoll.save()
    return redirect('uebersicht')

def loesung(req, zaehler_id):
    zaehler = get_object_or_404(Zaehler, pk = zaehler_id)
    zaehler.loesung +=1
    zaehler.richtig_of = 0 
    protokoll = Protokoll.objects.filter(user = zaehler.user).order_by('-id').first()
    msg=f'{protokoll.text} = {protokoll.loesung}'    
    protokoll.eingabe = "Lsg."
    protokoll.save()
    zaehler.hinweis = msg
    zaehler.save()   
    return redirect('main', zaehler.kategorie)
