
from django.shortcuts import render, redirect
from .forms import UserProfileForm, SymptomLogForm
from .models import UserProfile
from datetime import timedelta

def index(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            return redirect('result', profile_id=profile.id)
    else:
        form = UserProfileForm()
    return render(request, 'index.html', {'form': form})

def result(request, profile_id):
    user = UserProfile.objects.get(id=profile_id)
    due_date = user.lmp_date + timedelta(days=280)
    return render(request, 'result.html', {'user': user, 'due_date': due_date})

def log_symptom(request):
    response = None
    symptom_text = ''
    if request.method == 'POST':
        symptom_text = request.POST.get('symptom')
        
        # Example: Get a response from your API or assistant logic
        response = generate_pregnancy_content_payload(symptom_text)

    return render(request, 'log_symptom.html', {
        'response': response,
        'symptom_text': symptom_text
    })


def tips(request):
    return render(request, 'tips.html')

from .models import ChatLog
from datetime import datetime


import requests
import json

def generate_pregnancy_content_payload(user_question, api_key):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                     {
                        "text": (
                            f"You are a highly knowledgeable and compassionate pregnancy assistant. "
                            f"Answer the following question in a clear, medically accurate, and supportive manner. "
                            f"Include tips, potential risks (if any), and when to consult a healthcare professional. "
                            f"Question: {user_question}"
                        )
                    }                ]
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes
        output = response.json()
        return output['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.RequestException as e:
        return {"url": url, "payload": payload, "error": f"API request failed: {e}"}

def chat_view(request):
    if 'chats' not in request.session:
        request.session['chats'] = []

    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            # Append user message
            request.session['chats'].append({'role': 'user', 'user_message': user_message})

            # Call your AI function
            response = generate_pregnancy_content_payload(user_message,'AIzaSyBpLetJX8VwYq3QHc_icj9po2DWiQRqMdY')
            bot_message = 'Sorry, I could not process your request.'
            if response :
                bot_message = response

            # Append bot response
            request.session['chats'].append({'role': 'bot', 'bot_response': bot_message})
            request.session.modified = True  # Mark session as modified to save changes

    # Format for rendering: pair each user+bot message into a single dict
    chat_pairs = []
    temp = {}
    for chat in request.session.get('chats', []):
        if chat['role'] == 'user':
            temp = {'user_message': chat['user_message']}
        elif chat['role'] == 'bot' and temp:
            temp['bot_response'] = chat['bot_response']
            chat_pairs.append(temp)
            temp = {}
    return render(request, 'chat.html', {'chats': chat_pairs})
