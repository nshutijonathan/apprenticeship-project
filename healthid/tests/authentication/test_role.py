from django.test import Client, TestCase
from healthid.apps.authentication.models import User, Role
import json


class GraphQLTestCase(TestCase):
    """
    Testing the role functions
    """

    def create_default_role(self):
        return Role.objects.create(name="Master Admin")

    def setUp(self):
        self._client = Client()
        self.user = User.objects.create_user(
            email="testemail@test.com", password="testpassword123"
        )
        self.user.role = self.create_default_role()
        self.user.is_active = True
        self.user.save()
        self._client.login(
            email="testemail@test.com",
            password="testpassword123"
        )

    def create_test_user(self):
        return User.objects.create_user(
            email="user@test.com",
            password="userpassword123",
            mobile_number="+256 747464768"
        )

    def create_test_role(self):
        return Role.objects.create(name="User")

    def query(self, query: str):
        body = {"query": query}
        resp = self._client.post(
            "/healthid/", json.dumps(body), content_type="application/json"
        )
        jresp = json.loads(resp.content.decode())
        return jresp

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        self.assertNotIn("errors", resp, "Response had errors")
        self.assertEqual(resp["data"], expected, "Response has correct data")

    def test_create_role(self):
        query_string = """
            mutation createRole {
               createRole(input: {
                 name: "User"
               }) {
                 success
                 role {
                   name
                 }
               }
            }
                """
        expected = {"createRole": {"success": True, "role": {"name": "User"}}}
        resp = self.query(query_string)
        self.assertResponseNoErrors(resp, expected)

    def test_single_role(self):
        role = self.create_test_role()
        query_string = f"""
        query {{
          role(id:"{role.id}") {{
            id
            name
          }}
        }}
        """
        resp = self.query(query_string)
        self.assertResponseNoErrors(
            resp, {"role": {"id": str(role.id), "name": str(role.name)}}
        )

    def test_edit_role(self):
        role = self.create_test_role()
        query_string = f"""
            mutation editRole {{
           editRole (id:"{role.id}", input:{{
              name:"Test Role"
          }}) {{
            success
            role {{
              name
            }}
          }}
        }}

        """
        expected = {"editRole": {"success": True,
                                 "role": {"name": "Test Role"}}}
        resp = self.query(query_string)
        self.assertResponseNoErrors(resp, expected)

    def test_delete_role(self):
        role = self.create_test_role()
        query_string = f"""
           mutation deleteRole {{
           deleteRole (id:"{role.id}") {{
            success
          }}
        }}
        """
        expected = {"deleteRole": {"success": True}}
        resp = self.query(query_string)
        self.assertResponseNoErrors(resp, expected)
