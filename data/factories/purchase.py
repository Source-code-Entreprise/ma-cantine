import factory
import random
from factory.fuzzy import FuzzyChoice
from data.models import Purchase
from .canteen import CanteenFactory


class PurchaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Purchase

    canteen = factory.SubFactory(CanteenFactory)
    date = factory.Faker("date")
    provider = factory.Faker("company")
    category = FuzzyChoice(Purchase.Category.values)
    characteristics = factory.List(random.sample(list(Purchase.Characteristic.values), random.randint(0, 3)))
    price_ht = factory.Faker("random_int", min=0, max=2000)