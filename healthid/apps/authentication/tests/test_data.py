register_user_query = '''
            mutation {{  
               createUser( 
                   email:"{email}",
                   mobileNumber:"{mobileNumber}",
                   password:"{password}",
               ) {{
                 errors
                 success
               }}
            }}
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
 
