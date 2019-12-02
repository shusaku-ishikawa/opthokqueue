# Generated by Django 2.1.5 on 2019-11-27 02:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import main.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=150, unique=True, verbose_name='メールアドレス')),
                ('name', models.CharField(max_length=150, verbose_name='医院名')),
                ('phone', models.CharField(max_length=100, verbose_name='電話番号')),
                ('qrcode', models.ImageField(null=True, upload_to='qrcode', verbose_name='QR')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='管理者')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='有効')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '医院',
                'verbose_name_plural': '医院',
            },
            managers=[
                ('objects', main.models.MyUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ClinicAdditionalField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClinicAdditionalFieldOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ClinicAdditionalField')),
            ],
        ),
        migrations.CreateModel(
            name='ClinicInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='日')),
                ('start_time', models.TimeField(default=django.utils.timezone.now, verbose_name='開始時間')),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='医院')),
            ],
            options={
                'verbose_name': '空き枠',
                'verbose_name_plural': '空き枠',
            },
        ),
        migrations.CreateModel(
            name='UserEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='メールアドレス')),
                ('nickname', models.CharField(max_length=100, verbose_name='ニックネーム')),
                ('from_date', models.DateField(blank=True, null=True, verbose_name='いつから')),
                ('to_date', models.DateField(blank=True, null=True, verbose_name='いつまで')),
                ('is_anytime', models.BooleanField(verbose_name='時間帯不問')),
                ('is_anyday', models.BooleanField(verbose_name='日にち不問')),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='医院')),
                ('matched_invite', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='matched', to='main.ClinicInvite', verbose_name='マッチした空き枠')),
            ],
            options={
                'verbose_name': 'キャンまち',
                'verbose_name_plural': 'キャンまち',
            },
        ),
        migrations.CreateModel(
            name='UserEntryAdditionalItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chosen_option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ClinicAdditionalFieldOption')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.UserEntry')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.ClinicAdditionalField')),
            ],
        ),
        migrations.CreateModel(
            name='UserEntryTimeFrame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.CharField(max_length=10, verbose_name='希望曜日')),
                ('time_frame', models.CharField(max_length=10, verbose_name='希望時間帯')),
                ('user_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeframes', to='main.UserEntry')),
            ],
            options={
                'verbose_name': 'キャンまち明細',
                'verbose_name_plural': 'キャンまち明細',
            },
        ),
    ]
