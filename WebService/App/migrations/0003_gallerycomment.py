# Generated by Django 2.0.3 on 2018-04-04 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0002_gallery'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UploadDateTime', models.DateTimeField(default=None, null=True)),
                ('Text', models.CharField(max_length=1024)),
                ('Gallery', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='App.Gallery')),
                ('User', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='App.User')),
            ],
        ),
    ]
