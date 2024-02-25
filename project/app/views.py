from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import AdvertisementForm, AdForm, ResponseForm
from django.contrib.auth.decorators import login_required
from .models import Advertisement, Response, Notification
from django.http import HttpResponseNotAllowed
from .forms import SignUpForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
import random
import string


def index(request):
    advertisements = Advertisement.objects.all()
    # Получаем значение фильтра из параметра запроса
    category_filter = request.GET.get('category_filter')

    # Если указана категория для фильтрации, фильтруем объявления
    if category_filter:
        advertisements = advertisements.filter(category=category_filter)
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


@login_required
def delete_ad(request, ad_id):
    ad = get_object_or_404(Advertisement, id=ad_id)
    if request.user == ad.user:
        ad.delete()
        messages.success(request, 'Объявление успешно удалено.')
    else:
        messages.error(request, 'У вас нет прав на удаление этого объявления.')
    return redirect('profile')


@login_required
def profile(request):
    # Получаем профиль пользователя или возвращаем 404, если не найден
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Получаем все объявления пользователя
    user_advertisements = Advertisement.objects.filter(user=request.user)

    # Получаем значение фильтра из параметра запроса
    category_filter = request.GET.get('category_filter')

    # Если указана категория для фильтрации, фильтруем объявления пользователя
    if category_filter:
        user_advertisements = user_advertisements.filter(category=category_filter)

    # Получаем отклики на объявления пользователя
    user_responses = Response.objects.filter(advertisement__in=user_advertisements)

    # Если указана категория для фильтрации откликов, фильтруем отклики
    if category_filter:
        user_responses = user_responses.filter(advertisement__category=category_filter)

    return render(request, 'profile.html', {'user_profile': user_profile, 'user_advertisements': user_advertisements, 'user_responses': user_responses})


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


def generate_confirmation_code(length=6):
    """Генерация случайного одноразового кода указанной длины."""
    # Возможные символы для кода
    characters = string.ascii_letters + string.digits
    # Генерация случайного кода заданной длины
    code = ''.join(random.choice(characters) for _ in range(length))
    return code


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


@login_required
def send_response(request, ad_id):
    advertisement = get_object_or_404(Advertisement, id=ad_id)
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.advertisement = advertisement
            response.save()

            # Отправляем уведомление на электронную почту владельцу объявления
            subject = 'Новый отклик на ваше объявление'
            message = f'Пользователь {request.user.username} оставил отклик на ваше объявление "{advertisement.title}": {response.text}'
            from_email = settings.EMAIL_HOST_USER
            to_email = [advertisement.user.email]
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            return redirect('ad_detail', ad_id=ad_id)
    else:
        form = ResponseForm()
    return render(request, 'send_response.html', {'form': form, 'advertisement': advertisement})


@login_required
def user_responses(request):
    search_query = request.GET.get('search_query')
    user_advertisements = Advertisement.objects.filter(user=request.user)

    if search_query:
        user_responses = Response.objects.filter(advertisement__in=user_advertisements, text__icontains=search_query, accepted=False)
    else:
        user_responses = Response.objects.filter(advertisement__in=user_advertisements, accepted=False)

    return render(request, 'user_responses.html', {'user_responses': user_responses})


def response_detail(request, response_id):
    response = get_object_or_404(Response, id=response_id)
    return render(request, 'response_detail.html', {'response': response})


@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)
    if request.method == 'POST':
        response.delete()
        return redirect('user_responses')  # Перенаправляем пользователя на страницу с откликами
    # Обработка случая, когда метод запроса не POST
    return HttpResponseNotAllowed(['POST'])


@login_required
def accept_response(request, response_id):
    response = get_object_or_404(Response, id=response_id)
    if request.method == 'POST':
        notification_text = "Ваш отклик был принят."
        Notification.objects.create(user=response.user, text=notification_text)
        response.accepted = True  # Помечаем отклик как принятый
        response.save()

        # Отправляем уведомление пользователю
        subject = 'Ваш отклик был принят'
        message = 'Ваш отклик на объявление "{}" был принят.'.format(response.advertisement.title)
        from_email = settings.EMAIL_HOST_USER
        to_email = [response.user.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False)

        messages.success(request, 'Отклик успешно принят')
        return redirect('user_responses')  # Перенаправляем пользователя на страницу с откликами
    return HttpResponseNotAllowed(['POST'])
