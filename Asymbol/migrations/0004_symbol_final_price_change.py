# Generated by Django 4.1.7 on 2023-03-16 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Asymbol', '0003_symbol_market_symbol_sector_symbol_symbol_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='symbol',
            name='final_price_change',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
