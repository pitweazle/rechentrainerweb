import decimal
import random
from re import A
from token import NOTEQUAL
from unittest.util import strclass

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from datetime import date, datetime, timedelta

from .forms import AufgabeFormZahl, AufgabeFormStr
from .forms import AuswahlForm, ProtokollFilter

from .models import Kategorie, Protokoll, Zaehler
from .models import Schueler
from .models import Auswahl

from django.http import HttpResponse, HttpResponseNotFound

from django.db.models import Sum

def format_number(value, precision=2, trailing_zeros=True):
    text = f"{value:.{precision}f}".replace(".", ",")
    return text.rstrip(",0") if not trailing_zeros and "," in text else text

def ergaenzen(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1 
        typ_end = 3
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 5 + stufe%2                               #6 für E-Kurs
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end) 
        titel = "Ergänzen"
        hilfe = """Hier ist es gut die Zahlenpaare zu kennen, die zusammen 10 ergeben, also 1-9, 2-8, 3-7 ... 
        Beim Ergänzen musst du normalerweise immer vom Partner der angezeigten Ziffer 1 subtrahiern (Bsp.: Anzeige "7", Partner "3", Eingabe "2") - außer bei der letzten Ziffer, da darfst du nicht 1 subtrahieren."""
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
            titel = "Wechselgeld"
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
        return typ, titel, text, pro_text, "", [lsg],  hilfe, zahl2-zahl1, {'name':''}

def addieren(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 2
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)  
        titel = "Addieren"  
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
        return typ, titel, text, "", "", [lsg], "", zahl1+zahl2, {'name':''}

def subtrahieren(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 2
        return typ_anf, typ_end
    else:
        titel = "Subtrahieren"
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
    return typ, titel, text, "", "", [lsg], "", result, {'name':''}

def verdoppeln(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 0
        typ_end = 3
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_anf = -2
            typ_end = 2
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
        titel = "Verdoppeln"
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
    return typ, titel, text, "", "", [lsg], hilfe, erg, {'name':''}
    
def halbieren(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_anf = 2
            typ_end = 2 + stufe%1
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
        titel = "Halbieren"
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
    return typ, titel, text, "", "", [lsg], "Hilfe", zahl1/2, {'name':''}

def einmaleins(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 11
        if "nur" in optionen:
            typ_end = 7
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
        titel = "1 mal 1"
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
    return typ, titel, text, "", "", [lsg], "", erg, {'name':''}

def kopfrechnen(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 9
        if "nur" in optionen:
            typ_end = 7
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
        titel = "Kopfrechnen"
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
    return typ, titel, text, "", "", [lsg], hilfe, erg, {'name':''}

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

def ggt(a,b):
    if b == 0:
        return a
    return ggt(b, a % b)

def trenner(wert):
    zahl_mill = wert//1000000        
    zahl_tsnd = wert%1000000//1000
    zahl_klein = wert%1000 
    zahl = ""
    zahl =  "%d %03d %03d"%(zahl_mill, zahl_tsnd, zahl_klein)
    zahl = zahl.lstrip("0").lstrip(" ").lstrip("0") 
    return zahl

def zahlen(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        if stufe >= 4 or jg >= 7 or "Kommazahlen" in optionen:
            typ_end = 9
        elif stufe >= 8 or jg >= 7 or "Brüchen" in optionen:
            typ_end = 10
        elif stufe >= 18 or jg >= 8 or "negativen" in optionen:
            typ_end = 12
        else:
            typ_end = 5        
        return typ_anf, typ_end
    elif eingabe != "":
        if not "/" in eingabe:
            return 0, "Du sollst den angezeigten Wert als Bruch eingeben!"
        else:
            return 0, "" 
    else:
        typ = random.randint(typ_anf, typ_end+stufe%1*2) 
        anm = ""
        pro_text = ""
    # hier wird die Aufgabe erstellt:
        grafik = {'name': ''}
        if typ == 1:
            titel = "Zahlen schreiben"
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
            lsg = trenner(zahl1)
            erg=zahl1
            hilfe = ""
        elif typ == 2:
            titel = "Vorgänger und Nachfolger"
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
            titel = "Kleiner, größer oder gleich"
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
            grafik = {'name': ''}                  
        else:                                   # 4+5 ganze zahlen, 9+12 Kommazahlen, 10 Brüche, 11+12 negative Zahlen
            titel = "Zahlenstrahl"
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
                #zaehler = int(bruch*100//eint)
                zaehler = int(bruch*100//eint - ganz * 100/eint)
                nenner = int(100/eint) 
                bruch_str = str(zaehler) + "/" + str(nenner) 
                if ganz == 0:
                    lsg = [bruch_str]
                else:
                    bruch_str = str(ganz) + " " + bruch_str
                    lsg = [bruch_str, (str(zaehler+ganz*nenner)+"/"+str(nenner))] 
                kuerz = ggt(zaehler,100/eint)
                if kuerz > 1 :
                    bruch_str = str(int(zaehler/kuerz)) + "/" + str(int(nenner/kuerz)) 
                    if ganz == 0:                        
                        lsg.append(bruch_str)
                    else: 
                        bruch_str = str(ganz) + " " +  bruch_str
                        lsg.append(bruch_str)
                        lsg.append(str(int((zaehler+ganz*nenner)/kuerz)) +"/"+ str(int(nenner/kuerz)))
                lsg = ["indiv"] + lsg
                text = "Welcher Bruch ist hier dargestellt ?"
                anm = "Schreibe als Bruch (9/7) oder als gemischte Zahl (1 2/7)"
            grafik = {'name': 'zahlenstrahl', 'anf': anf, 'eint':eint, 'v': v, 'txt0':  z+(v-1)*z, 'txt1': z+v*z, 'txt2': z+(v+1)*z, 'txt3': z+z*(v+2), 'txt4': z+z*(v+3), 'text_v': text_v, 'x': int(zahl1)+20, 'bruch':bruch}
        return typ, titel, text, pro_text, anm, lsg, hilfe, erg, grafik 

def malget10(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 3
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 8 + stufe%2                               #6 für E-Kurs
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end)
        hilfe = ""
        exp = random.randint(1,3)
        if typ < 4:                                     #ganze Zahl
            zahl1 = random.randint(1,99)                #Multi.
            zahl2 = 10**exp 
            if typ == 3:                                #Div.'                    
                exp2 = 4
                while exp2 > exp:
                    exp2 = random.randint(1,3)
                    zahl2 = 10**exp2
        elif typ > 3:                                   #Kommazahlen
            if typ < 6:                                 #Multip. typ 4 und 5
                zahl1 = random.randint(1,999)/10  
                zahl2 = 10**exp 
            else:
                zahl1 = random.randint(1,99)*10/100     #typ 6
                zahl2=  10**(exp*-1)                
        elif typ < 9:                                   #Div. durch ganze Zahl   typ 7 und 8     
            zahl1 = random.randint(1,99)  
            zahl2 = 10**exp 
        else:                                           #Div. durch Kommazahl  typ 9                           
            zahl1 = random.randint(1,99)
            zahl2 = 10**(exp*-1)  
                                                        #Aufgabe, Ergebnis, Lösung, Hilfe:    
        if typ == 1 or typ == 2 or typ == 4 or typ == 5:
            text = "Multipliziere:<br> {0} {1} {2}".format(zahl1, chr(8901), zahl2).replace(".", ",")
            erg = zahl1 * zahl2
            lsg = str(int(erg))
            if typ < 3:
                hilfe = "Mal {0} heißt, dass die Zahl {1} um  {2} Stelle(n) größer wird.".format(zahl2,zahl1, exp) 
                if stufe%2 == 0:
                    hilfe = hilfe + "<br>Du musst also {0} Null(en) anhängen.".format(exp)
                titel = "Mal: 10, 100, 1000"
            else:
                typ = "Mal: 0,01; 0,1; 10; 100; 1000"
        else:                                           #typ 3, 6, 7 , 8, 9
            text = "Dividiere:<br> {0} {1} {2}".format(zahl1, " : ", zahl2).replace(".", ",")
            erg = zahl1 / zahl2
            lsg = str(round(erg,5)).replace(".", ",").rstrip(",")
            if typ == 3:
                hilfe="Geteilt durch {0} heißt, dass die Zahl {1} um  {2} Stelle(n) kleiner wird.".format(zahl2, zahl1, exp2) 
                if stufe%2 == 0:
                    hilfe = hilfe + "<br>Du musst also {0} Null(en) wegnehmen.".format(exp2)
                titel = "Geteilt durch: 10, 100, 1000"
            else:
                if typ == 9:
                    hilfe = "Geteilt durch {0} heißt, dass die Zahl {1} um  {2} Stelle(n) größer wird.".format(zahl2,zahl1, exp).replace(".", ",") 
                    hilfe = hilfe + "<br>Du musst also das Komma um {0} Stelle(n) nach rechts verschieben <br>(und unter Umständen noch Nullen ergänzen).".format(exp)
                    titel = "Geteilt durch: 0,1; 0,01"
                else:
                    hilfe = "Geteilt durch {0} heißt, dass die Zahl {1} um  {2} Stelle(n) kleiner wird.".format(zahl2,zahl1, exp).replace(".", ",") 
                    hilfe = hilfe + "<br>Du musst also das Komma um {0} Stelle(n) nach links verschieben <br>(und unter Umständen noch Nullen ergänzen).".format(exp)
                    if typ == 8:
                        hilfe = hilfe = hilfe + "<br>(Ja, stimmt, es ist kein Komma da - du musst es dir hinter der {0} denken".format(zahl1)
                    titel = "Geteilt durch: 10, 100, 1000" 
        return typ, text, "", "", [lsg], hilfe, erg, {'name':''}

def runden(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 6
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_anf = -3  
        return typ_anf, typ_end
    elif eingabe != "":
        loe = (lsg[1])
        if eingabe.replace(" ","") != loe.replace(" ",""):
            erg = loe.replace(",",".")
            eing = eingabe.replace(",",".")
            if float(erg) == float(eing):
                meldung = "Leider falsch! Richtig wäre: " + (erg) + "- Deine Eingabe: " + eing + "<br>Du darfst die Null am Ende nicht weglassen - <br>Die Zahl muss genau {0} Stellen hinter dem Komma haben".format(len(erg)-erg.find("."))
                return -1, meldung.replace(".", ",")
        else:
            return 0, "" 
    else:
        typ = random.randint(typ_anf, typ_end)
        titel = "Runden"
        name_liste = ("Einer", "zehn", "hundert", "tausend", "zehntausend", "hunderttausend",  "million")
        n = ""
        if typ < -1:
            endung = "stel" 
        elif typ == 6:
            endung = "en"
        elif typ > 0:
            endung = "er"
            n = "n"
        elif typ == -1:
            endung = "tel"
        else:
            endung = ""

        if typ > 0:
            exp = 10**(typ+2)
            zahl1 = int(random.random()*exp)        
            name = name_liste[typ] + endung
            name = name.title()
            zahl = trenner(zahl1)
            text = " Runde {0} auf {1}".format(zahl,name)
            erg = round(zahl1 / 10.0 ** typ)
            erg = int(erg * 10 ** typ)
            lsg = [trenner(erg)]
            hilfe = "{0} ist die {1}.Stelle von rechts. Dahinter musst du Nullen schreiben!".format(name,typ+1)
            next = name_liste[typ-1]
            hilfe = hilfe + "<br>Wenn die Zahl rechts von den {0}{1} (die {2}er) eine 5, 6, 7, 8 oder 9 ist musst du aufrunden!".format(name,n,next.title())
        else:
            zahl2 = random.randint(1,2)
            zahl1 = int(random.random()*10**(abs(typ)+zahl2+1))
            zahl1 = zahl1*10**(typ-zahl2)
            zahl = format_number(zahl1,abs(typ)+zahl2)
            name = name_liste[abs(typ)] + endung
            name = name.title()
            text = " Runde {0} auf {1}".format(zahl,name)
            if typ < 0:
                erg = round(zahl1 ,abs(typ))
                lsg = ["{0:.{1}f}".format(zahl1,abs(typ)).replace(".",",")]
            else:
                lsg = [format_number(zahl1,abs(typ))]
            if typ < 0:
                hilfe = "{0} ist die {1}.Stelle hinter dem Komma.".format(name,abs(typ))
                hilfe = hilfe + "<br>Wenn die Zahl rechts von den {0}{1} eine 5, 6, 7, 8 oder 9 ist musst du aufrunden!".format(name,n.title())
            else:
                hilfe = "'Runde auf Einer' heißt, dass die Zahlen hinter dem Komma wegfallen."
                hilfe = hilfe + "<br>Wenn die erste Zahl hinter dem Komma eine 5, 6, 7, 8 oder 9 ist musst du aufrunden!"
            lsg = ["indiv"] + lsg
        erg = 0
        return typ, titel, text, "", "", lsg, hilfe, erg, {'name':''}

def regeln(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":
        typ_anf = 1
        typ_end = 15 + stufe%2
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end) 
        erg = 0
        anmerkung = ""
        hilfe = ""
    # hier wird die Aufgabe erstellt:
        if typ < 5:
            operation_liste = ["Addition", "Subtraktion", "Multiplikation","Division"]
            name_liste = ["Plus", "Minus", "Mal", "Geteilt"]
            ergebnis_liste = ["Summe", "Differenz", "Produkt", "Quotient"]
            typ2 = random.randint(0,3)
        elif typ > 10:
            titel = "Zahlenfolgen"
            folge = []
            n = 1
            zahl = random.randint(1,2)
            anzab = random.randint(0,1)	
            anz = 4
        else:
            titel = "Rechenregeln"
            hilfe="Es gelten die Regeln:<br>1. Punktrechnung vor Strichrechnung!<br>2. Falls Klammern da sind, werden sie zuerst berechnet!"

        if typ < 3:
            titel = "Begriffe"
            text = "Wie heißt das Ergebnis einer {0}saufgabe?".format(operation_liste[typ2])
            erg = 0
            anmerkung = "Achte auf die korrekte Schreibweise!"
            lsg = ergebnis_liste[typ2]
            random.shuffle(ergebnis_liste)
            hilfe = "Es gibt: " + ", ".join(ergebnis_liste)
            if stufe%2 == 0:
                hilfe = hilfe + "<br>{0} ist die '{1}'-Rechnung.".format(operation_liste[typ2], name_liste[typ2])
        elif typ < 5:
            titel = "Kennst du die Begriffe?"
            artikel_liste = ["die", "die", "das", "den"]
            endung_liste = ["","","","en"]
            if typ2 == 0:
                zahl1 = random.randint(1,1000)
                zahl2 = random.randint(1,20)
                erg = zahl1 + zahl2
            elif typ2 == 1:
                zahl3 = random.randint(1,980)
                zahl2 = random.randint(1,20)
                zahl1 = zahl3 + zahl2
                erg = zahl3    
            elif typ2 == 2:
                zahl1 = random.randint(1,12)
                zahl2 = random.randint(1,15)
                erg = zahl1 * zahl2 
            else:
                zahl3 = random.randint(1,9)
                zahl2 = random.randint(1,9)
                zahl1 = zahl3 * zahl2
                erg = zahl3                                            
            text = "Berechne {0} {1}{2} aus {3} und {4}".format(artikel_liste[typ2], ergebnis_liste[typ2], endung_liste[typ2],zahl1, zahl2)
            lsg = str(erg)
            if stufe%2 == 0:
                hilfe = "{0} ist das Ergebnis einer {1}saufgabe.".format(ergebnis_liste[typ2], operation_liste[typ2])
        elif typ == 5:
            zahl1=random.randint(1,10)
            zahl2=random.randint(1,8)
            zahl3=random.randint(1,7)
            text=str(zahl1) + " · ( " + str(zahl2) + " + " + str(zahl3) + ") "
            erg=zahl1*(zahl2+zahl3)
        elif typ == 6:
            zahl1=random.randint(1,8)
            zahl2=random.randint(1,7)
            zahl3=random.randint(1,8)
            zahl4=random.randint(1,7)
            text="( " + str(zahl1) + " + " + str(zahl2) + " ) · ( " + str(zahl3) + " + " + str(zahl4) + " ) "
            erg=(zahl1+zahl2)*(zahl3+zahl4)
        elif typ == 7:       
            zahl1=random.randint(2,4)
            zahl2=random.randint(1,10)
            zahl3=random.randint(1,10)*zahl1
            text=str(zahl2) + " + " + str(zahl3) + " : " + str(zahl1)
            erg=zahl2+zahl3/zahl1
        elif typ == 8:
            zahl1=random.randint(1,10)
            zahl2=random.randint(1,5)*zahl1
            zahl3=random.randint(1,10)
            text=str(zahl2) + " · " + str(zahl3) + " - " + str(zahl1)
            erg=zahl2*zahl3-zahl1
        elif typ == 9:
            zahl1=random.randint(1,10)
            zahl2=random.randint(1,10)
            zahl3=random.randint(1,10)
            text=str(zahl1) + " + " + str(zahl2) + " · " + str(zahl3)
            erg=zahl1+zahl2*zahl3
        elif typ == 10:
            zahl1=random.randint(1,10)
            zahl2=random.randint(1,10)
            zahl3=random.randint(1,10)
            text=str(zahl1) + " · " + str(zahl2) + " + " + str(zahl3)
            erg=zahl1*zahl2+zahl3
        else:
            if typ == 11:
                hilfe = "Das ist eine arithmetische Reihe. <br>Hier wird immer eine Zahl addiert."
                add = random.randint(2,4)	    
                mult = random.randint(2,3)	
                zahl = random.randint(2,10)     #Startzahl
                anzab = random.randint(0,2)	    #Start Anzeige                
            elif typ == 12:
                hilfe = "Das ist eine geometrische Reihe. <br>Hier wird immer eine Zahl multipliziert."
                add = random.randint(2,4)	    
                mult = random.randint(2,3)	
            elif typ == 13:
                hilfe = "Hier wird im Wechsel immer eine Zahl addiert und subtrahiert."
                add = random.randint(3,5)       #wird subtrahiert	    
                mult = random.randint(1,2)	             
            elif typ == 14:
                hilfe = "Hier wird im Wechsel immer eine Zahl multipliziert und addiert."
                anmerkung = "Hier musst du zwei verschiedene Rechnungen anwenden."
                add = random.randint(2,4)	    
                mult = random.randint(2,3)
                if mult == 3 and anzab == 1:
                    anz = 3	
            elif typ == 15:
                hilfe = "Hier wird im Wechsel immer eine Zahl multipliziert und subtrahiert."
                mult = random.randint(2,3)	                  
                add = mult
                while add >= mult:
                    add = random.randint(1,2)	#wird addiert
                zahl1 = 2
                anzab = 1
            elif typ == 16:
                folge = ["0","1"]
                a = 1 
                b = 1
                anmerkung = "Diese Folge nennt man 'Fibonacci Zahlen'."
                hilfe = " Addiere die benachbarten Zahlen ..."
                anzab = 0           

            if anzab == 0:
                zahl = 1
            if typ >12:
                anz = anzab + 6
            if typ == 16:
                anz =random.randint(5,8)

            n = 1
            while n <= anz + anzab:
                folge.append(str(zahl))
                if typ == 11:
                    zahl = zahl + add
                elif typ == 12:
                    zahl = zahl * mult
                elif typ == 13:
                    if n%2 == 1:
                        zahl = zahl + add
                    else:
                        zahl = zahl - mult                   
                elif typ == 14:
                    if n%2 == 1:
                        zahl = zahl * mult
                    else:
                        zahl = zahl + add
                elif typ == 15:
                    if n%2 == 1:
                        zahl = zahl * mult
                    else:
                        zahl = zahl - add                        
                else:
                    zahl = a + b
                    b = a
                    a = zahl
                n = n+1

        if typ > 10:
            folge.append("...")   
            if anzab > 0:
                folge = folge[anzab:n+anzab]  
                folge = ["..."] + folge        
            text = "Wie heißt die nächste Zahl: <br>" + "; ".join(folge)
            lsg = str(zahl)
        return typ, titel, text, "", anmerkung, [lsg], hilfe, erg, {'name':''}

def geometrie(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":                                                              #hier wird typ_anf und typ_end festgelegt u.u. nach Wahl unter 'Optionen'
        typ_anf = 1
        typ_end = 2
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 2
        return typ_anf, typ_end
    else:
        typ = random.randint(typ_anf, typ_end) 
        typ = random.randint(1,2) 

        titel = ""  
                                                                                    # hier wird die Aufgabe erstellt:
        if typ <3:
            titel = "Paralelle"

            if typ == 1:
                g = [-10,25,25]
                h = [10,25,-25]
            else:
                h = [-10,25,25]
                g = [5,25,-25]                
            random.shuffle(g)
            random.shuffle(h)
            lsg1 = ""
            n = 0
            if typ == 1:
                while n < 3:
                    if g[n] == 25:
                        lsg1 = lsg1 + "g" + str(n+1)
                    n = n+1
            else:
                while n < 3:
                    if h[n] == 25:
                        lsg1 = lsg1 + "h" + str(n+1)
                    n = n+1
            text = "Welche der Geraden sind parallel zueinander?"
            erg = 0
            lsg = lsg1[:2] + " und " + lsg1[2:]
            lsg2= lsg1[2:] + lsg1[:2]
           
            lsg = [lsg, lsg1, lsg2]
            grafik = {'name': 'parallele', 'g11': g[0], 'g21':g[1], 'g31': g[2], 'g12': -g[0], 'g22': -g[1], 'g32': -g[2],'h11': h[0], 'h21': h[1], 'h31': h[2], 'h12': -h[0], 'h22': -h[1], 'h32': -h[2]}
        else:
            pass
        return typ, titel, text, "", "", lsg, "", erg, grafik

def default(jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    if optionen != "":                                                              #hier wird typ_anf und typ_end festgelegt u.u. nach Wahl unter 'Optionen'
        typ_anf = 1
        typ_end = 1
        if stufe >= 4 or jg >= 7 or "mit" in optionen:
            typ_end = 2
        return typ_anf, typ_end
    elif eingabe != "":                                                              #wenn in Lösungen 'iniv' steht, kann die Lösung hier überprüft werden                                            
        loe = (lsg[0])
        if eingabe.replace(" ","") != loe.replace(" ",""):
            erg = loe.replace(",",".")
            eing = eingabe.replace(",",".")
            if float(erg) == float(eing):
                return 0, "Du darfst die Null am Ende nicht weglassen - <br>Die Zahl muss genau {0} Stellen hinter dem Komma haben".format(len(erg)-erg.find("."))
        else:
            return 0, "" 
    else:
        typ = random.randint(typ_anf, typ_end)  
        titel = "Titel"  
                                                                                    # hier wird die Aufgabe erstellt:
        if typ == 1:
                zahl1 = random.randint(0,2)
                text = ""
                erg = 0
                lsg = str(erg)
        else:
            pass
        return typ, titel, text, "", "", [lsg], "", erg, {'name':''}

AUFGABEN = {
    1: ergaenzen,
    2: addieren,
    3: subtrahieren,
    4: verdoppeln,
    5: halbieren,
    6: einmaleins,
    7: kopfrechnen,
    8: zahlen,
    9: malget10,
    10: runden,
    11: regeln,
    12: geometrie,
}

def aufgaben(kategorie_id, jg = 5, stufe = 3, typ_anf = 0, typ_end = 0, optionen = "", eingabe = "", lsg = ""):
    return AUFGABEN[kategorie_id](jg, stufe, typ_anf, typ_end, optionen, eingabe, lsg)

def kontrolle(eingabe, value, lsg, protokoll_id):
    if value != 0:                                      #das wird zB gebraucht beim Kürzen, wenn es nicht auf den Wert ankommt, sondern auf die Schreibweise
        if eingabe == value:
            return 1, ""
        #return abs(given - value) < decimal.Decimal('0.001')
        else:
            return -1, ""    
    else:
        if "indiv" in lsg:                              #wenn in der Liste 'loesungen' 'indiv' steht, dann wird der eingegebene Wert in der Funtion der entsprechenden Kategorie überprüft
            protokoll = get_object_or_404(Protokoll, pk = protokoll_id)
            punkte, rueckmeldung = aufgaben(protokoll.kategorie_id, eingabe=eingabe, lsg=lsg) 
            if rueckmeldung:
                return punkte, rueckmeldung             #hier kann unter 'punkte" festgelegt werden, ob es z.B. Extrapunkte oder Punktabzüge gibt
        for loe in (lsg):
            if eingabe.replace(" ","") == loe.replace(" ",""):
                return 1, ""
        else:
            return -1, ""

def get_fake_user():
    #return Schueler.objects.all().order_by('?').first()
    return Schueler.objects.all().first()

def kategorien(req):
    Protokoll.objects.filter(eingabe = "").delete()
    kategorie = Kategorie.objects.all().order_by('zeile')
    return render(req, 'core/kategorien.html', {'kategorie': kategorie})

def uebersicht(req):
    user = get_fake_user()
    summe = Zaehler.objects.filter(user=user)
    richtig = summe.aggregate(Sum('richtig'))
    richtig = richtig['richtig__sum']
    falsch = summe.aggregate(Sum('falsch'))
    falsch = falsch['falsch__sum']
    if richtig+falsch > 0:
        quote = int(falsch/(richtig+falsch)*100)
    else:
        quote = "-"
    abbr = summe.aggregate(Sum('abbrechen'))
    abbr = abbr['abbrechen__sum']
    lsg = summe.aggregate(Sum('loesung'))
    lsg = lsg['loesung__sum']
    hilfe = summe.aggregate(Sum('hilfe'))
    hilfe = hilfe['hilfe__sum']

    kategorien = []
    for kategorie in Kategorie.objects.all():
        zaehler = Zaehler.objects.filter(user=user, kategorie=kategorie).first()
        kategorien.append((kategorie, zaehler))
    return render(req, 'core/uebersicht.html', {'kategorien': kategorien, 'user':user, 'richtig':richtig, 'falsch':falsch, 'quote':quote, 'abbr':abbr, 'lsg':lsg, 'hilfe': hilfe})

def protokoll(req):
    user = get_fake_user()    
    protokoll = Protokoll.objects.filter(user=user).order_by('id').reverse()
    form = ProtokollFilter
    filter = "aktuelles Halbjahr"
    if req.method == 'POST':
        auswahl = form(req.POST)
        if auswahl.is_valid():     
            filter = auswahl.cleaned_data['filter']
            print(filter)
            if filter == "hj":
                print("OK")
            elif filter == "heute":
                protokoll = protokoll.filter(start__date = date.today())
            elif filter == "Woche":
                protokoll =  protokoll.filter(start__date__gte = date.today() - timedelta(days = 7))
    
    return render(req, 'core/protokoll.html', {'protokoll': protokoll, 'form': form, 'filter': filter})

def details(req, zeile_id):
    protokoll = get_object_or_404(Protokoll, pk = zeile_id)
    zaehler = Zaehler.objects.get(user = protokoll.user, kategorie = protokoll.kategorie)
    return render(req, 'core/details.html', {'protokoll': protokoll, 'zaehler': zaehler})

def main(req, slug):                                                        #hier läuft alles zusammen
    kategorie = get_object_or_404(Kategorie, slug = slug)
    kategorie_id = kategorie.id
    user = get_fake_user()    
    if req.method == 'POST':  
        protokoll = Protokoll.objects.get(pk = req.session.get('protokoll_id'))
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
            wertung, rueckmeldung = kontrolle(eingabe, protokoll.value, protokoll.loesung, protokoll.id)
            if wertung == 1:
            #if kontrolle(eingabe, protokoll.value, protokoll.loesung):      #Anwort richtig
                protokoll.wertung = protokoll.wertung + "r"
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
            else:  
                print(wertung)   
                print(rueckmeldung) 
                if wertung < 0:
                    messages.info(req, rueckmeldung)  
                    wertung = -1 
                                                                                 #Antwort falsch
                if wertung == -1:
                    protokoll.wertung = protokoll.wertung + "f"
                    protokoll.save()
                    zaehler.falsch += 1
                    zaehler.richtig_of  = 0
                    zaehler.save()
                    quote = int(zaehler.falsch/(zaehler.richtig+zaehler.falsch)*100)
                    msg = f'<br>richtig: {zaehler.richtig}, falsch: {zaehler.falsch}, Fehlerquote: {quote}%, EoF: {zaehler.richtig_of}/{kategorie.eof}'
                    messages.info(req, f'Die letzte Aufgabe war leider falsch! Versuche: {protokoll.tries}, {msg}')   
                    if protokoll.tries >= 3:                                            #3 mal falsch
                        messages.info(req, f'letzte Aufgabe: {protokoll.text}, Lösung: {protokoll.loesung}')                     
                        return redirect('kategorien')
                else:
                    messages.info(req, f'{rueckmeldung}')                               #gibt eine Rückmeldung wenn "indiv" bei Lösung steht  
                titel = protokoll.titel
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
        typ, titel, text, pro_text, anm, lsg, hilfe, result, grafik = aufgaben(kategorie.id, jg = user.jg, stufe = user.stufe, typ_anf = zaehler.typ_anf, typ_end = zaehler.typ_end, optionen = "") 
        if not pro_text:
            pro_text = text 
        if not titel:
            titel = kategorie.name
        halbjahr = user.halbjahr/10
        protokoll = Protokoll.objects.create(
            user = user, titel = titel, halbjahr = halbjahr, kategorie = kategorie, text = text, pro_text = pro_text, anmerkung = anm, value = result, loesung = lsg, hilfe = hilfe, grafik = grafik, individuell = ""       
        )                                                                   #Protokoll wird erstellt
        req.session['protokoll_id'] = protokoll.id    
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
    context = dict(kategorie = kategorie, typ = protokoll.typ, titel = titel, aufgnr = zaehler.aufgnr, text = text, anmerkung = anm, form = form, zaehler_id = zaehler.id, hilfe = hilfe, protokoll_id = protokoll.id, grafik = grafik)
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
    protokoll.wertung = protokoll.wertung + "a"
    protokoll.eingabe = protokoll.eingabe + "abbr."
    protokoll.save()
    return redirect('uebersicht')

def loesung(req, zaehler_id):
    zaehler = get_object_or_404(Zaehler, pk = zaehler_id)
    zaehler.loesung +=1
    zaehler.richtig_of = 0 
    protokoll = Protokoll.objects.filter(user = zaehler.user).order_by('-id').first()
    msg=f'letzte Aufgabe:<br>{protokoll.text} Lösung: {protokoll.loesung[0]}'    
    protokoll.eingabe = protokoll.eingabe + "Lsg."
    protokoll.save()
    zaehler.hinweis = msg
    zaehler.save()   
    return redirect('main', zaehler.kategorie)

def hilfe(req, zaehler_id, protokoll_id):
    zaehler = get_object_or_404(Zaehler, pk = zaehler_id)
    protokoll = get_object_or_404(Protokoll, pk = protokoll_id)
    kategorie = protokoll.kategorie
    if protokoll.value != 0:
        form = AufgabeFormZahl(req.POST)
    else:
        form = AufgabeFormStr(req.POST)
    protokoll.eingabe = protokoll.eingabe + " Hilfe "
    protokoll.save()
    zaehler.hilfe +=1
    zaehler.save()
    messages.info(req, f'Hilfe: {protokoll.hilfe}')  
    context = dict(kategorie = kategorie, typ = protokoll.typ, titel = protokoll.titel, aufgnr = zaehler.aufgnr, text = protokoll.text, anmerkung = protokoll.anmerkung, form = form, zaehler_id = zaehler.id, hilfe = protokoll.hilfe, protokoll_id = protokoll.id, grafik = protokoll.grafik)
    return render(req, 'core/aufgabe.html', context)