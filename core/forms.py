from django import forms


class AufgabeForm(forms.Form):
    eingabe = forms.DecimalField(label='Ergebnis', max_digits=10,
                                decimal_places=2)