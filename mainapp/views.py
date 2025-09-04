# mainapp/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from .models import Lot, SiteSetting, Post, PostMediaFile, LotMediaFile, LotRequest
from .forms import LotRequestForm, BidForm
from django.db.models import Q
import json # <-- Добавьте этот импорт
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
def index_view(request):
    all_posts = Post.objects.all()
    context = {'posts': all_posts}
    return render(request, 'mainapp/index.html', context)


# Эта функция-декоратор проверяет, является ли пользователь администратором (суперпользователем)
def is_admin(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_admin)
@require_POST
def update_post_api(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # 1. Обновляем текстовые поля и чекбокс из request.POST
    post.title = request.POST.get('title', post.title)
    post.content = request.POST.get('content', post.content)
    # Для чекбокса 'is_pinned' будет в POST, если он отмечен
    post.is_pinned = 'is_pinned' in request.POST

    # 2. Обрабатываем удаление старых файлов
    # Фронтенд пришлет нам строку с ID файлов для удаления, например "1,5,12"
    if 'deleted_media_ids' in request.POST:
        ids_to_delete = request.POST.get('deleted_media_ids').split(',')
        if ids_to_delete:
            # Безопасно удаляем только те файлы, которые принадлежат этому посту
            post.media_files.filter(pk__in=ids_to_delete).delete()

    # 3. Обрабатываем загрузку НОВЫХ файлов из request.FILES
    # Фронтенд пришлет их под именем 'new_media_files'
    if 'new_media_files' in request.FILES:
        for uploaded_file in request.FILES.getlist('new_media_files'):
            PostMediaFile.objects.create(post=post, file=uploaded_file)

    post.save()
    return JsonResponse({'success': True})


def auction_list_view(request):
    lots = Lot.objects.filter(is_approved=True)
    context = {
        'lots': lots,
        'bid_options': [1000, 2000, 3000, 4000, 5000, 10000, 15000, 20000, 25000, 50000],
        'pending_requests': None  # По умолчанию заявок нет
    }

    # Если пользователь - админ, добавляем в контекст необработанные заявки
    if request.user.is_authenticated and request.user.is_superuser:
        context['pending_requests'] = LotRequest.objects.filter(status='new').prefetch_related('media_files')

    return render(request, 'mainapp/auction_list.html', context)

@require_POST # Разрешаем только POST-запросы
def create_lot_request_view(request):
    form = LotRequestForm(request.POST, request.FILES)
    if form.is_valid():
        lot_request = form.save(commit=False)
        lot_request.save()
        files = request.FILES.getlist('lot_files')
        for uploaded_file in files:
            LotMediaFile.objects.create(lot_request=lot_request, file=uploaded_file)
        # Логика отправки письма
        try:
            # 1. Получаем ЕДИНСТВЕННЫЙ объект настроек (pk=1)
            settings = SiteSetting.objects.get(pk=1)
            # 2. Берем email из его ЯВНОГО поля auction_email
            target_email = settings.auction_email
            subject = f"Новая заявка на лот: {form.cleaned_data['lot_title']}"
            message = f"""
            От: {form.cleaned_data['author_name']} ({form.cleaned_data['author_email']})
            Телефон: {form.cleaned_data['mobile_phone']}
            Реестровый номер: {form.cleaned_data.get('reestr_number', 'Не указан')}
            Название: {form.cleaned_data['lot_title']}
            Описание: {form.cleaned_data['lot_description']}
            Количество прикрепленных файлов: {len(request.FILES.getlist('lot_files'))}
            """
            send_mail(subject, message, 'noreply@your-site.com', [target_email])
        except SiteSetting.DoesNotExist:
            # Если email в админке не настроен, просто пропускаем
            pass
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})

@require_POST
def create_bid_view(request, lot_id):
    lot = get_object_or_404(Lot, pk=lot_id)
    form = BidForm(request.POST)
    if form.is_valid():
        bid = form.save(commit=False)
        bid.lot = lot
        bid.save()
        # Логика отправки письма
        try:
            target_email = SiteSetting.objects.get(name='auction_email').value
            subject = f"Новая ставка на лот: {lot.title}"
            message = f"""
            От: {form.cleaned_data['bidder_name']} ({form.cleaned_data['bidder_email']})
            Лот: {lot.title}
            Ставка: {form.cleaned_data['amount']} руб.
            """
            send_mail(subject, message, 'noreply@your-site.com', [target_email])
        except SiteSetting.DoesNotExist:
            pass
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})

def history_view(request):
    history_posts = Post.objects.filter(tags__name__icontains='Бал')
    context = {'posts': history_posts, 'page_title': 'Как это было'}
    return render(request, 'mainapp/post_list.html', context)

def media_gallery_view(request):
    media_posts = Post.objects.filter(Q(image_url__isnull=False) | Q(video_url__isnull=False))
    context = {'posts': media_posts, 'page_title': 'Фото и Видео'}
    return render(request, 'mainapp/post_list.html', context)

def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Логика увеличения счетчика
    post.views_count += 1
    post.save(update_fields=['views_count'])
    context = {'post': post}
    return render(request, 'mainapp/post_detail.html', context)

def lot_detail_view(request, pk):
    lot = get_object_or_404(Lot, pk=pk)
    lot.views_count += 1
    lot.save(update_fields=['views_count'])
    context = {'lot': lot}
    return render(request, 'mainapp/lot_detail.html', context)

# НОВАЯ VIEW ДЛЯ СТРАНИЦЫ ПОЛИТИКИ
def policy_view(request):
    return render(request, 'mainapp/policy.html')


@user_passes_test(is_admin)  # Защищаем, доступ только для админов
@require_POST
def create_post_api(request):
    try:
        # Создаем новый пост с данными из request.POST
        new_post = Post.objects.create(
            title=request.POST.get('title', 'Новый пост'),
            content=request.POST.get('content', ''),
            is_pinned='is_pinned' in request.POST
        )

        # Добавляем теги (если они переданы)
        tag_ids = request.POST.getlist('tags')
        if tag_ids:
            new_post.tags.set(tag_ids)

        # Добавляем медиафайлы из request.FILES
        if 'media_files' in request.FILES:
            for uploaded_file in request.FILES.getlist('media_files'):
                PostMediaFile.objects.create(post=new_post, file=uploaded_file)

        return JsonResponse({'success': True, 'message': 'Пост успешно создан.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@user_passes_test(is_admin)
def get_lot_request_details_api(request, request_id):
        """Возвращает HTML для модального окна с деталями заявки."""
        lot_request = get_object_or_404(LotRequest, pk=request_id)
        # Мы рендерим небольшой кусок HTML на сервере и отдаем его как JSON
        html = render_to_string('mainapp/partials/lot_request_modal.html', {'request': lot_request})
        return JsonResponse({'html': html})

@user_passes_test(is_admin)
@require_POST
def process_lot_request_api(request, request_id):
        """Одобряет или отклоняет заявку."""
        lot_request = get_object_or_404(LotRequest, pk=request_id)
        data = json.loads(request.body)
        action = data.get('action')  # 'approve' или 'reject'

        if action == 'reject':
            lot_request.status = 'rejected'
            lot_request.save()
            return JsonResponse({'success': True, 'message': 'Заявка отклонена.'})

        elif action == 'approve':
            # Создаем лот на основе отредактированных данных
            new_lot = Lot.objects.create(
                title=data.get('lot_title', lot_request.lot_title),
                description=data.get('lot_description', lot_request.lot_description),
                start_price=0,  # Цену нужно будет выставить позже
                is_approved=False  # Не публикуем сразу, даем админу шанс проверить
            )
            # Переносим медиафайлы от заявки к лоту
            lot_request.request_media_files.update(lot=new_lot, lot_request=None)

            lot_request.status = 'approved'
            lot_request.save()
            return JsonResponse({'success': True, 'message': 'Заявка одобрена, лот создан.'})

        return JsonResponse({'success': False, 'message': 'Неизвестное действие.'}, status=400)