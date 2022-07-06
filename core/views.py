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
            typ_end = 5 + stufe%2                               #6 für E-Kurs
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end) 
        if typ == 1 :                                               #Wechselgeld
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
            typ = "Wechselgeld"
        elif typ <= 3:                                              #ganze Zahlen
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
            text = pro_text = (
                f"ergänze {format_number(zahl1, exp+exp2,)}"
                f" zu {format_number(zahl2, exp)}")
            lsg = f"{format_number(zahl2-zahl1,exp+exp2)}"
        return typ, text, pro_text, "", lsg,  "", zahl2-zahl1, {'name':''}

def addieren(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 2
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)    
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
        return typ, text, "", "", lsg, "", zahl1+zahl2, {'name':''}

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
    return typ, text, "", "", lsg, "", result, {'name':''}

def verdoppeln(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 0
        typ_end = 3
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_anf = -2
            typ_end = 2
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
        hilfe = "Wenn man das gut geübt hat, kann man viel schneller Kopfrechnen!"
    # hier wird die Aufgabe erstellt:
        if typ == 0:
            zahl1 = random.randint(6,60)
            text = "Was ist das Doppelte von " + (str(zahl1)) + "?"
            lsg = str(zahl1*2) 
            erg = zahl1*2      
        elif typ > 0:
            zahl1 = random.randint(3,30)
            text = "Was ist das Vierfache von " + (str(zahl1)) + "?"
            lsg = str(zahl1*4)  
            erg = zahl1*4      
            hilfe = "Hier muss du zweimal verdoppeln"
        else:                                                               #Kommazahlen      
            zahl2 = random.randint(4,60)
            zahl1 = zahl2*10**(typ)
            text = f"Was ist das Doppelte von {format_number(zahl1,abs(typ))} ?"
            lsg = f"{format_number(zahl1*2,abs(typ))}" 
            erg = zahl1*2    
    pro_text = text
    return typ, text, "", "", lsg, hilfe, erg, {'name':''}
    
def halbieren(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_anf = 2
            typ_end = 2 + stufe%1
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
    # hier wird die Aufgabe erstellt:
        if typ == 1:
            zahl1 = random.randint(5,99)
            text = "Was ist die Hälfte von " + 2*(str(zahl1)) + "?"
            lsg = str(zahl1)       
        elif typ > 2:                                                               #Kommazahlen      
            zahl2 = random.randint(0,2)
            zahl1= 2*random.randint(1,99)
            zahl1 = zahl1/10**(zahl2)
            text = f"Was ist die Hälfte von {format_number(zahl1,zahl2)} ?"
            lsg = f"{format_number(zahl1/2,zahl2)}"   
        else:   
            zahl2 = random.randint(0,2)
            zahl3= random.randint(1,99)
            zahl1 = zahl3/10**(zahl2)
            text = f"Was ist die Hälfte von {format_number(zahl1,zahl2)} ?"
            lsg = f"{format_number(zahl1/2,(zahl2+(zahl3%2)))}"   
    pro_text = text
    return typ, text, "", "", lsg, "Hilfe", zahl1/2, {'name':''}

def einmaleins(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 11
        if "nur" in optionen:
            typ_end = 7
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
    # hier wird die Aufgabe erstellt:
        if typ <= 7 :
            zahl1 = random.randint(2,10)
            zahl2 = random.randint(2,10)
        elif typ < 10:                                                               #Kommazahlen      
            zahl1 = random.randint(4,14)
            zahl2 = random.randint(2,10) 
        else:   
            zahl1 = random.randint(10,13)
            zahl2 = random.randint(10,13)
        if typ != 7:
            text = pro_text = str(zahl1) + chr(8901) + str(zahl2) +"=?"
            lsg = str(zahl1*zahl2)  
            erg = zahl1*zahl2  
        else:
            text = pro_text = str(zahl1*zahl2) + ":" + str(zahl2) +"=?"
            lsg = str(zahl1)  
            erg = zahl1             
    return typ, text, "", "", lsg, "", erg, {'name':''}

def kopfrechnen(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 9
        if "nur" in optionen:
            typ_end = 7
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
        hilfe = "Diese Aufgaben muss du ohne Taschenrechner üben! Du wirst sehen: Wenn du Kopfrechnen kannst, wirst du stolz auf dich sein!"
    # hier wird die Aufgabe erstellt:
        if typ < 3 or typ == 6 :
            zahl1 = random.randint(1,99)
            zahl2 = random.randint(1,9)
            lsg = str(zahl1+zahl2)
            erg = zahl1+zahl2
            if typ < 3:
                text = str(zahl1) + " + " + str(zahl2) +" ="
            else:
                text = str(zahl2) + " + " + str(zahl1) +" ="
        elif typ == 3  or typ == 7:
            zahl2 = random.randint(1,9)
            zahl1 = random.randint(1,90) + zahl2
            lsg = str(zahl1-zahl2)
            erg = zahl1-zahl2
            text = str(zahl1) + " - " + str(zahl2) +" ="
        elif typ == 4: 
            zahl1 = random.randint(1,10)
            zahl2 = random.randint(1,10)  
            text = pro_text = str(zahl1) + " " + chr(8901) + " " + str(zahl2) +" ="
            lsg = str(zahl1*zahl2)  
            erg = zahl1*zahl2  
        elif typ == 5:
            zahl2 = random.randint(1,9)
            zahl1 = random.randint(1,9) * zahl2
            lsg = str(zahl1/zahl2)
            erg = zahl1/zahl2
            text = str(zahl1) + " : " + str(zahl2) +" ="  
        else:
            zahl1 = random.randint(1,14)
            if zahl1 < 5:
                zahl2 = random.randint(1,4+zahl1) + (11-zahl1)   
            else:
                zahl2 = random.randint(1,14)
            typ2 = random.randint(1,5)
            if typ2 == 5:
                lsg = str(zahl2)
                erg = zahl2
                text = str(zahl1) + " : " + str(zahl2) +" ="                  
            else:
                lsg = str(zahl1*zahl2)
                erg = zahl1*zahl2
                text = str(zahl1) + " " + chr(8901) + " " + str(zahl2) +" ="       
        pro_text = text            
    return typ, text, "", "", lsg, hilfe, erg, {'name':''}

def zahl_wort(zahl):
    einer = ["", "ein", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn", "zwanzig"]
    zehner = ["zwanzig", "dreißig", "vierzig", "fünfzig", "sechzig", "siebzig", "achtzig", "neunzig"]
    if zahl > 99:
        zahl_hundert = zahl//100
        zahlwort = einer[zahl_hundert] + "hundert"
        zahl = zahl%100
    else:
        zahlwort = ""
    if zahl <= 20:
        zahlwort = zahlwort + einer[zahl]
    else:
        zahl_einer = zahl%10
        zahlwort = zahlwort + einer[zahl_einer]
        zahl_zehner = zahl//10
        if zahl_einer != 0:
            zahlwort = zahlwort + "und" + zehner[zahl_zehner-2]
        else:
            zahlwort = zahlwort + zehner[zahl_zehner-2]
    return zahlwort

def zahlen(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    if optionen != "":
        typ_anf = 3
        if stufe >= 4 or jg >= 7 or "Kommazahlen" in optionen:
            typ_end = 9
        elif stufe >= 8 or jg >= 7 or "Brüchen" in optionen:
            typ_end = 10
        elif stufe >= 18 or jg >= 8 or "negativen" in optionen:
            typ_end = 12
        else:
            typ_anf = 1
            typ_end = 5        
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end+stufe%1*2) 
        anm = ""
        pro_text = ""
    # hier wird die Aufgabe erstellt:
        grafik = {'name': ''}
        if typ == 1:
            zahl2 = random.randint(5,7+stufe%1)
            zahl1 = random.randint(10000,10**zahl2)
            if stufe%2 == 1:
                while not "0" in str(zahl1):
                    zahl1 = random.randint(10000,10**zahl2)
            if zahl1 >= 1000000:
                zahl_mill = zahl1//1000000
                if zahl_mill == 1:
                    text = "Eine Million "
                else: 
                    text = (zahl_wort(zahl_mill)) + "millionen " 
                    #text = text_k.capitalize()
            else:
                text =""
            zahl_tsnd = zahl1%1000000//1000
            text =text + zahl_wort(zahl_tsnd) + "tausend"
            zahl_klein = zahl1%1000
            text_k = text + zahl_wort(zahl_klein)
            text = "Schreibe folgende Zahl in Ziffern: " + text_k.title()
            if zahl1 < 1000000:
                lsg= "%d %03d"%((zahl_tsnd), (zahl_klein))
            else:
                lsg= "%d %03d %03d"%(zahl_mill, zahl_tsnd, zahl_klein)
            erg=zahl1
            hilfe = ""
        elif typ == 2:
            typ2 = random.randint(1,2)
            zahl3 = random.randint(2,3+stufe%2)
            zahl1 = 1
            for n in range(1,zahl3):
               zahl2 = random.randint(0,3)
               zahl2 = (20-zahl2)%10
               zahl1 = zahl1 + zahl2*10**n
            if typ2 == 1:
                text = "Wie heißt der Nachfolger von %d ?"%zahl1 
                erg = zahl1+1
                lsg = str(zahl1+1)
                hilfe = "Um den Nachfolger auszurechnen musst du 1 addieren."
            else:
                if zahl1 < 1:
                    zahl1 = 1
                text = "Wie heißt der Vorgänger von %d ?"%zahl1 
                erg = zahl1-1
                lsg = str(zahl1-1)
                hilfe = "Um den Vorgänger auszurechnen musst du 1 subtrahieren."
        elif typ in (3,6,7,8):
            zuza1 = random.randint(1,9)
            zuza2 = 1
            if typ == 3:
                stellen = random.randint(2,3)
            else:
                stellen = random.randint(1,2)
            zahl1 = zahl2 = zuza1*10**stellen
            zuza = [0, zuza1, zuza2]
            for n in 0, stellen-1:
                random.shuffle(zuza)
                zahl1 = zuza[0] * 10**n + zahl1
                zahl1_str = str(zahl1)
                random.shuffle(zuza)
                zahl2 = zuza[0] * 10**n + zahl2  
                zahl2_str = str(zahl2)
            if typ in [6,8]:                                      #erzeugt Kommazahlen
                komma = random.randint(0,2)
                if komma > 0:
                    zahl1_str = str(zahl1)[:komma]+","+str(zahl1)[1:].rstrip("0")
                    zahl2_str = str(zahl2)[:komma]+","+str(zahl2)[1:].rstrip("0")
                else:
                    zahl1_str = "0,"+str(zahl1).rstrip("0")
                    zahl2_str = "0,"+str(zahl2).rstrip("0")
                zahl1_str = zahl1_str.rstrip(",")
                zahl2_str = zahl2_str.rstrip(",") 
                zahl1=float(zahl1_str.replace(",", "."))
                zahl2 = float(zahl2_str.replace(",", "."))
            if typ in [7,8]:                                      #erzeugt negative Zahlen
                zahl1_str = "-" + str(zahl1_str)
                zahl2_str = "-" + str(zahl2_str)
                zahl1 = -zahl1
                zahl2 = -zahl2
            pro_text = zahl1_str + " ? " +  zahl2_str
            text = 'Kleiner, größer oder gleich?<br>' + pro_text 
            anm = "(Setze das entsprechende Zeichen ein)" 
            erg = 0
            if zahl1 < zahl2:
                lsg = [str(zahl1) + "<" +  str(zahl2), "<"]
            elif zahl1 > zahl2:
                lsg = [str(zahl1) + ">" +  str(zahl2), ">"]
            else:
                lsg = [str(zahl1) + "=" +  str(zahl2), "="]
            hilfe = "" 
            typ = "Kleiner, größer oder gleich? (" + str(typ) +")"
            grafik = {'name': ''}                  
        else:                                   # 4+5 ganze zahlen, 9+12 Kommazahlen, 10 Brüche, 11+12 negative Zahlen
            if typ != 10:
                bruch = False
                if typ == 4 and stufe%2 == 1:
                    eint = 20                       # 10 = 10er, 20 = 5er, 25 = 4er (für Brüche)
                else:
                    eint = 10
                exp = random.randint(1,4)
                z = 10**exp                         #Einteilung der Anzeige 0.1 1, 10, 100 ...
                if typ == 10:
                    v = random.randint(3,7)*-1
                else:
                    v = random.randint(0,8)         #ist die Verschiebung des Nullpunktes
                if typ_end == 5 and v == 0:         #ohne neg Zahlen bei 20 an, sonst bei 0
                    anf = 20                             
                else:
                    anf = 0
                text_v = len(str(z))*-3             #die Verscheibung des Textes (dmit die Zahl in der Mitte unter dem Strich steht)
                if stufe%2 == 1 and eint == 10 and z > 10:
                    zahl1 = random.randint(1,90)*5
                else:
                    zahl1 = random.randint(1,45)*10
                text = "Auf welche Zahl zeigt der Pfeil ?"               
                if eint == 10 and zahl1%10 == 5:
                    anm = "(Du musst genau hinsehen: Der Pfeil steht zwischen zwei Strichen.)"
                hilfe = ""
                erg = int((zahl1+v*100)*z/100)
                lsg = str(erg)
            else:
                bruch = True
                typ2 = random.randint(1,4)
                anf = 0
                z = 1
                v = 0
                text_v = 0
                nenner_liste = [4,5,10]
                random.shuffle(nenner_liste)
                nenner = nenner_liste[0]
                if nenner == 4:
                    eint = 25
                else:
                    eint = 10
                zaehler = nenner
                while zaehler%nenner == 0:                      #keine ganzen Zahlen
                    zaehler = random.randint(1,nenner)
                bruch = 0.0
                if typ2 > 2:
                    ganz = 0
                else:
                    ganz = typ2
                bruch = zaehler/nenner+ganz
                zahl1 = bruch * 100
                hilfe = "Für den Nenner musst du zählen in wieviele Teile der Zahlenstrahl zwischen den Zahlen unterteilt ist."
                erg = 0
                ganz = int(bruch*100//100)
                zaehler = int(bruch*100//eint)
                if ganz == 0:
                    bruch_str = str(zaehler) + "/" + str(int(100/eint)) 
                    lsg = [bruch_str]
                else:
                    bruch_str = str(ganz) + " " +  str(int(bruch*100//eint - ganz * 100/eint))  + "/" + str(int(100/eint)) 
                    lsg = [bruch_str, (str(zaehler)+"/"+str(nenner))] 
                print(bruch_str)
                print(bruch)
                print(zaehler)
                print(100/eint)
                kuerz = ggt(zaehler,100/eint)
                print(kuerz)
                if kuerz > 1 :
                    if ganz == 0:
                        bruch_str = str(int(zaehler/kuerz)) + "/" + str(int(100/eint/kuerz)) 
                        lsg.append(bruch_str)
                    else: 
                        bruch_str = str(ganz) + " " +  str(int(bruch*50//eint - ganz * 50/eint))  + "/" + str(int(50/eint)) 
                        lsg.append(bruch_str)
                        lsg.append(str(int(zaehler/2))+"/"+str(int(50/eint))) 
                text = "Welcher Bruch ist hier dargestellt ?"
                anm = "Schreibe als Bruch (9/7) oder als gemischte Zahl (1 2/7)"
            grafik = {'name': 'zahlenstrahl', 'anf': anf, 'eint':eint, 'v': v, 'txt0':  z+(v-1)*z, 'txt1': z+v*z, 'txt2': z+(v+1)*z, 'txt3': z+z*(v+2), 'txt4': z+z*(v+3), 'text_v': text_v, 'x': int(zahl1)+20, 'bruch':bruch}
        return typ, text, pro_text, anm, lsg, hilfe, erg, grafik 

def ggt(a,b):
    if b == 0:
        return a
    return ggt(b, a % b)

AUFGABEN = {
    1: ergaenzen,
    2: addieren,
    3: subtrahieren,
    4: verdoppeln,
    5: halbieren,
    6: einmaleins,
    7: kopfrechnen,
    8: zahlen,
}

def aufgaben(kategorie_id, jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = ""):
    return AUFGABEN[kategorie_id](jg, stufe, typ_anf, typ_end, optionen)

def kontrolle(given, value, lsg):
    if value != 0:
        return given == value 
        #return abs(given - value) < decimal.Decimal('0.001')
    else:
        for loe in (lsg):
            if given.replace(" ","") == loe.replace(" ",""):
                return True
        else:
            return False

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
    return render(req, 'core/details.html', {'protokoll': protokoll, 'zaehler': zaehler})

def main(req, slug):                                                        #hier läuft alles zusammen
    kategorie = get_object_or_404(Kategorie, slug = slug)
    kategorie_id = kategorie.id
    user = get_fake_user()    
    if req.method == 'POST':  
        protokoll = Protokoll.objects.get(pk = req.session.get('eingabe_id'))
        protokoll.tries += 1
        zaehler = Zaehler.objects.get(pk = req.session.get('zaehler_id'))
        zaehler.hinweis = ""
        if protokoll.value != 0:
            form = AufgabeFormZahl(req.POST)
        else:
            form = AufgabeFormStr(req.POST)
        if form.is_valid():                                                 #Aufgabe beantwortet
            eingabe = form.cleaned_data['eingabe']
            if protokoll.tries == 1:
                protokoll.eingabe = protokoll.eingabe + str(eingabe)
            elif protokoll.tries == 2:
                protokoll.eingabe =f"(1:) {protokoll.eingabe} (2:) {eingabe}"
            else:
                protokoll.eingabe = f"{protokoll.eingabe} (3:) {eingabe}"
            protokoll.bearbeitungszeit = (timezone.now() - protokoll.start).total_seconds()
            protokoll.save()
            if kontrolle(eingabe, protokoll.value, protokoll.loesung):      #Anwort richtig
                protokoll.wertung = "richtig"
                protokoll.save()
                zaehler.richtig += 1
                zaehler.richtig_of +=1
                zaehler.aufgnr += 1
                zaehler.save()
                if zaehler.aufgnr > 10:
                    if  zaehler.optionen_text not in ["", "keine",] and "nur" not in zaehler.optionen_text:         #setzt eventuell Stufe hoch wenn eine Option angekreuzt wurde
                        max_stufe = 3
                        for auswahl in Auswahl.objects.filter(
                            kategorie=kategorie_id,
                            text__in=zaehler.optionen_text.split(";"),
                            ).all():
                                if(auswahl.bis_stufe) > user.stufe:
                                    user.stufe = auswahl.bis_stufe+user.stufe%2
                                    user.save()
                    zaehler.optionen_text = ""
                    zaehler.hinweis = ""
                    zaehler.aufgnr = 0
                    zaehler.save()
                    return redirect('kategorien')
                quote = int(zaehler.falsch/(zaehler.richtig+zaehler.falsch)*100)
                msg = f'<br>richtig: {zaehler.richtig}, falsch: {zaehler.falsch}, Fehlerquote: {quote}%, EoF: {zaehler.richtig_of}/{kategorie.eof}'
                messages.info(req, f'Die letzte Aufgabe war richtig! {msg}')
                return redirect('main', slug)
            else:                                                           #Antwort falsch
                protokoll.wertung = "f"
                protokoll.save()
                zaehler.falsch += 1
                zaehler.richtig_of  = 0
                zaehler.save()
                quote = int(zaehler.falsch/(zaehler.richtig+zaehler.falsch)*100)
                msg = f'<br>richtig: {zaehler.richtig}, falsch: {zaehler.falsch}, Fehlerquote: {quote}%, EoF: {zaehler.richtig_of}/{kategorie.eof}'
                messages.info(req, f'Die letzte Aufgabe war leider falsch! Versuche: {protokoll.tries}, {msg}')   
                if protokoll.tries >= 3:                                    #3 mal falsch
                    messages.info(req, f'letzte Aufgabe: {protokoll.text}, Lösung: {protokoll.loesung}')                     
                    return redirect('kategorien')
                text = protokoll.text
                anm = protokoll.anmerkung
                hilfe = protokoll.hilfe
                grafik = protokoll.grafik
    else:                                                                   #Aufgabenstellung
        zaehler, created = Zaehler.objects.get_or_create(user = user, kategorie = kategorie)
        form = AufgabeFormZahl()
        user = get_fake_user()
        if not zaehler.optionen_text :                                     #Aufgaben Einstellung
            return redirect('optionen', slug)
        typ, text, pro_text, anm, lsg, hilfe, result, grafik = aufgaben(kategorie.id, jg = user.jg, stufe = user.stufe, typ_anf = zaehler.typ_anf, typ_end = zaehler.typ_end, optionen = "") 
        if not pro_text:
            pro_text = text 
        protokoll = Protokoll.objects.create(
            user = user, kategorie = kategorie, text = text, pro_text = pro_text, anmerkung = anm, value = result, loesung = lsg, hilfe = hilfe, grafik = grafik       
        )                                                                   #Protokoll wird erstellt
        req.session['eingabe_id'] = protokoll.id    
        req.session['zaehler_id'] = zaehler.id   
        if protokoll.value != 0:
            form = AufgabeFormZahl(req.POST)
        else:
            form = AufgabeFormStr(req.POST)
        if zaehler.aufgnr == 0:
            zaehler.aufgnr = 1
        zaehler.save()        
        protokoll.typ = typ
        protokoll.aufgnr = zaehler.aufgnr        
        protokoll.save()  
        if zaehler.hinweis!= "":
            messages.info(req, f'{zaehler.hinweis}')   
    if len(str(protokoll.typ)) < 3:
        protokoll.typ = ""
    context = dict(kategorie = kategorie, typ = protokoll.typ, aufgnr = zaehler.aufgnr, text = text, anmerkung = anm, form = form, zaehler_id = zaehler.id, hilfe = hilfe, protokoll_id = protokoll.id, grafik = grafik)
    return render(req, 'core/aufgabe.html', context)

def optionen(req, slug):
    kategorie = get_object_or_404(Kategorie, slug = slug)
    form = AuswahlForm(kategorie = kategorie)
    user = get_fake_user()   
    zaehler = get_object_or_404(Zaehler, kategorie = kategorie, user = user)
    if req.method == 'POST':
        form = AuswahlForm(req.POST, kategorie = kategorie)
        if form.is_valid():
            optionen_text = ';'.join(map(str, form.cleaned_data['optionen']))
            if optionen_text == "":
                optionen_text = "keine"
        else:
            optionen_text = "keine"  
    else:
        anzahl = kategorie.auswahl_set.all().count()
        if anzahl>0:
            anzahl = Auswahl.objects.filter(bis_jg__gt = user.jg, bis_stufe__gt = user.stufe,kategorie = kategorie).count()
            if anzahl>0:
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
    protokoll.eingabe = protokoll.eingabe + "abbr."
    protokoll.save()
    return redirect('uebersicht')

def loesung(req, zaehler_id):
    zaehler = get_object_or_404(Zaehler, pk = zaehler_id)
    zaehler.loesung +=1
    zaehler.richtig_of = 0 
    protokoll = Protokoll.objects.filter(user = zaehler.user).order_by('-id').first()
    msg=f'letzte Aufgabe:<br>{protokoll.text} Lösung: {protokoll.loesung[0]}'    
    protokoll.eingabe = "Lsg."
    protokoll.save()
    zaehler.hinweis = msg
    zaehler.save()   
    return redirect('main', zaehler.kategorie)

def hilfe(req, zaehler_id, protokoll_id):
    zaehler = get_object_or_404(Zaehler, pk = zaehler_id)
    protokoll = get_object_or_404(Protokoll, pk = protokoll_id)
    kategorie = protokoll.kategorie
    typ = protokoll.typ
    text = protokoll.text
    anm = protokoll.anmerkung
    hilfe = protokoll.hilfe
    grafik = protokoll.grafik
    msg=f'{protokoll.hilfe}'
    messages.info(req, f'{zaehler.hinweis}')  
    protokoll.eingabe = protokoll.eingabe + " Hilfe "
    protokoll.save()
    zaehler.hilfe +=1
    zaehler.hinweis = msg
    zaehler.save()
    if protokoll.value != 0:
        form = AufgabeFormZahl(req.POST)
    else:
        form = AufgabeFormStr(req.POST)
    context = dict(kategorie = kategorie, typ = typ, aufgnr = zaehler.aufgnr, text = text, form = form, zaehler_id = zaehler.id, hilfe = hilfe, protokoll_id = protokoll.id)
    return render(req, 'core/aufgabe.html', context)