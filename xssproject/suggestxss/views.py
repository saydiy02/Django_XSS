from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserDataForm
from .models import UserData, Feedback, ToolResult
import joblib
from .helpers import prepare_input_data
import numpy as np
from django.contrib.auth.decorators import login_required
import subprocess
import json
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import os
import re
from ansi2html import Ansi2HTMLConverter

def load_model():
    try:
        with open('svmxss.pkl', 'rb') as f:
            model = joblib.load(f)
    except FileNotFoundError:
        model = retrain_model()
    return model

def retrain_model():
    data = UserData.objects.all()
    if not data:
        return None

    X = [[d.goal, d.attackT, d.skill, d.automation, d.platform] for d in data]
    y = [d.suggest for d in data]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = SVC()
    model.fit(X_train, y_train)
    
    with open('svmxss.pkl', 'wb') as f:
        joblib.dump(model, f)
    
    return model


def delete_data(request, data_id):
    data_to_delete = get_object_or_404(UserData, pk=data_id)
    if data_to_delete.user == request.user:
        data_to_delete.delete()
        return redirect('view_data')
    else:        
        return HttpResponseForbidden("You are not allowed to delete this asset.")
    
@login_required
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
            #svm_model = joblib.load('svmxss.pkl')  # Pastikan nama file model sesuai
            svm_model = load_model()
            # Lakukan prediksi
            prediction = svm_model.predict(input_data)[0]
            
            # Menyimpan hasil prediksi ke dalam model
            user_data = UserData.objects.create(
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
    feedback = Feedback.objects.filter(user_data=data).last() if data else None
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

    
@login_required
def nmap_tool(request):
    if request.method == 'POST':
       target = request.POST.get('target')
       if target:
          result = subprocess.run(['nmap', target], capture_output=True, text=True)
          output = result.stdout
          
          ToolResult.objects.create(user=request.user, tool_name='Nmap', target=target, result=output)
       else:
          output = "No target specified."
    else:
       output = None
    return render(request, 'suggestxss/nmap_tool.html', {'output': output})
    

def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'''
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by a control sequence
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    ''', re.VERBOSE)
    return ansi_escape.sub('', text)

@csrf_exempt
def run_xsstrike(request):
    if request.method == 'POST':
        url = request.POST.get('url', '')
        if not url:
            return render(request, 'suggestxss/run_xsstrike.html', {'error': 'No URL provided'})

        try:
            # Run XSStrike using subprocess
            result = subprocess.run(
                ['python3', os.path.expanduser('~/XSStrike/xsstrike.py'), '-u', url, '--crawl'],
                capture_output=True, text=True, check=True
            )
            output = remove_ansi_escape_sequences(result.stdout)
            
            ToolResult.objects.create(user=request.user, tool_name='XSStrike', target=url, result=output)
            
        except subprocess.CalledProcessError as e:
            return render(request, 'suggestxss/run_xsstrike.html', {'error': str(e)})

        return render(request, 'suggestxss/run_xsstrike.html', {'output': output})

    return render(request, 'suggestxss/run_xsstrike.html')

@csrf_exempt
def run_pwnxss(request):
    if request.method == 'POST':
        url = request.POST.get('url', '')
        if not url:
            return render(request, 'suggestxss/run_pwnxss.html',{'error': 'No URL provided'})

        try:
            # Run pwnxss using subprocess
            result = subprocess.run(
                ['python3', os.path.expanduser('~/PwnXSS/pwnxss.py'), '--single', url],
                capture_output=True, text=True, check=True
            )
            output = result.stdout
            
            start_marker = "Checking connection to:"
            if start_marker in output:
                output = output[output.index(start_marker):]

            conv = Ansi2HTMLConverter()
            html_output = conv.convert(output, full=False)
            
            ToolResult.objects.create(user=request.user, tool_name='PwnXSS', target=url, result=html_output)
            
        except subprocess.CalledProcessError as e:
            return JsonResponse({'error': str(e)}, status=500)

        return render(request, 'suggestxss/run_pwnxss.html',{'output': html_output})

    return render(request, 'suggestxss/run_pwnxss.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def tool_results(request):
    results = ToolResult.objects.filter(user=request.user).order_by('-created_at')
    if not results:
        message = "No tool results found."
    else:
        message = None
    return render(request, 'suggestxss/tool_results.html', {'results': results, 'message': message})


@csrf_exempt
@login_required
def submit_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            agree = data.get('agree')
            preferred_suggestion = data.get('preferred_suggestion', None)
            user_data = UserData.objects.filter(user=request.user).last()
            
            if user_data:
                if agree:
                    Feedback.objects.create(user_data=user_data, agree=True, preferred_suggestion=user_data.suggest)
                else:
                    Feedback.objects.create(user_data=user_data, agree=False, preferred_suggestion=preferred_suggestion)
                
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'message': 'No user data found'}, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'failed', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=405)