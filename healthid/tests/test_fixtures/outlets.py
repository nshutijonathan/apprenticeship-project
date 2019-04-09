def create_outlet(business_id, city_id, type_id):
    return (f'''
            mutation{{
                createOutlet(
                    businessId: \"{business_id}\",
                    kindId: {type_id},
                    name: "green ville",
                    addressLine1: "10/11 Nagera",
                    addressLine2: "Nakawa, Kampala",
                    lga: "Nakawa",
                    cityId: {city_id},
                    phoneNumber: "2567803201607",
                    dateLaunched: "2019-02-27",)
                   {{
                    outlet{{name}}
                }}
            }}
            ''')


def update_outlet(outlet_id, outlet_name):
    return (f'''
            mutation{{
                updateOutlet(
                    id: {outlet_id},
                    name: "{outlet_name}",
                    addressLine1: "10/11 Nagera",
                    addressLine2: "Nakawa, Kampala",
                    lga: "Nakawa",
                    phoneNumber: "2567803201607",
                    dateLaunched: "2019-02-27",)
                   {{
                    outlet{{name, prefixId}}
                }}
            }}
            ''')


def delete_outlet(outlet_id):
    return f'mutation{{deleteOutlet(id: {outlet_id}){{success}}}}'
