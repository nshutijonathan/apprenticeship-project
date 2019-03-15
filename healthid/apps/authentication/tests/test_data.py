userquery = '''
            mutation {  
               createUser( 
                   email:"user@gmail.com",
                   mobileNumber:"70777777",
                   password:"userQ1",
               ) {
                 success
               
               }
            }
            '''
password_error_query = '''
            mutation {  
               createUser( 
                   email:"user@gmail.com",
                   mobileNumber:"70777777",
                   password:"weakpassword",
          
               ) {
                 
                 errors
               }
            }
            '''

secondquery = '''
            mutation {  
               createUser( 
                   email:"user@gmail.com",
                   mobileNumber:"70777777",
                   password:"userQ1"
               ) {
               
                 errors
               }
            }
            '''


query_string = '''
            mutation {{  
               createUser( 
                   email:"{email}",
                   mobileNumber:"{mobileNumber}",
                   password:"{password}",
               ) {{
                 errors

               
               }}
            }}
'''
