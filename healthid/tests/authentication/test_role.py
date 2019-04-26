from healthid.tests.base_config import BaseConfiguration


class GraphQLTestCase(BaseConfiguration):
    """
    Testing the role functions
    """

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
        resp = self.query_with_token(
            self.access_token_master, query_string)
        self.assertResponseNoErrors(resp, expected)

    def test_single_role(self):
        query_string = f"""
        query {{
          role(id:"{self.role.id}") {{
            id
            name
          }}
        }}
        """
        resp = self.query_with_token(
            self.access_token_master, query_string)
        self.assertResponseNoErrors(
            resp, {"role": {"id": str(self.role.id),
                            "name": str(self.role.name)}}
        )

    def test_edit_role(self):
        query_string = f"""
            mutation editRole {{
           editRole (id:"{self.role.id}", input:{{
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
        resp = self.query_with_token(
            self.access_token_master, query_string)
        self.assertResponseNoErrors(resp, expected)

    def test_delete_role(self):
        query_string = f"""
           mutation deleteRole {{
           deleteRole (id:"{self.role.id}") {{
            success
          }}
        }}
        """
        expected = {"deleteRole": {"success": True}}
        resp = self.query_with_token(
            self.access_token_master, query_string)
        self.assertResponseNoErrors(resp, expected)
