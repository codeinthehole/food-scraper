import factory

# Archive types


class PriceChange(factory.DictFactory):
    date = "2022-09-20"
    price = "0.85"


class ProductPriceHistory(factory.DictFactory):
    name = "Mars bar"
    prices = factory.List([PriceChange()])


class ArchiveProductMap(factory.DictFactory):
    p1 = factory.SubFactory(ProductPriceHistory)
