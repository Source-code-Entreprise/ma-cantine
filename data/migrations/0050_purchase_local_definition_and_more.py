# Generated by Django 4.0.2 on 2022-02-23 09:52

import data.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0049_purchase_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='local_definition',
            field=models.CharField(blank=True, choices=[('REGION', 'Région'), ('DEPARTMENT', 'Département'), ('AUTOUR_SERVICE', '200 km autour du lieu de service'), ('AUTRE', 'Autre')], max_length=255, null=True, verbose_name='Comment définir local'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='characteristics',
            field=data.fields.ChoiceArrayField(base_field=models.CharField(blank=True, choices=[('BIO', 'Bio'), ('CONVERSION_BIO', 'En conversion bio'), ('LABEL_ROUGE', 'Label rouge'), ('AOCAOP', 'AOC / AOP'), ('ICP', 'Indication géographique protégée'), ('STG', 'Spécialité traditionnelle garantie'), ('HVE', 'Haute valeur environnementale'), ('PECHE_DURABLE', 'Pêche durable'), ('RUP', 'Région ultrapériphérique'), ('FERMIER', 'Fermier'), ('EXTERNALITES', 'Produit prenant en compte les coûts imputés aux externalités environnementales pendant son cycle de vie'), ('COMMERCE_EQUITABLE', 'Commerce équitable'), ('PERFORMANCE', 'Produits acquis sur la base de leurs performances en matière environnementale'), ('EQUIVALENTS', 'Produits équivalents'), ('FRANCE', 'Provenance France'), ('SHORT_DISTRIBUTION', 'Circuit-court'), ('LOCAL', 'Produit local')], max_length=255, null=True, verbose_name='Caractéristique'), blank=True, null=True, size=None, verbose_name='Caractéristiques'),
        ),
    ]