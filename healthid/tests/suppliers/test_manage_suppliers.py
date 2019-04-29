from django.core.management import call_command

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.suppliers import (approve_request,
                                                    approve_supplier,
                                                    approved_suppliers,
                                                    decline_request,
                                                    delete_supplier,
                                                    edit_request,
                                                    edit_requests,
                                                    empty_search,
                                                    filter_suppliers,
                                                    invalid_search,
                                                    supplier_mutation,
                                                    user_requests,
                                                    edit_proposal)


class ManageSuppliersTestCase(BaseConfiguration):

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'tests')
        self.supplier = self.query_with_token(
            self.access_token_master,
            supplier_mutation
        )
        self.supplier_id = \
            self.supplier['data']['addSupplier']['supplier']['id']
        self.approve_suppler = self.query_with_token(
            self.access_token_master,
            approve_supplier.format(
                supplier_id=self.supplier_id
            )
        )
        self.request = self.query_with_token(
            self.access_token_master,
            edit_request.format(
                supplier_id=self.supplier_id
            )
        )
        self.request_id = \
            self.request['data']['editSupplier']['editRequest']['id']

    def test_approve_supplier(self):
        response = self.approve_suppler
        self.assertIn(
            'approved!',
            response['data']['approveSupplier']['success'])

    def test_delete_supplier(self):
        response = self.query_with_token(
            self.access_token_master,
            delete_supplier.format(
                supplier_id=self.supplier_id
            )
        )
        self.assertIn(
            'deleted!',
            response['data']['deleteSupplier']['success'])

    def test_propose_edit(self):
        self.assertIn('sent!', self.request['data']['editSupplier']['message'])

    def test_edit_proposal(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_proposal.format(
                proposal_id=self.request_id)
        )
        self.assertIn('updated!', response['data']['editProposal']['message'])

    def test_cannot_edit_request_you_didnot_propose(self):
        response = self.query_with_token(
            self.access_token,
            edit_proposal.format(
                proposal_id=self.request_id)
        )
        self.assertIn('didnot propose!', response['errors'][0]['message'])

    def test_query_edit_requests(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_requests
        )
        self.assertIsNotNone(response['data']['editRequests'])

    def test_approve_edit_request(self):
        response = self.query_with_token(
            self.access_token_master,
            approve_request.format(
                request_id=self.request_id
            )
        )
        self.assertIn(
            'updated!',
            response['data']['approveEditRequest']['message'])

    def test_decline_edit_request(self):
        response = self.query_with_token(
            self.access_token_master,
            decline_request.format(
                request_id=self.request_id
            )
        )
        self.assertIn(
            'declined!',
            response['data']['declineEditRequest']['message'])

    def test_query_approved_suppliers(self):
        response = self.query_with_token(
            self.access_token,
            approved_suppliers
        )
        self.assertIsNotNone(response['data']['approvedSuppliers'][0])

    def test_query_user_edit_requests(self):
        response = self.query_with_token(
            self.access_token,
            user_requests
        )
        self.assertListEqual([], response['data']['userRequests'])

    def test_filter_supplier(self):
        response = self.query_with_token(
            self.access_token,
            filter_suppliers
        )
        self.assertEqual(
            'shadik.',
            response['data']['filterSuppliers']['edges'][0]['node']['name'])

    def test_empty_search_result(self):
        response = self.query_with_token(
            self.access_token,
            empty_search
        )
        self.assertIn('does not exist!', response['errors'][0]['message'])

    def test_search_parameter(self):
        response = self.query_with_token(
            self.access_token,
            invalid_search
        )
        self.assertIn('Please provide a valid search keyword',
                      response['errors'][0]['message'])
