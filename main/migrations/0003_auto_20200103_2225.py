# Generated by Django 2.1.5 on 2020-01-03 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20191127_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinic_invite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matched', to='main.ClinicInvite')),
            ],
            options={
                'verbose_name': 'キャン待ちマッチング',
                'verbose_name_plural': 'キャン待ちマッチング',
            },
        ),
        migrations.AlterModelOptions(
            name='clinicadditionalfield',
            options={'verbose_name': '医院拡張項目', 'verbose_name_plural': '医院拡張項目'},
        ),
        migrations.AlterModelOptions(
            name='clinicadditionalfieldoption',
            options={'verbose_name': '医院拡張項目選択肢', 'verbose_name_plural': '医院拡張項目選択肢'},
        ),
        migrations.AlterModelOptions(
            name='clinicinviteadditionalitem',
            options={'verbose_name': '空き枠拡張項目', 'verbose_name_plural': '空き枠キャンまち拡張項目'},
        ),
        migrations.AlterModelOptions(
            name='userentryadditionalitem',
            options={'verbose_name': 'キャンまち拡張項目', 'verbose_name_plural': 'キャンまち拡張項目'},
        ),
        migrations.RemoveField(
            model_name='userentry',
            name='matched_invite',
        ),
        migrations.AlterField(
            model_name='clinicinviteadditionalitem',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_items', to='main.ClinicInvite'),
        ),
        migrations.AlterField(
            model_name='userentryadditionalitem',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_items', to='main.UserEntry'),
        ),
        migrations.AddField(
            model_name='match',
            name='user_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.UserEntry'),
        ),
    ]
