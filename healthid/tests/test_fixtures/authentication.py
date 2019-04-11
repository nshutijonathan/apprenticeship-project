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
        mutation GetToken {{
            tokenAuth(
              email: "{email}",
              password: "{password}"
              ){{
              token
              }}
            }}
        '''

update_username_query = '''
          mutation {{
            updateUser(
              username: "{}"
            ){{
              error
              success
              user{{
              id
              username
              }}
            }}
          }}
        '''

update_email_query = '''
          mutation {{
            updateUser(
              email: "{}"
            ){{
              error
              success
              user{{
              id
              email
              }}
            }}
          }}
        '''

update_image_query = '''
          mutation {{
            updateUser(
              profileImage: "{}"
            ){{
              error
              success
              user{{
              id
              profileImage
              }}
            }}
          }}
        '''

add_user_query = '''
mutation {{
        addUser (
          email:"{email}",
          outletId: ["{outletId}"],
          roleId: "{roleId}",
          mobileNumber:"{mobileNumber}",
          firstName: "Firstname",
          lastName: "Lastname",
          username: "username",
          startingDate: "2019-12-04",
          birthday: "2019-11-15"
        ){{
          user{{
            email
          mobileNumber
          }}
        success
        errors
        }}
      }}
  '''

admin_update_user_query = '''
mutation {{
        adminUpdateUser (
        id:"{id}",
        jobTitle: "{jobTitle}",
        email:"{email}",
        mobileNumber:"{mobileNumber}",
        firstName: "{firstname}",
        lastName: "Lastname",
        username: "newUsername",
        startingDate: "2019-12-10",
        birthday: "2019-11-15"
      ) {{
        errors
        message
        user {{
          id
          firstName
          email
          mobileNumber
          jobTitle
        }}
      }}
      }}
  '''

update_user_role_query = '''
mutation updateRole {{
           updateRole (roleId:"{roleId}",
           userId:"{userId}"){{
           errors
            user {{
              id
              email
              role {{
                name
              }}
            }}
          }}
        }}
'''

add_user_business_query = '''
    mutation addUserBusiness {{
    addUserBusiness (userId:"{userId}", businessId:"{businessId}") {{
        errors
        message
        user {{
          id
          email
        }}
      }}
    }}
'''
