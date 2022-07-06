from django import forms
from .models import Kategorie, Auswahl, Zaehler

class AufgabeFormZahl(forms.Form):
    eingabe = forms.DecimalField(label='Ergebnis', max_digits=15,
                                decimal_places=5, widget=forms.NumberInput(attrs={'autofocus': True}))
    
class AufgabeFormStr(forms.Form):
    eingabe = forms.CharField(label='Ergebnis', localize=True, widget=forms.TextInput(attrs={'autofocus': True}))
    

class AuswahlForm(forms.Form):
    optionen=forms.ModelMultipleChoiceField(queryset=Kategorie.objects, widget=forms.CheckboxSelectMultiple, required=False)
    def __init__(self, *args, **kwargs):
        kategorie = kwargs.pop('kategorie')
        super().__init__(*args, **kwargs)
        self.fields['optionen'].queryset = kategorie.auswahl_set.all()

