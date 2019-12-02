from django import forms
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import os
from django.db.models import Q
# Create your models here.
import unicodedata
from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe 
from django.template.loader import get_template
from .enums import *
from django.conf import settings
import datetime
class MyUserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class Clinic(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = '医院'
        verbose_name_plural = '医院'

    def __str__(self):
        return self.name
    """カスタムユーザーモデル."""
    email = models.EmailField('メールアドレス', max_length=150, null = False, blank=False, unique = True)
    name = models.CharField('医院名', max_length=150, null = False, blank=False)
    phone = models.CharField('電話番号', max_length = 100, null = False, blank = False)
    qrcode = models.ImageField('QR', upload_to = 'qrcode', null = True)
    is_staff = models.BooleanField(
        '管理者',
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        '有効',
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = MyUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.name

from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from io import StringIO, BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


@receiver(post_save, sender=Clinic)
def create_qrcode(sender, instance, created, **kwargs):
    if created:
        print('new clinic created')
        content = 'mailto:{contact}?subject=clinicId_{clinic_id}'.format(contact = settings.DEFAULT_FROM_EMAIL_FOR_QR, clinic_id = instance.id)
        img = qrcode.make(content)
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        qrfile = InMemoryUploadedFile(img_io, None, 'qrcode_{}.jpg'.format(instance.id), 'image/jpeg', len(img_io.getvalue()), None)
        instance.qrcode = qrfile
        instance.save()


def has_common_member(a, b): 
    a_set = set(a) 
    b_set = set(b) 
    if (a_set & b_set): 
        return True 
    else: 
        return False
            
class ClinicInvite(models.Model):
    class Meta:
        verbose_name = '空き枠'
        verbose_name_plural = '空き枠'

    def __str__(self):
        return self.clinic.name # + self.date.strftime('%Y/%m/%d') + self.timeframe_readable

    clinic = models.ForeignKey(
        verbose_name = '医院',
        to = Clinic,
        on_delete = models.CASCADE
    )
    date = models.DateField(
        verbose_name = '日'
    )
    start_time = models.TimeField(
        verbose_name = '開始時間',
        default=timezone.now,
    )

    # time_frame = models.CharField(
    #     verbose_name = '時間帯',
    #     max_length = 10,
    #     choices = [(key, value) for (key, value) in TIME_FRAME_DICT.items() if key != TIME_FRAME_ANYTIME]
    # )
    # @property
    # def timeframe_readable(self):
    #     return TIME_FRAME_DICT[self.time_frame]
    @property
    def matched_count(self):
        return len(self.matched.all())

    @property
    def day_of_week(self):
        return str(self.date.weekday())
    

    def match(self, user_entry):
        if user_entry.matched_invite:
            print('already matched')
            return False
        if user_entry.from_date and user_entry.from_date > self.date:
            print('from date invalid')
            return False
        if user_entry.to_date and user_entry.to_date < self.date:
            print('to date invalid')
            return False
        if user_entry.is_anytime:
            return True
        else:
            print('match called')
            for tf in user_entry.timeframes.all():
                if tf.day_of_week == self.day_of_week:    
                    if tf.time_frame == TIME_FRAME_ANYTIME:
                        return True
                    thresholds = {
                        TIME_FRAME_9_12: {
                            'start': datetime.time(hour = 9),
                            'end': datetime.time(hour = 11, minute = 59)
                        },
                        TIME_FRAME_12_15: {
                            'start': datetime.time(hour = 12),
                            'end': datetime.time(hour = 14, minute = 59)
                        },
                        TIME_FRAME_15_18: {
                            'start': datetime.time(hour = 15),
                            'end': datetime.time(hour = 17, minute = 59)
                        },
                        TIME_FRAME_18_21: {
                            'start': datetime.time(hour = 18),
                            'end': datetime.time(hour = 20, minute = 59)
                        }
                    }
                    item = thresholds[str(tf.time_frame)]
                    if self.start_time >= item['start'] and self.start_time < item['end']:
                        matched = True
                        for field in self.clinic.additional_fields.all():
                            invited_option_id_list = [item.chosen_option.id for item in self.additional_items.all() if item.question.id == field.id]
                            user_entry_option_id_list = [item.chosen_option.id for item in user_entry.additional_items.all() if item.question.id == field.id]
                            if not has_common_member(invited_option_id_list, user_entry_option_id_list):
                                return False
                        return True
                        #user_entry.additional_items.all()
                    else:
                        print('start time not matched' + str(item['start']) + ' ' + str(item['end']), str(self.start_time))
                else:
                    print('day invalid')
            else:
                print('user entry timeframe empy')
        return False
    def notify_start(self):
        context = { 'object': self }
        subject = 'キャンセル待ちシステム[募集開始]'
        message = get_template('mail/start_invite.txt').render(context)
        self.clinic.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    def notify_new_candidate(self, new_entry):
        context = { 'object': self, 'new_entry': new_entry }
        subject = 'キャンセル待ちシステム[新規に応募がありました]'
        message = get_template('mail/new_candidate.txt').render(context)
        self.clinic.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
    
class ClinicAdditionalField(models.Model):
    class Meta:
        verbose_name = '医院拡張項目'
        verbose_name_plural = '医院拡張項目'
    def __str__(self):
        return self.clinic.__str__() + self.name
    clinic = models.ForeignKey(
        to = Clinic,
        on_delete = models.CASCADE,
        related_name = 'additional_fields'
    )
    name = models.CharField(
        max_length = 255
    )
class ClinicAdditionalFieldOption(models.Model):
    class Meta:
        verbose_name = '医院拡張項目選択肢'
        verbose_name_plural = '医院拡張項目選択肢'
    def __str__(self):
        return self.parent.__str__() + ' ' + self.value
    parent = models.ForeignKey(
        to = ClinicAdditionalField,
        on_delete = models.CASCADE,
        related_name = 'options'
    )
    value = models.CharField(
        max_length = 255
    )

class UserEntry(models.Model):
    class Meta:
        verbose_name = 'キャンまち'
        verbose_name_plural = 'キャンまち'
    def __str__(self):
        return self.nickname

    matched_invite = models.ForeignKey(
        verbose_name = 'マッチした空き枠',
        to = ClinicInvite,
        null = True,
        blank = True,
        on_delete = models.CASCADE,
        related_name = 'matched'
    )

    clinic = models.ForeignKey(
        verbose_name = '医院',
        to = Clinic,
        on_delete = models.CASCADE
    )
    email = models.EmailField(
        verbose_name = 'メールアドレス'
    )

    nickname = models.CharField(
        verbose_name = 'ニックネーム',
        max_length = 100
    )
    from_date = models.DateField(
        verbose_name = 'いつから',
        blank = True,
        null = True
    )
    to_date = models.DateField(
        verbose_name = 'いつまで',
        blank = True,
        null = True
    )
    is_anytime = models.BooleanField(
        verbose_name = '時間帯不問'
    )
    is_anyday = models.BooleanField(
        verbose_name = '日にち不問'
    )


    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def notify_match(self, invite):
        context = { "clinic": invite.clinic.name, "nickname": self.nickname, "date": invite.date, "timeframe": invite.start_time, 'clinic_phone': self.clinic.phone }
        subject = '予約空き情報[{}]'.format(self.clinic.name)
        message = get_template('mail/match.txt').render(context)
        self.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        self.matched_invite = invite    
        self.save()
    @property
    def timeframe_list(self):
        return ['{}_{}'.format(tf.day_of_week, tf.time_frame) for tf in self.timeframes.all()]


class UserEntryAdditionalItem(models.Model):
    class Meta:
        verbose_name = 'キャンまち拡張項目'
        verbose_name_plural = 'キャンまち拡張項目'

    def __str__(self):
        return self.parent.__str__() + ' ' + self.question.__str__() + ' ' + self.chosen_option.__str__()

    parent = models.ForeignKey(
        to = UserEntry,
        related_name = 'additional_items',
        on_delete = models.CASCADE
    )
    question = models.ForeignKey(
        to = ClinicAdditionalField,
        on_delete = models.CASCADE
    )
    chosen_option = models.ForeignKey(
        to = ClinicAdditionalFieldOption,
        on_delete = models.CASCADE
    )
class ClinicInviteAdditionalItem(models.Model):
    class Meta:
        verbose_name = '空き枠拡張項目'
        verbose_name_plural = '空き枠キャンまち拡張項目'
    def __str__(self):
        return self.parent.__str__() + ' ' + self.question.__str__() + ' ' + self.chosen_option.__str__()
        
    parent = models.ForeignKey(
        to = ClinicInvite,
        on_delete = models.CASCADE,
        related_name = 'additional_items',
    )
    question = models.ForeignKey(
        to = ClinicAdditionalField,
        on_delete = models.CASCADE
    )
    chosen_option = models.ForeignKey(
        to = ClinicAdditionalFieldOption,
        on_delete = models.CASCADE
    )

class UserEntryTimeFrame(models.Model):
    class Meta:
        verbose_name = 'キャンまち明細'
        verbose_name_plural = 'キャンまち明細'
    user_entry = models.ForeignKey(
        to = UserEntry,
        on_delete = models.CASCADE,
        related_name = 'timeframes'
    )
    day_of_week = models.CharField(
        verbose_name = '希望曜日',
        max_length = 10
    )
    time_frame = models.CharField(
        verbose_name = '希望時間帯',
        max_length = 10
    )
    @property
    def day_of_week_readable(self):
        return DAY_OF_WEEK_DICT[self.day_of_week]
    
    @property
    def timeframe_readable(self):
        return TIME_FRAME_DICT[self.time_frame]

