from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import eingabe

def forum(req):
    # if req.method=='POST':
    #     eingabe=req.POST['username']
    #     print(eingabe)
    #     return HttpResponseRedirect("/eingabe")
    # else:
    #     return render(req, "forum/forum.html")

    form=eingabe()
    return render(req, "forum/forum.html", {"form": form})

def eingabe(req):
    return render(req, "forum/thankyou.html")
