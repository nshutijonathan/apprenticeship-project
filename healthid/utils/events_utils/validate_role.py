from graphql import GraphQLError


class ValidateAdmin():
    '''Class to validate the admin status of an event creator
    '''
    permitted_roles = ['Master Admin', 'Manager']

    def validate_master_admin(self, user, event_type):
        if str(user.role) != 'Master Admin' and event_type == 'Business':
            raise GraphQLError('You are not authorised to carry out Business \
operations!')
        elif (str(user.role) not in self.permitted_roles and event_type ==
              'Outlet'):
            raise GraphQLError('You are not authorised to carry out Outlet \
operations!')
