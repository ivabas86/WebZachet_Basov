from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField

from api_rest.models import User


class CustomUserCreationForm(UserCreationForm):
    email = EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        # field_classes = {"username": UsernameField}