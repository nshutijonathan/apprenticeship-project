register_user_query = '''
                mutation{{
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
                   mobileNumber:"+256 770777777",
                   password:"Passsword12"
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


query_str = '''
      mutation{{
          updateAdminUser(
              firstName:"{firstname}",
              lastName:"{lastname}",
              username:"{username}",
              secondaryEmail:"{email}",
              secondaryPhoneNumber:"{phone}",
              ){{
              user{{
                  firstName
                  lastName
                  username
                  secondaryEmail
              }},
              success
          }}
      }}
      '''
