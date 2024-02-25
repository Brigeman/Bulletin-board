from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Response
from .models import Advertisement


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    nickname = forms.CharField(max_length=30, help_text='Required. Enter your nickname.')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'nickname', 'password1', 'password2')


class AdvertisementForm(forms.ModelForm):
    # Добавляем поле выбора категории
    CATEGORY_CHOICES = [
        ('Танки', 'Танки'),
        ('Хилы', 'Хилы'),
        ('ДД', 'ДД'),
        ('Торговцы', 'Торговцы'),
        ('Гилдмастеры', 'Гилдмастеры'),
        ('Квестгиверы', 'Квестгиверы'),
        ('Кузнецы', 'Кузнецы'),
        ('Кожевники', 'Кожевники'),
        ('Зельевары', 'Зельевары'),
        ('Мастера заклинаний', 'Мастера заклинаний'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES)

    class Meta:
        model = Advertisement
        fields = ['title', 'text', 'image', 'video', 'category']


class AdForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'text', 'image', 'video', 'category']  # Добавьте поля, которые можно редактировать


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']
