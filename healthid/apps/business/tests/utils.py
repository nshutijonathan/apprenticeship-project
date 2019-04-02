from healthid.apps.business.models import Business


def create_business():
    return Business.objects.create(
        legal_name="rockerr",
        trading_name="Andela Uganda",
        email="arockerr.andela.com",
        address="30 Bukoto Street",
        phone_number="+2567099988",
        website="andela.com",
        twitter="andela@twitter.com",
        instagram="instragram.andela.com",
        logo="rtyuio/tyuio/rtyuhij",
        facebook="andela.facebook.com",
    )
