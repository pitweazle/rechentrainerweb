from django import forms
from .models import Kategorie, Auswahl, Zaehler

class AufgabeFormZahl(forms.Form):
    eingabe = forms.DecimalField(label='Ergebnis', max_digits=15,
                                decimal_places=5)

class AufgabeFormStr(forms.Form):
    eingabe = forms.CharField(label='Ergebnis')

class AuswahlForm(forms.Form):
    optionen = forms.ModelMultipleChoiceField(queryset=Kategorie.objects, widget=forms.CheckboxSelectMultiple, required=False)
    #optionen=forms.ModelChoiceField(queryset=Kategorie.objects, widget=forms.RadioSelect)
    def __init__(self, *args, **kwargs):
        kategorie = kwargs.pop('kategorie')
        super().__init__(*args, **kwargs)
        self.fields['optionen'].queryset = kategorie.auswahl_set.all()
