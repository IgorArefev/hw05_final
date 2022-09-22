from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=20, label="Имя пользователя",
        help_text='Обязательное поле. Не более 20 символов. '
                  'Только буквы, цифры и символы @/./+/-/_.'
    )
    first_name = forms.CharField(max_length=12, required=False, label="Имя")
    last_name = forms.CharField(max_length=12, required=False, label='Фамилия')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
