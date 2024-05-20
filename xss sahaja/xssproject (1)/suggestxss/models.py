from django.db import models
from django.contrib.auth.models import User

class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.IntegerField(choices=[(0, 'Web-application'), (1, 'API'), (2, 'Mobile-app')])
    attackT = models.IntegerField(choices=[(0, 'Reflected'), (1, 'Stored'), (2, 'Dom-based')])
    skill = models.IntegerField(choices=[(0, 'Beginner'), (1, 'Intermediate'), (2, 'Advanced')])
    automation = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    platform = models.IntegerField(choices=[(0, 'Windows'), (1, 'Linux'), (2, 'MacOS')])
    suggest = models.IntegerField(choices=[(0, 'Nmap & OWASP ZAP'), (1, 'Nmap & XSSser')])

    def __str__(self):
        return f'{self.user.username} - {self.goal}'
