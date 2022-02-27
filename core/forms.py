from django import forms


class AufgabeForm(forms.Form):
    eingabe = forms.DecimalField(label='Ergebnis', max_digits=15,
                                decimal_places=5)

