import factory  # type:ignore


class ArchiveProductPrice(factory.DictFactory):
    date = "2022-09-20"
    price = "0.85"


class ArchiveProduct(factory.DictFactory):
    name = "Mars bar"
    prices = factory.List([ArchiveProductPrice()])


class Archive(factory.DictFactory):
    p1 = factory.SubFactory(ArchiveProduct)
