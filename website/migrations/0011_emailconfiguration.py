# Generated manually for EmailConfiguration model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_blogs_delete_block'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_host', models.CharField(default='smtp.gmail.com', help_text='SMTP server address', max_length=255)),
                ('email_port', models.IntegerField(default=587, help_text='SMTP port (e.g. 587 for TLS, 465 for SSL)')),
                ('email_use_tls', models.BooleanField(default=True, help_text='Use TLS connection')),
                ('email_use_ssl', models.BooleanField(default=False, help_text='Use SSL connection')),
                ('email_host_user', models.CharField(blank=True, default='', help_text='SMTP Username / Email address', max_length=255)),
                ('email_host_password', models.CharField(blank=True, default='', help_text='SMTP Password / App Password', max_length=255)),
                ('default_from_email', models.CharField(default='Sreemr Homes <noreply@sreemrhomes.com>', help_text='Default Sender header (e.g. Sreemr Homes <noreply@sreemrhomes.com>)', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Set to True to use this email configuration')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Email Configuration',
                'verbose_name_plural': 'Email Configurations',
                'ordering': ['-updated_at'],
            },
        ),
    ]
