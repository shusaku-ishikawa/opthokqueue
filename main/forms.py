from django import forms

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.core.exceptions import ValidationError
from .enums import *
import datetime
from django.template.loader import get_template
from django.conf import settings

class LoginForm(AuthenticationForm):
    """ログインフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            if field.label == 'メールアドレス':
                field.widget.attrs['placeholder'] = 'ID'
            elif field.label == 'パスワード':
                field.widget.attrs['placeholder'] = 'PW'

class UserEntryForm(forms.ModelForm):
    timeframes = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required = False
    )

    class Meta:
        model = UserEntry
        fields = ('clinic','is_anytime', 'email', 'nickname', 'from_date', 'to_date', 'is_anyday')
        widgets = {
            'from_date': forms.DateInput(format=('%Y/%m/%d'), attrs={'type':'date'}),
            'to_date': forms.DateInput(format=('%Y/%m/%d'), attrs={'type':'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_date'].widget.attrs['class'] = 'my-date-input'
        self.fields['to_date'].widget.attrs['class'] = 'my-date-input'
        self.fields['is_anytime'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_anyday'].widget.attrs['class'] = 'form-check-input'
        
        self.fields['email'].widget.attrs['placeholder'] = "パソコン、携帯どちらも可"    
        self.fields['email'].widget.attrs['class'] = "form-control"    
        
        self.fields['nickname'].widget.attrs['placeholder'] = "例) オプト　太郎"
        self.fields['nickname'].widget.attrs['class'] = "form-control"

        timeframchoices = []
        for wod_key, wod_value in DAY_OF_WEEK_DICT.items():
            for tf_key, tf_value in TIME_FRAME_DICT.items():
                timeframchoices.append(('{}_{}'.format(wod_key, tf_key), '{}_{}'.format(wod_key, tf_key)))
        self.fields['timeframes'].choices = timeframchoices

    def save(self, commit=True):
        timeframes = self.cleaned_data.pop('timeframes')
        email = self.cleaned_data['email']
        clinic = self.cleaned_data['clinic']
        try:
            instance = UserEntry.objects.get(email = email, clinic = clinic)
        except UserEntry.DoesNotExist:
            print('does not exitst')
            instance = UserEntry(**self.cleaned_data)
            instance.save()
            print(timeframes)
        else:
            old_timeframes = UserEntryTimeFrame.objects.filter(user_entry = instance)
            old_timeframes.delete()
            instance.is_anytime = self.cleaned_data['is_anytime']
            instance.nickname = self.cleaned_data['nickname']
            instance.from_date = self.cleaned_data['from_date']
            instance.to_date = self.cleaned_data['to_date']
            instance.is_anyday = self.cleaned_data['is_anyday']
            instance.save()
        if timeframes:
            for timeframe in timeframes:
                (dow, tf) = timeframe.split('_')
                obj = UserEntryTimeFrame(
                    user_entry = instance,
                    day_of_week = dow,
                    time_frame = tf
                )
                
                obj.save()
                print(obj)
        for invite in ClinicInvite.objects.all():
            if invite.match(instance):
                new_match = Match(user_entry = instance, clinic_invite = invite)
                new_match.save()
                instance.notify_match(invite)
                invite.notify_new_candidate(instance)
        return instance

class ClinicInviteForm(forms.ModelForm):
    class Meta:
        model = ClinicInvite
        fields = ('clinic', 'date', 'start_time')
        widgets = {
            'date': forms.DateInput(format=('%Y/%m/%d'), attrs={'type':'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['start_time'].widget.attrs['class'] = 'form-control'
    def save(self, commit = True):
        instance = super().save(commit)
        for user_entry in UserEntry.objects.all():
            if instance.match(user_entry):
                user_entry.notify_match(instance)
                new_match = Match(user_entry = user_entry, clinic_invite = instance)
                new_match.save()
                
        instance.notify_start()
        return instance

        