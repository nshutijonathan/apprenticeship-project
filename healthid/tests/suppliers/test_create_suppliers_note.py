from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.suppliers import (
                                                       create_suppliers_note,
                                                       update_suppliers_note,
                                                       delete_supplier_note,
                                                       all_suppliers_note,
                                                       supplier_notes)


class TestSuppliersNote(BaseConfiguration):
    def test_create_suppliers_note(self):
        """Test method for creating a suppliers note"""
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": self.outlet.id,
            "note": "Great Supplier man"
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = "Successfully created Note"
        self.assertEqual(
            expected_message,
            response["data"]["createSuppliernote"]["message"])
        self.assertNotIn("errors", response)

    def test_create_suppliers_note_with_invalid_supplier_id(self):
        """Test method for creating a suppliers note with invalid input"""
        data = {
            "supplier_id": 0,
            "outlet_id": self.outlet.id,
            "note": "Great Supplier"
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = "Suppliers with id 0 does not exist."
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_suppliers_note_with_special_characters(self):
        """Test method for creating a suppliers note with special characters"""
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": self.outlet.id,
            "note": "Great <>]]]#@ Supplier"
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = "special characters not allowed"
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_suppliers_note_with_less_than_two_words(self):
        """
          Test method for creating a suppliers note with less than two words
        """
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": self.outlet.id,
            "note": "Great "
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = "Suppliers note must be two or more words"
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_suppliers_note_with_invalid_outlet_id(self):
        """Test method for creating a suppliers note with invalid input"""
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": 0,
            "note": "Great Supplier"
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = "Outlet with id 0 does not exist."
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_update_suppliers_note(self):
        """Test method for updating a suppliers note"""
        data = {
            "supplier_note": self.suppliers_note.id,
            "outlet_id": self.outlet.id,
            "note": "Update Supplier note"
        }
        response = self.query_with_token(
            self.access_token,
            update_suppliers_note.format(**data))
        expected_message = "Suppliers Note was updated successfully"
        self.assertEqual(
            expected_message,
            response["data"]["updateSuppliernote"]["success"])
        self.assertNotIn("errors", response)

    def test_update_suppliers_note_with_less_than_two_words(self):
        """
          Test method for updating a suppliers note, with less than two words
        """
        data = {
            "supplier_note": self.suppliers_note.id,
            "outlet_id": self.outlet.id,
            "note": "Updated  "
        }
        response = self.query_with_token(
            self.access_token,
            update_suppliers_note.format(**data))
        expected_message = "Suppliers note must be two or more words"
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_update_suppliers_note_with_special_characters(self):
        """
          Test method for updating a suppliers note, with special characters
        """
        data = {
            "supplier_note": self.suppliers_note.id,
            "outlet_id": self.outlet.id,
            "note": "Updated %^&$3$@ suplier "
        }
        response = self.query_with_token(
            self.access_token,
            update_suppliers_note.format(**data))
        expected_message = "special characters not allowed"
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_update_suppliers_note_with_invalid_user(self):
        """
          Test method for updating a suppliers note, with invalid user
        """
        data = {
            "supplier_note": self.suppliers_note.id,
            "outlet_id": self.outlet.id,
            "note": "Updating supplier "
        }
        response = self.query_with_token(
            self.access_token_master,
            update_suppliers_note.format(**data))
        expected_message = "You can't update a note you didn't create"
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_get_all_suppliers_note(self):
        """Test method for quering all suppliers note"""
        response = self.query_with_token(
            self.access_token,
            all_suppliers_note)
        self.assertIn("allSuppliersNote", response["data"])
        self.assertNotIn("errors", response)

    def test_get_a_suppliers_notes(self):
        """Test method for quering a particular suppliers note"""
        response = self.query_with_token(
            self.access_token,
            supplier_notes(self.suppliers_note.supplier_id))
        self.assertIn("suppliersNote", response["data"])
        self.assertNotIn("errors", response)

    def test_get_a_suppliers_notes_with_invalid_supplier_id(self):
        """
         Test method for quering a particular suppliers note with invalid id
        """
        response = self.query_with_token(
            self.access_token,
            supplier_notes(0))
        expected_message = "Suppliers with id 0 does not exist."
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_delete_suppliers_note_with_invalid_user(self):
        """Test method for deleting suppliers note with invalid user"""
        response = self.query_with_token(
            self.access_token_master,
            delete_supplier_note(self.suppliers_note.id))
        expected_message = "You can't delete a note you didn't create"
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_delete_suppliers_note(self):
        """Test method for deleting suppliers note"""
        response = self.query_with_token(
            self.access_token,
            delete_supplier_note(self.suppliers_note.id))
        self.assertIn("Supplier note was deleted successfully",
                      response["data"]["deleteSuppliernote"]["success"])
        self.assertNotIn("errors", response)
