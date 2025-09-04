from django.contrib import admin, messages
# 1. Импортируем все наши модели в одном месте
from .models import (
    Tag, Post, PostMediaFile,
    Lot, LotMediaFile, Bid,
    LotRequest, SiteSetting
)


@admin.action(description='Одобрить выбранные заявки (создать черновики лотов)')
def approve_lot_requests(modeladmin, request, queryset):
    requests_to_process = queryset.filter(status='new')
    created_count = 0
    for lot_request in requests_to_process:
        # Создаем черновик лота
        new_lot = Lot.objects.create(
            title=lot_request.lot_title,
            description=lot_request.lot_description,
            start_price=0,
            is_approved=False  # Администратор должен будет одобрить его вручную
        )
        # Переносим медиафайлы от заявки к новому лоту
        lot_request.request_media_files.update(lot=new_lot, lot_request=None)

        lot_request.status = 'approved'
        lot_request.save()
        created_count += 1

    if created_count > 0:
        messages.success(request,
                         f"Создано {created_count} черновиков лотов. Проверьте их, установите цену и одобрите для показа.")
    else:
        messages.warning(request, "Не было выбрано ни одной новой заявки для обработки.")


@admin.action(description='Отклонить выбранные заявки')
def reject_lot_requests(modeladmin, request, queryset):
    updated_count = queryset.filter(status='new').update(status='rejected')
    messages.success(request, f"Успешно отклонено {updated_count} новых заявок.")


@admin.action(description='Одобрить выбранные лоты для показа на сайте')
def approve_lots_for_display(modeladmin, request, queryset):
    updated_count = queryset.update(is_approved=True)
    messages.success(request, f"Успешно одобрено для показа {updated_count} лотов.")


# --- 2. Определяем Inline-классы ---

class PostMediaFileInline(admin.TabularInline):
    model = PostMediaFile
    extra = 1


class LotMediaFileInlineForLot(admin.TabularInline):
    model = LotMediaFile
    extra = 1
    fk_name = 'lot'


class LotMediaFileInlineForRequest(admin.TabularInline):
    model = LotMediaFile
    extra = 1
    fk_name = 'lot_request'


# --- 3. Регистрируем модели и их отображение в админке ---

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_pinned', 'created_at')
    list_filter = ('is_pinned',)
    inlines = [PostMediaFileInline]


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_price', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('title', 'description')
    inlines = [LotMediaFileInlineForLot]
    actions = [approve_lots_for_display]
    list_editable = ('start_price', 'is_approved')


@admin.register(LotRequest)
class LotRequestAdmin(admin.ModelAdmin):
    list_display = ('lot_title', 'author_name', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    readonly_fields = (
        'author_name', 'author_email', 'mobile_phone', 'reestr_number',
        'lot_title', 'lot_description', 'created_at'
    )
    inlines = [LotMediaFileInlineForRequest]
    actions = [approve_lot_requests, reject_lot_requests]


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('lot', 'bidder_name', 'amount', 'created_at')
    list_filter = ('lot', 'created_at')
    search_fields = ('bidder_name', 'lot__title')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('main_title', 'subtitle', 'auction_email')

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()


# Простая регистрация для моделей без сложных настроек
admin.site.register(Tag)
