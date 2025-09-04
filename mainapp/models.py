from django.db import models
from django.contrib.auth.models import User

# --- Модель для тегов ---
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название тега")
    # Счетчик для сортировки по актуальности
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Количество использований")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        # Сортировка: сначала самые используемые, потом по алфавиту
        ordering = ['-usage_count', 'name']


# --- НОВАЯ МОДЕЛЬ для медиафайлов ПОСТОВ ---
class PostMediaFile(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='media_files')
    # Используем FileField для загрузки любых файлов (картинки, видео)
    file = models.FileField(upload_to='post_media/', verbose_name="Файл")

    @property
    def is_video(self):
        video_extensions = ['.mp4', '.webm', '.mov', '.avi']
        if not self.file:
            return False
        file_name = self.file.name.lower()
        return any(file_name.endswith(ext) for ext in video_extensions)

    def __str__(self):
        return f"Медиафайл для поста: {self.post.title}"

# --- НОВАЯ МОДЕЛЬ для медиафайлов ЛОТОВ ---
class LotMediaFile(models.Model):
    # Связь с уже созданным лотом.
    # null=True, blank=True делают эту связь НЕОБЯЗАТЕЛЬНОЙ.
    lot = models.ForeignKey('Lot', on_delete=models.CASCADE, related_name='media_files', null=True, blank=True)

    # Связь с заявкой. Тоже НЕОБЯЗАТЕЛЬНАЯ.
    lot_request = models.ForeignKey('LotRequest', on_delete=models.SET_NULL, related_name='media_files', null=True,
                                    blank=True)

    file = models.FileField(upload_to='lot_media/')  # Файлы от лотов и заявок будут в одной папке

    def __str__(self):
        if self.lot:
            return f"Медиафайл для лота: {self.lot.title}"
        elif self.lot_request:
            return f"Медиафайл для заявки: {self.lot_request.lot_title}"
        return "Непривязанный медиафайл"
    @property
    def is_video(self):
        video_extensions = ['.mp4', '.webm', '.mov', '.avi']
        if not self.file:
            return False
        file_name = self.file.name.lower()
        return any(file_name.endswith(ext) for ext in video_extensions)


# --- ИЗМЕНЯЕМ МОДЕЛЬ Post ---
class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")

    # УДАЛЯЕМ старые поля image_url и video_url
    # image_url = models.URLField(...)
    # video_url = models.URLField(...)

    is_pinned = models.BooleanField(default=False, verbose_name="Закрепить новость")
    views_count = models.IntegerField(default=0, verbose_name="Количество просмотров")

    # ... остальное без изменений ...
    class Meta:
        # Теперь самые важные посты - закрепленные
        ordering = ['-is_pinned', '-created_at']
# --- Модель для лотов аукциона (немного изменена) ---
class Lot(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название лота")
    description = models.TextField(verbose_name="Описание")
    # УБИРАЕМ image_url, так как теперь у нас есть MediaFile
    # image_url = models.URLField(...)
    start_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Начальная цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата выставления")
    views_count = models.IntegerField(default=0, verbose_name="Количество просмотров")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено для показа")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Лот"
        verbose_name_plural = "Лоты"
        ordering = ['-created_at']




# --- НОВАЯ МОДЕЛЬ для хранения заявок на добавление лота ---
class LotRequest(models.Model):
    author_name = models.CharField(max_length=150, verbose_name="ФИО")
    mobile_phone=models.CharField(max_length=13, verbose_name="Номер телефона")
    reestr_number=models.CharField(max_length=6, verbose_name="Реестровый номер", blank=True, null=True)
    author_email = models.EmailField(verbose_name="Электронная почта")

    lot_title = models.CharField(max_length=200, verbose_name="Название лота")
    lot_description = models.TextField(verbose_name="Описание лота")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('approved', 'Одобрена (Лот создан)'),
        ('rejected', 'Отклонена'),
    ]

    # А это само поле, которое Django не смог найти
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус заявки"
    )
    privacy_policy_accepted = models.BooleanField(default=False, verbose_name="Согласие на обработку ПД")

    def __str__(self):
        return f"Заявка на лот '{self.lot_title}' от {self.author_name}"



# --- Модель для ставок (изменена для анонимных ставок) ---
class Bid(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="bids", verbose_name="Лот")
    # Заменяем user на поля для ФИО и почты
    bidder_name = models.CharField(max_length=150, verbose_name="ФИО/Псевдоним участника")
    bidder_email = models.EmailField(verbose_name="Электронная почта участника")

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма ставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата ставки")

    def __str__(self):
        return f"Ставка от {self.bidder_name} на {self.lot.title}"

    class Meta:
        verbose_name = "Ставка"
        verbose_name_plural = "Ставки"
        ordering = ['-created_at']


# --- НОВАЯ МОДЕЛЬ для настроек сайта (например, email для уведомлений) ---
# Для этого лучше использовать пакет django-solo, но для простоты сделаем так:
class SiteSetting(models.Model):
    # Вместо name/value делаем явные поля - это надежнее
    main_title = models.CharField(max_length=100, default="Зимний бал", verbose_name="Главный заголовок")
    subtitle = models.CharField(max_length=255, blank=True, verbose_name="Подпись под заголовком")
    auction_email = models.EmailField(blank=True, verbose_name="Email для уведомлений с аукциона")
    def __str__(self):
        return "Основные настройки сайта"

    # Трюк, чтобы в админке была только одна запись с настройками
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# Эта функция будет вызываться каждый раз, когда меняются теги у поста
@receiver(m2m_changed, sender=Post.tags.through)
def update_tag_usage_count(sender, instance, action, **kwargs):
    # Нас интересуют действия только после добавления или удаления тегов
    if action == "post_add":
        for tag in instance.tags.all():
            tag.usage_count += 1
            tag.save()
    if action == "post_remove":
        # pk_set содержит ID тегов, которые были удалены
        pk_set = kwargs.get('pk_set')
        if pk_set:
            tags_to_update = Tag.objects.filter(pk__in=pk_set)
            for tag in tags_to_update:
                tag.usage_count -= 1
                tag.save()