from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import AdvertisementForm, AdForm
from django.contrib.auth.decorators import login_required
from .models import Advertisement


def index(request):
    advertisements = Advertisement.objects.all()
    return render(request, 'index.html', {'advertisements': advertisements})

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохранение объявления в базе данных
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('index')  # Перенаправление на главную страницу
    else:
        form = AdvertisementForm()
    return render(request, 'create_ad.html', {'form': form})


def edit_ad(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.user.is_authenticated and request.user == ad.user:
        if request.method == 'POST':
            form = AdForm(request.POST, instance=ad)
            if form.is_valid():
                form.save()
                return redirect('ad_detail', ad_id=ad.id)
        else:
            form = AdForm(instance=ad)
        return render(request, 'edit_ad.html', {'form': form})
    else:
        return redirect('index')  # Или другая страница перенаправления



def ad_detail(request, ad_id):
    advertisement = get_object_or_404(Advertisement, id=ad_id)
    return render(request, 'ad_detail.html', {'advertisement': advertisement})


def profile(request):
    # Получаем профиль пользователя или возвращаем 404, если не найден
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})


def responses(request):
    return render(request, 'responses.html')


def response_detail(request, response_id):
    return render(request, 'response_detail.html', {'response_id': response_id})


from django.contrib.auth.forms import AuthenticationForm


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Редирект на другую страницу после успешного входа
                return redirect('profile')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    # Редирект на другую страницу после успешного выхода
    return redirect('index')


import random
import string

def generate_confirmation_code(length=6):
    """Генерация случайного одноразового кода указанной длины."""
    # Возможные символы для кода
    characters = string.ascii_letters + string.digits
    # Генерация случайного кода заданной длины
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

from .forms import SignUpForm
from django.core.mail import send_mail
from django.conf import settings

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя
            # Генерируем и сохраняем одноразовый код для подтверждения регистрации
            code = generate_confirmation_code()  # Генерация кода
            UserProfile.objects.create(user=user, registration_confirmation_code=code)

            # Отправляем код по электронной почте
            subject = 'Подтверждение регистрации'
            message = f'Ваш одноразовый код для подтверждения регистрации: {code}'
            from_email = settings.EMAIL_HOST_USER
            to_email = [user.email]
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            # Редирект на другую страницу после успешной регистрации
            return redirect('registration_confirmation', user_id=user.id)

    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


def registration_confirmation(request, user_id):
    if request.method == 'POST':
        confirmation_code = request.POST.get('confirmation_code')
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            if confirmation_code == user_profile.registration_confirmation_code:
                user_profile.confirmed_registration = True
                user_profile.save()
                return redirect('profile')  # Редирект на профиль после успешной регистрации
            else:
                return render(request, 'registration_confirmation.html', {'error': 'Неверный код подтверждения'})
        except UserProfile.DoesNotExist:
            return render(request, 'registration_confirmation.html', {'error': 'Ошибка при подтверждении регистрации'})
        except User.DoesNotExist:
            return render(request, 'registration_confirmation.html', {'error': 'Ошибка при подтверждении регистрации'})
    else:
        return render(request, 'registration_confirmation.html', {'user_id': user_id})



