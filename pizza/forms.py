from django import forms
from .models import Pizza, Size

# class PizzaForm(forms.Form):
#     belaege=forms.MultipleChoiceField(choices=[('sal','Salami'),('pilz','Pilze'),('Oli','Oliven')], widget=forms.CheckboxSelectMultiple)
#     #belag1=forms.CharField(label='Belag 1', max_length=100, widget=forms.Textarea)
#     #belag2=forms.CharField(label='Belag 2', max_length=100)
#     size=forms.ChoiceField(label='Größe', choices=[('klein','klein'),('mittel','mittel'),('gross','groß')])

class PizzaForm(forms.ModelForm):
    #size=forms.ModelChoiceField(queryset=Size.objects, empty_label=None, widget=forms.RadioSelect)
    #labels={'size:"Größe'}
    #image=forms.ImageField()

    class Meta:
        model=Pizza
        fields=['belag1', 'belag2', 'size']
        labels={'belag2':'Belag 2', 'size':'Größe'}
        #widgets={'size':forms.CheckboxSelectMultiple}

class MultiplePizzaForm(forms.Form):
    number=forms.IntegerField(min_value=2, max_value=6)
    labels={'number:"Anzahl'}