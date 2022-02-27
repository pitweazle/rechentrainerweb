from django import forms


class AufgabeFormZahl(forms.Form):
    eingabe = forms.DecimalField(label='Ergebnis', max_digits=15,
                                decimal_places=5)

class AufgabeFormStr(forms.Form):
    eingabe = forms.CharField(label='Ergebnis')