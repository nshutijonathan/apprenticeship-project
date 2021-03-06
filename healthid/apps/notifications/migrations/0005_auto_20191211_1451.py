# Generated by Django 2.2 on 2019-12-11 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0004_auto_20190529_2317'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('body', models.TextField()),
                ('deleted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='notification',
            name='message',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='notification_records',
        ),
        migrations.AddField(
            model_name='notification',
            name='status',
            field=models.CharField(choices=[('unread', 'unread'), ('read', 'unread')], default='unread', max_length=10),
        ),
        migrations.AddField(
            model_name='notification',
            name='subject',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='NotificationRecord',
        ),
        migrations.AddField(
            model_name='notificationmeta',
            name='notification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.Notification'),
        ),
    ]
