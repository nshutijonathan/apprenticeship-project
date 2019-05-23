from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.notifications import (view_notifications)


class NotificationTests(BaseConfiguration):
    '''Class to test app notifications
    '''

    def test_no_notification(self):
        '''Test that an error message is returned
        when there are no notifications
        '''
        response = self.query_with_token(self.access_token, view_notifications)
        self.assertEqual(response['errors'][0]['message'],
                         'Oops! There are no notifications yet!')
