import click

from chow import usecases


@click.group()
def cli():
    pass


@cli.command()
def update_price_archive() -> None:
    """
    Update a price archive JSON file.
    """
    # Declare products to track. This maps Ocado's product ID to a product description.
    # TODO make this a separate file that is passed in.
    products: usecases.ProductMap = {
        "13175011": {"name": "Lurpak butter (500g)", "price": None},
        "23476011": {"name": "New York bagels (5)", "price": None},
        "65448011": {"name": "Brown onions (3 pack)", "price": None},
        "64861011": {"name": "Royal Gala apples (6 pack)", "price": None},
        "44855011": {"name": "Fairtrade bananas (5 pack)", "price": None},
        "78914011": {"name": "Semi skimmed milk (4 pints)", "price": None},
        "57293011": {"name": "Large free range eggs (6 pack)", "price": None},
        "53687011": {"name": "Blueberries (150g)", "price": None},
        "47305011": {"name": "Lemons (5 pack)", "price": None},
        "91370011": {"name": "Large garlic", "price": None},
        "96798011": {"name": "Red seedless grapes (500g)", "price": None},
        "240875011": {"name": "Cucumber", "price": None},
        "31833011": {"name": "Cathedral City Cheese (550g)", "price": None},
        "510737011": {"name": "Super seeded loaf (800g)", "price": None},
        "321394011": {"name": "Helda stringless beans (180g)", "price": None},
        "225627011": {"name": "Chicken thigh fillets (450g)", "price": None},
        "32003011": {"name": "Onken biopot natural yoghurt (1kg)", "price": None},
        "98385011": {"name": "Parmigiano reggiano (320g)", "price": None},
    }
    summary = usecases.update_price_archive(products)
    if summary:
        print(summary)


if __name__ == "__main__":
    cli()
