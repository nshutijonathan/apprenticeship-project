
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
