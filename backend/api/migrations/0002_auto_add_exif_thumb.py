from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='thumbnail',
            field=models.ImageField(upload_to='photos/thumbnails/', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='exif',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='tags',
            field=models.JSONField(blank=True, null=True, help_text='自动标签'),
        ),
        migrations.AddField(
            model_name='photo',
            name='taken_at',
            field=models.DateTimeField(blank=True, null=True, help_text='拍摄时间'),
        ),
        migrations.AddField(
            model_name='photo',
            name='location',
            field=models.CharField(max_length=255, blank=True, null=True, help_text='拍摄地点'),
        ),
        migrations.AddField(
            model_name='photo',
            name='resolution',
            field=models.CharField(max_length=32, blank=True, null=True, help_text='分辨率'),
        ),
    ]
