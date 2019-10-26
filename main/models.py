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

    """カスタムユーザーモデル."""
    email = models.EmailField('メールアドレス', max_length=150, null = False, blank=False, unique = True)
    name = models.CharField('医院名', max_length=150, null = False, blank=False)
    
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
        return self.email

class ClinicInvite(models.Model):
    clinic = models.ForeignKey(
        to = Clinic,
        on_delete = models.CASCADE
    )
    date = models.DateField()
    time_frame = models.CharField(
        max_length = 10,
        choices = [(key, value) for (key, value) in TIME_FRAME_DICT.items() if key != TIME_FRAME_ANYTIME]
    )
    @property
    def timeframe_readable(self):
        return TIME_FRAME_DICT[self.time_frame]
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
            for tf in user_entry.timeframes.all():
                if tf.day_of_week == self.day_of_week:
                    if tf.time_frame == TIME_FRAME_ANYTIME:
                        return True
                    else:
                        if tf.time_frame == self.time_frame:
                            return True
                        else:
                            print('timeframe invalid')
                else:
                    print(type(tf.day_of_week))
                    print(type(self.day_of_week))
                    print('day of week invaid{} {}'.format(tf.day_of_week, self.day_of_week))
        return False
class UserEntry(models.Model):
    def __str__(self):
        return self.nickname

    matched_invite = models.ForeignKey(
        to = ClinicInvite,
        null = True,
        blank = True,
        on_delete = models.CASCADE,
        related_name = 'matched'
    )

    clinic = models.ForeignKey(
        to = Clinic,
        on_delete = models.CASCADE
    )
    email = models.EmailField()

    nickname = models.CharField(
        max_length = 100
    )
    from_date = models.DateField(
        blank = True,
        null = True
    )
    to_date = models.DateField(
        blank = True,
        null = True
    )
    is_anytime = models.BooleanField()
    is_anyday = models.BooleanField()

    do_chiryo = models.BooleanField(
        verbose_name = '治療'
    )
    do_teikikenshin = models.BooleanField()
    do_whitening = models.BooleanField()
    do_kyousei = models.BooleanField()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def notify_match(self, invite):
        context = { "date": invite.date, "timeframe": TIME_FRAME_DICT[invite.time_frame] }
        subject = '空きが出ました'
        message = get_template('mail/match.txt').render(context)
        self.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        self.matched_invite = invite    
        self.save()
class UserEntryTimeFrame(models.Model):

    user_entry = models.ForeignKey(
        to = UserEntry,
        on_delete = models.CASCADE,
        related_name = 'timeframes'
    )
    day_of_week = models.CharField(max_length = 10)
    time_frame = models.CharField(max_length = 10)
    @property
    def day_of_week_readable(self):
        return DAY_OF_WEEK_DICT[self.day_of_week]
    
    @property
    def timeframe_readable(self):
        return TIME_FRAME_DICT[self.time_frame]

