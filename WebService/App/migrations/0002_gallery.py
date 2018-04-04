# Generated by Django 2.0.3 on 2018-04-04 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('Owner', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='App.User')),
            ],
        ),
    ]
