from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from .forms import PizzaForm, MultiplePizzaForm
from django.forms import formset_factory

def pizza(req):
    return render(req, 'pizza/home.html')

def order(req):
    multiple_form=MultiplePizzaForm()
    if req.method=='POST':
        #return HttpResponse("OK")
        filled_form=PizzaForm(req.POST)
        if filled_form.is_valid():
            filled_form.save()
            note="Danke für die Bestellung! Deine %se %s-und-%s-Pizza ist unterwegs!" %(
            filled_form.cleaned_data['size'],
            filled_form.cleaned_data['belag1'],
            filled_form.cleaned_data['belag2'],)
            new_form=PizzaForm()
            return render(req, 'pizza/order.html', {'pizzaform':new_form, 'note':note, 'multiple_form':multiple_form})
    else:
        form=PizzaForm()
        return render(req, 'pizza/order.html', {'pizzaform':form, 'multiple_form':multiple_form})

def pizzas(request):
    number_of_pizzas = 2
    filled_multiple_pizza_form = MultiplePizzaForm(request.GET)
    if filled_multiple_pizza_form.is_valid():
        number_of_pizzas = filled_multiple_pizza_form.cleaned_data['number']
    PizzaFormSet = formset_factory(PizzaForm, extra=number_of_pizzas)
    formset = PizzaFormSet()
    if request.method == "POST":
        filled_formset = PizzaFormSet(request.POST)
        if(filled_formset.is_valid()):
            for form in filled_formset:
                print(form.cleaned_data['belag1'])
            note="Pizzen wurden bestellt"
        else:
            note="keine Bestellung"
        return render(request, 'pizza/pizzas.html', {'note':note, 'formset':formset})
    else:
        return render(request, 'pizza/pizzas.html', {'formset':formset})
       
