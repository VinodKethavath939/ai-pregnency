
from django.db import models

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    lmp_date = models.DateField(help_text="Last Menstrual Period")

    def __str__(self):
        return self.name

class SymptomLog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date_logged = models.DateField(auto_now_add=True)
    symptom = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.name} - {self.symptom}"



class ChatLog(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - User: {self.user_message}"
