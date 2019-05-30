create_customer = '''
      mutation{{
        createCustomer(
            firstName:"{first_name}",
            lastName:"{last_name}",
            email: "{email}",
            cityId:{city_id},
            countryId:{country_id},
            primaryMobileNumber:"{primary_mobile_number}",
            secondaryMobileNumber:"{secondary_mobile_number}",
            loyaltyMember:{loyalty_member},
            localGovernmentArea:"Okene",
            addressLine1:"Oshodi 2",
            addressLine2:"Oshodi 1",
            emergencyContactName:"Moses",
            emergencyContactEmail:"{emergency_contact_email}",
            emergencyContactNumber:"+256 788088831"
        ){{
            message
        customer{{
                id
                firstName
                lastName
                primaryMobileNumber
                secondaryMobileNumber
                email
                addressLine1
                addressLine2
                localGovernmentArea
                emergencyContactName
                emergencyContactNumber
                emergencyContactEmail
                loyaltyMember
                createdAt
        }}
        }}
        }}

'''
