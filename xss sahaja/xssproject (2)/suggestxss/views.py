from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserDataForm
from .models import UserData
import joblib
from .helpers import prepare_input_data
import numpy as np
from django.contrib.auth.decorators import login_required

def new_data(request):
    if request.method == 'POST':
        form = UserDataForm(request.POST)
        if form.is_valid():
            # Save the form data
            goal = form.cleaned_data['goal']
            attackT = form.cleaned_data['attackT']
            skill = form.cleaned_data['skill']
            automation = form.cleaned_data['automation']
            platform = form.cleaned_data['platform']
            
            # Simpan data user
            user = request.user
            
            # Pisahkan ip dan port dari data yang akan diprediksi
            input_data = prepare_input_data(goal, attackT, skill, automation, platform)
            
            # Load model RandomForestClassifier
            svm_model = joblib.load('svmxss.pkl')  # Pastikan nama file model sesuai
            
            # Lakukan prediksi
            prediction = svm_model.predict(input_data)[0]
            
            # Menyimpan hasil prediksi ke dalam model
            UserData.objects.create(
                user=user, 
                goal=goal, 
                attackT=attackT, 
                skill=skill, 
                automation=automation, 
                platform=platform, 
                suggest=prediction
            )
            return redirect('success')  # Redirect ke halaman sukses
    else:
        form = UserDataForm()
    return render(request, 'suggestxss/new_data.html', {'form': form})

def success(request):
    return render(request, 'suggestxss/success.html')

def result(request):
    # Retrieve and display user's data
    data = UserData.objects.filter(user=request.user).last()
    return render(request, 'suggestxss/result.html', {'data': data})

def home(request):
    return render(request, 'suggestxss/home.html')

def user_login(request):
    # Handle login logic
    login_error = False  # Initialize login error flag
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            login_error = True

    return render(request, 'suggestxss/login.html', {'login_error': login_error})

def user_register(request):
    # Handle registration logic
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        # Create a new user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'suggestxss/register.html')

@login_required
def view_data(request):
    # Retrieve and display user's data
    data = UserData.objects.filter(user=request.user)
    return render(request, 'suggestxss/view_data.html', {'data': data})
    
@login_required
def dashboard(request):
    return render(request, 'suggestxss/dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('home')
