create_customer_credit = '''
    mutation{{
        createCustomerCredit(
            customerId:{customer_id},
        )
        {{
            message
            customerCredit{{
            storeCredit
            creditCurrency{{
                id
                name
            }}
            customer{{
                id
                firstName
                lastName
                email
            }}
            }}
        }}
    }}
'''

edit_credit = '''
    mutation {{
        editCustomerWallet(
            customerId:{customer_id},
            storeCredit:{store_credit}
        ){{
    message
    customer{{
      storeCredit
   }}
  }}
}}
'''
