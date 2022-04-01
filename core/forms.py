from django import forms
<<<<<<< HEAD
from .models import Kategorie, Auswahl, Zaehler
=======
>>>>>>> 077ad612518978bb87d7db2e0d84a1163ef49987

class AufgabeFormZahl(forms.Form):
    eingabe = forms.DecimalField(label='Ergebnis', max_digits=15,
                                decimal_places=5)

class AufgabeFormStr(forms.Form):
    eingabe = forms.CharField(label='Ergebnis')

class AuswahlForm(forms.Form):
<<<<<<< HEAD
    optionen = forms.ModelMultipleChoiceField(queryset=Kategorie.objects, widget=forms.CheckboxSelectMultiple, required=False)
    #optionen=forms.ModelChoiceField(queryset=Kategorie.objects, widget=forms.RadioSelect)
    def __init__(self, *args, **kwargs):
        kategorie = kwargs.pop('kategorie')
        super().__init__(*args, **kwargs)
        self.fields['optionen'].queryset = kategorie.auswahl_set.all()
=======
    #name = forms.CharField(label="Auswahl")
    auswahl=forms.ChoiceField(label="Wähle aus", choices=[('mit Komma', 'mit Komma'),('ohne Komma','ohne Komma')])
>>>>>>> 077ad612518978bb87d7db2e0d84a1163ef49987
