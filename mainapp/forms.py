# mainapp/forms.py
from django import forms
from .models import LotRequest, Bid


class LotRequestForm(forms.ModelForm):
    # 1. Объявляем ТОЛЬКО те поля, которых НЕТ в модели LotRequest
    lot_files = forms.FileField(
        label="Прикрепите фото/видео",

        required=True
    )

    class Meta:
        model = LotRequest
        # 2. Перечисляем ВСЕ поля из модели, которые должна обрабатывать форма.
        # Теперь 'privacy_policy_accepted' здесь, и Django сам создаст для него
        # правильное поле BooleanField на основе модели.
        fields = [
            'author_name', 'mobile_phone', 'reestr_number', 'author_email',
            'lot_title', 'lot_description', 'privacy_policy_accepted'
        ]

    # 3. Дополнительная валидация
    # Этот метод будет вызван во время form.is_valid()
    def clean_privacy_policy_accepted(self):
        data = self.cleaned_data['privacy_policy_accepted']
        if not data:
            # Если галочка не поставлена, вызываем ошибку валидации
            raise forms.ValidationError("Вы должны согласиться с условиями обработки персональных данных.")
        return data



class BidForm(forms.ModelForm):
    # Создаем поле с выбором ставок
    BID_CHOICES = [(i, f"{i} руб.") for i in range(5000, 50000, 1000)]
    amount = forms.ChoiceField(choices=BID_CHOICES, label="Ваша ставка")

    class Meta:
        model = Bid
        fields = ['bidder_name', 'bidder_email', 'amount']