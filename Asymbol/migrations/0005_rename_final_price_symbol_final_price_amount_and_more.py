# Generated by Django 4.1.7 on 2023-03-16 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Asymbol', '0004_symbol_final_price_change'),
    ]

    operations = [
        migrations.RenameField(
            model_name='symbol',
            old_name='final_price',
            new_name='final_price_amount',
        ),
        migrations.AddField(
            model_name='symbol',
            name='final_price_percent',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
