# from django.shortcuts import render, redirect
# from .forms import RegisterForm

# def register(response):
#     if response.method == "POST":
#         form = RegisterForm(response.POST)
#     if form.is_valid():
#         form.save()
#         return redirect("/home")
#     else:
#         form = RegisterForm()
#     return render(response, "register/register.html", {"form":form})

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    
