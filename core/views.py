import decimal
import random

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from datetime import datetime

from .forms import ChallengeForm, AufgabeForm
from .models import Category, Result, Question
from .models import Kategorie, Frage, Daten
from django.http import HttpResponse, HttpResponseNotFound

NOTES = [5, 10, 20, 50, 100]


def make_task():
    low = random.uniform(0.1, 99.0)
    low = decimal.Decimal(round(low, 2))
    start = 0
    while True:
        if NOTES[start] > low:
            break
        start += 1
    high = decimal.Decimal(random.choice(NOTES[start:]))
    return low, high, high - low


def check_result(given, right):
    return abs(given - right) < decimal.Decimal('0.001')

def get_fake_user():
    return User.objects.all().first()

def index(req):
    Result.objects.filter(tries=0).delete()
    modul = Kategorie.objects.all().order_by('id')
    return render(req, 'core/index.html', {'module': modul})

def protokoll(req):
    daten = Result.objects.all().order_by('id').reverse()
    return render(req, 'core/protokoll.html', {'module': daten})

def antwort(req, antwort_id):
    antwort=Result.objects.all()[antwort_id]
    return render(req, 'core/antwort.html', {'module': antwort})

    #return HttpResponse(antwort)


def aufgabe(req, modul_id):
    category = get_object_or_404(Kategorie, pk=modul_id)
    if req.method == 'POST':
        form = AufgabeForm(req.POST)
        result = Result.objects.get(pk=req.session.get('result_id'))
        #antwort = Daten.objects.get(pk=req.session.get('antwort_id'))
        result.tries += 1
        result.save()
        if form.is_valid():
            if check_result(form.cleaned_data['result'], result.value):
                result.end = timezone.now()
                result.save()
                min, sec = divmod(result.duration, 60)
                msg = f'Zeit: {int(min)}min {int(sec)}s'
                messages.info(req, f'Richtig! Versuche: {result.tries}, {msg}')
                return redirect('modul', modul_id)
        messages.info(req, 'Leider falsch.')
        text = result.text
    else:
        question = Frage.objects.filter(
            #category=category
        ).order_by('?').first()

        # 2 Zufallszahlen erzeugen und Ergebnis ausrechnen
        low, high, result = make_task()

        text = question.text.format(low=low, high=high)
        result = Result.objects.create(
            user=get_fake_user(), value=result,
            text=text
        )
        req.session['result_id'] = result.id
        form = AufgabeForm()
    context = dict(category=category, text=text, aufgabe=aufgabe, form=form)
    return render(req, 'core/aufgabe.html', context)

def challenge(req, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if req.method == 'POST':
        form = ChallengeForm(req.POST)
        result = Result.objects.get(pk=req.session.get('result_id'))
        result.tries += 1
        result.save()
        if form.is_valid():
            if check_result(form.cleaned_data['result'], result.value):
                result.end = timezone.now()
                result.save()
                min, sec = divmod(result.duration, 60)
                msg = f'Zeit: {int(min)}min {int(sec)}s'
                messages.info(req, f'Richtig! Versuche: {result.tries}, {msg}')
                return redirect('challenge', category_id)
        messages.info(req, 'Leider falsch.')
        text = result.text
    else:
        question = Question.objects.filter(
            category=category
        ).order_by('?').first()
        # 2 Zufallszahlen erzeugen und Ergebnis ausrechnen
        low, high, result = make_task()
        text = question.text.format(low=low, high=high)
        result = Result.objects.create(
            user=get_fake_user(), value=result, category=category,
            text=text
        )
        req.session['result_id'] = result.id
        form = ChallengeForm()
    context = dict(category=category, text=text, form=form)
    return render(req, 'core/challenge.html', context)

