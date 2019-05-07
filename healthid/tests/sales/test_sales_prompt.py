from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales import (
                                                       create_sales_prompts,
                                                       update_sales_prompt,
                                                       delete_sales_prompt,
                                                       query_all_sales_prompt,
                                                       query_a_sales_prompt,
                                                       incomplete_sales_entry)


class TestSalesPrompt(BaseConfiguration):
    def test_create_sales_prompts(self):
        """Test method for creating sales prompts"""
        data = {
            "product_id": self.product.id,
            "outlet_id": self.outlet.id,
            "title": "Title1 Coming",
            "description": "Description2 Coming"
        }
        response = self.query_with_token(
            self.access_token_master,
            create_sales_prompts.format(**data))
        expected_message = 'Successfully created 1 sales prompt'
        self.assertEqual(
            expected_message,
            response["data"]["createSalesprompts"]["message"])
        self.assertNotIn("errors", response)

    def test_sales_prompts_with_invalid_product(self):
        """
        Test method for creating multiple sales prompts with invalid product
        """
        data = {
            "product_id": 0,
            "outlet_id": self.outlet.id,
            "title": "Title1 Coming",
            "description": "Description2 Coming"
        }
        response = self.query_with_token(
            self.access_token_master,
            create_sales_prompts.format(**data))
        self.assertIn(
            "Product with id 0 does not exist.",
            response['errors'][0]['message'])

    def test_sales_prompts_with_invalid_list(self):
        """
        Test method for creating multiple sales prompts with No list Item
        """
        data = {
            "product_id": [],
            "outlet_id": self.outlet.id,
            "title": "Title1 Coming",
            "description": "Description2 Coming"
        }
        response = self.query_with_token(
            self.access_token_master,
            create_sales_prompts.format(**data))
        self.assertIn("errors", response)

    def test_sales_prompts_with_empty_title(self):
        """
        Test method for creating multiple sales prompts with No list Item
        """
        data = {
            "product_id": self.product.id,
            "outlet_id": self.outlet.id,
            "title": "   ",
            "description": "Description2 Coming"
        }
        response = self.query_with_token(
            self.access_token_master,
            create_sales_prompts.format(**data))
        self.assertIn(
            "Titles and discription must contain words",
            response['errors'][0]['message'])

    def test_sales_prompts_with_invalid_incomplete_inputs(self):
        """
        Test method for creating multiple sales prompts with No list Item
        """
        data = {
            "product_id": self.product.id,
            "outlet_id": self.outlet.id,
            "title": "Title1 Coming",
            "description": "Description2 Coming"
        }
        response = self.query_with_token(
            self.access_token_master,
            incomplete_sales_entry.format(**data))
        self.assertEqual("List inputs are incomplete or empty",
                         response['errors'][0]['message'])
        self.assertIn("errors", response)

    def test_sales_prompts_with_invalid_outlet(self):
        """
        Test method for creating multiple sales prompts with invalid outlet
        """
        data = {
            "product_id": self.product.id,
            "outlet_id": 0,
            "title": "Title1 Coming",
            "description": "Description2 Coming"
        }
        response = self.query_with_token(
            self.access_token_master,
            create_sales_prompts.format(**data))
        self.assertIn("errors", response)
        self.assertIn(
            "Outlet with id 0 does not exist.",
            response['errors'][0]['message'])

    def test_update_sales_prompts(self):
        """Test method for updating sales prompts"""
        data = {
            "sales_prompt_id": self.sales_prompt.id,
            "title": "Brand new Title",
            "description": "Description2 Coming2",
            "product_id": self.product.id,
            "outlet_id": self.outlet.id
        }
        response = self.query_with_token(
            self.access_token_master,
            update_sales_prompt.format(**data))
        self.assertIn("Sales prompt was updated successfully",
                      response["data"]["updateSalesprompt"]["success"])
        self.assertNotIn("errors", response)

    def test_update_sales_prompts_with_empty_title_or_discription(self):
        """Test method for updating sales prompts"""
        data = {
            "sales_prompt_id": self.sales_prompt.id,
            "title": "  ",
            "description": "  ",
            "product_id": self.product.id,
            "outlet_id": self.outlet.id
        }
        response = self.query_with_token(
            self.access_token_master,
            update_sales_prompt.format(**data))
        self.assertIn("errors", response)
        self.assertIn(
            "Titles or discription must contain words",
            response['errors'][0]['message'])

    def test_get_all_sales_prompt(self):
        """Test method for quering all sales prompt"""
        response = self.query_with_token(
            self.access_token_master,
            query_all_sales_prompt)
        self.assertIn("salesPrompts", response["data"])
        self.assertNotIn("errors", response)

    def test_get_a_sales_prompt(self):
        """Test method for quering a particular sales prompt"""
        response = self.query_with_token(
            self.access_token_master,
            query_a_sales_prompt(self.sales_prompt.id))
        self.assertIn("salesPrompt", response["data"])
        self.assertNotIn("errors", response)

    def test_delete_sales_prompt(self):
        """Test method for deleting sales prompts"""
        response = self.query_with_token(
            self.access_token_master,
            delete_sales_prompt(self.sales_prompt.id))
        self.assertIn("Sales Prompt was deleted successfully",
                      response["data"]["deleteSalesprompt"]["success"])
        self.assertNotIn("errors", response)
