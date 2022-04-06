from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class UserAdmin(UserAdmin):
    fieldsets = (
        (_('username & email & password'), {'fields': ('username', 'email', 'password')}),
        (_('authority'), {'fields': (
            'is_staff',
            'is_active',
            'is_superuser',
            'groups',
            'user_permissions',
        )}),
        (_('registration information'), {
         'fields': ('created_at', 'last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        'id',
        'email',
        'username',
        'is_active',
        'is_staff',
        'created_at',
        'updated_at',
        'last_login',
    )
    list_filter = ('is_staff', 'is_active',)
    search_fields = ('id', 'email', 'username')
    ordering = ('-created_at', )


admin.site.register(User, UserAdmin)
