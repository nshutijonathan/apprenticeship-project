from healthid.apps.outlets.models import Country


class CheckCity:
    """Implements a constraint on duplication of
    cities belonging to the same country
    """
    @staticmethod
    def check_city(city_name, ctry_id):
        """This method checks whether a city with a given
        name already exists on a given country

         Returns:
            - A boolean of True or False i.e found = true or false
            - A list of cities belonging to the country
        """
        country = Country.objects.filter(id=ctry_id).first()
        exist = False
        cities = None
        if country is not None:
            cities = [city['name'] for city in list(country.city_set.values())]
            exist = city_name in cities
        return (exist, cities)
