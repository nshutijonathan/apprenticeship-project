
userquery = '''
            mutation {
               createUser(
                   email:"user@gmail.com",
                   mobileNumber:70777777,
                   password:"user",
                   confirmPassword:"user",
               ) {
                 success

               }
            }
            '''
password_error_query = '''
            mutation {
               createUser(
                   email:"user@gmail.com",
                   mobileNumber:70777777,
                   password:"1234",
                   confirmPassword:"1234p",
               ) {

                 errors
               }
            }
            '''

secondquery = '''
            mutation {
               createUser(
                   email:"user@gmail.com",
                   mobileNumber:70777777,
                   password:"user",
                   confirmPassword:"user",
               ) {

                 errors
               }
            }
            '''

login_user_query = '''
            mutation {
               createUser(
                   email:"user@gmail.com",
                   mobileNumber:"070777777",
                   password:"userQ1"
               ) {
                 success
               }
            }
            '''

login_mutation = '''
            mutation GetToken($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password) {
                token
                user {
                    id
                }
                }
            }
            '''

test_users_query = '''
            {
                users {
                    id
                }
            }
            '''
