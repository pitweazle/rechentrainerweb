from django import forms

class AufgabeFormZahl(forms.Form):
    eingabe = forms.DecimalField(label='Ergebnis', max_digits=15,
                                decimal_places=5)

class AufgabeFormStr(forms.Form):
    eingabe = forms.CharField(label='Ergebnis')

class AuswahlForm(forms.Form):
    #name = forms.CharField(label="Auswahl")
    auswahl=forms.ChoiceField(label="Wähle aus", choices=[('mit Komma', 'mit Komma'),('ohne Komma','ohne Komma')])
