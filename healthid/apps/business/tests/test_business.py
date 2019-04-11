import json

from django.test import Client, TestCase

from healthid.apps.authentication.models import Role, User
from healthid.utils.business_utils.create_business import create_business


class GraphQLTestCase(TestCase):

    def create_default_role(self):
        return Role.objects.create(name='Master Admin')

    def setUp(self):
        self._client = Client()
        self.user = User.objects.create_user(
            email='qwertyu@example.com',
            password='qwertyuiop',
            mobile_number='256'
        )
        self.user.role = self.create_default_role()
        self.user.is_active = True
        self.user.save()

    def query(self, query: str):
        body = {"query": query}
        response = self._client.post(
            "/healthid/", json.dumps(body), content_type="application/json",)
        jresponse = json.loads(response.content.decode())
        return jresponse

    def login_user(self):
        self._client.login(email='qwertyu@example.com', password='qwertyuiop')

    def test_no_business(self):
        self.login_user()
        response = self.query('{businesses{id}}')
        self.assertIn('data', response)

    def test_create_business(self):
        self.login_user()
        response = self.query(
            (f'''
            mutation{{
                createBusiness(
                    legalName:"Ngora Traders"
                    tradingName:"Ngoraqpp Pharm"
                    email:"ngoraqpp.andela.com"
                    address:"30 Bukoto Street"
                    phoneNumber:"+2567099988"
                    website:"andela.com"
                    twitter:"andela@twitter.com"
                    instagram:"instragram.andela.com"
                    logo:"rtyuio/tyuio/rtyuhij"
                    facebook: "andela.facebook.com"
                ){{
                    business{{
                        id
                        email
                        legalName
                    }}
                }}
                }}
            '''),
        )
        self.assertIn('data', response)

    def test_update_business(self):
        self.login_user()
        business = create_business()
        response = self.query(
            (f'''

                mutation{{
                    updateBusiness(
                        id: "{business.id}"
                        legalName: "Bio Pain Killers"
                        tradingName: "qwerty"
                        address: "30 Bukoto Street"
                        phoneNumber: "+2567099988"
                        website: "andela.com"
                        twitter: "andela@twitter.com"
                        instagram: "instragram.andela.com"
                        logo: "rtyuio/tyuio/rtyuhij"
                        facebook: "andela.facebook.com"
                    ){{
                        business{{
                            id
                            legalName
                            tradingName
                            address
                            phoneNumber
                            email
                            instagram
                            website
                            twitter
                            facebook

                        }}
                        success

                    }}
                }}
            '''),
        )
        self.assertIn('data', response)

    def test_delete_business(self):
        self.login_user()
        business = create_business()
        response = self.query(
            f'''
            mutation{{
                deleteBusiness(
                    id: "{business.id}"
                    ){{
                        success
                        }}
                    }}
            ''')
        self.assertIn('data', response)

    # def test_business_model(self):
    #     # this create the business to test list of businesses
    #     business = create_business()
    #     response = self.query(
    #         f'''
    #         query{{businesses{{
    #             id
    #             legalName
    #             tradingName
    #             email
    #             phoneNumber
    #             address
    #             twitter
    #             facebook
    #             website
    #         }}}}
    #     ''')
    #     self.assertIn('data', response)
