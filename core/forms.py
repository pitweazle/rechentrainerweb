from django import forms


class ChallengeForm(forms.Form):
    result = forms.DecimalField(label='Ergebnis', max_digits=10,
                                decimal_places=2)
