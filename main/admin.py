from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = Clinic
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = Clinic
        fields = ('email',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email','name', 'phone', 'qrcode' , 'password')}),
        (_('Personal info'), {'fields': ()}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','name', 'phone', 'qrcode', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'name', 'phone', 'qrcode', 'is_staff', 'is_active', 'is_superuser')

    ordering = ('name',)

class UserEntryAdmin(admin.ModelAdmin):
    list_display = ('matched_invite', 'clinic', 'email', 'nickname', 'from_date', 'to_date', 'is_anytime', 'is_anyday')

class UserEntryTimeFrameAdmin(admin.ModelAdmin):
    list_display = ('user_entry', 'day_of_week_readable', 'timeframe_readable')

class ClinicInviteAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'date', 'start_time')

class ClinicAdditionalFieldAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'name')

class ClinicAdditionalFieldOptionAdmin(admin.ModelAdmin):
    list_display = ('parent', 'value')
class ClinicInviteAdditionalItemAdmin(admin.ModelAdmin):
    list_display = ('parent', 'question', 'chosen_option')

class UserEntryAdditionalItemAdmin(admin.ModelAdmin):
    list_display = ('parent', 'question', 'chosen_option')


admin.site.register(Clinic, MyUserAdmin)
admin.site.register(UserEntry, UserEntryAdmin)
admin.site.register(UserEntryTimeFrame, UserEntryTimeFrameAdmin)
admin.site.register(ClinicInvite, ClinicInviteAdmin)
admin.site.register(ClinicAdditionalField, ClinicAdditionalFieldAdmin)
admin.site.register(ClinicAdditionalFieldOption, ClinicAdditionalFieldOptionAdmin)
admin.site.register(ClinicInviteAdditionalItem, ClinicInviteAdditionalItemAdmin)
admin.site.register(UserEntryAdditionalItem, UserEntryAdditionalItemAdmin)
