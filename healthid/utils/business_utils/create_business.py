from healthid.apps.business.models import Business


def create_business():
    return Business.objects.create(
        legal_name="rockerr",
        trading_name="Andela Uganda",
        business_email="arockerr.andela.com",
        address_line_1="30 Bukoto Street",
        phone_number="+2567099988",
        local_government_area="Kamwokya",
        city="Kampala",
        country="Uganda",
        website="andela.com",
        twitter="andela@twitter.com",
        instagram="instragram.andela.com",
        logo="rtyuio/tyuio/rtyuhij",
        facebook="andela.facebook.com",
    )
