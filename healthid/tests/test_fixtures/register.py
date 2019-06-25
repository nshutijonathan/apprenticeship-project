def create_register_query(outlet_id, receipt_id):
    return (f'''
                mutation{{
                createRegister(
                 name: "liver moore"
                 outletId:{outlet_id},
                 receiptId:\"{receipt_id}\",)
                   {{
                    register{{name}}
                }}
            }}
            ''')


update_register_query = '''
mutation{{
  updateRegister (id:{register_id},
      name: "ever moore"
) {{
    success
      register {{
        name
      }}

  }}
  }}
'''


def delete_register_query(register_id):
    return f'''mutation{{
                deleteRegister(id: {register_id}){{success}}
                    }}'''


def query_register(register_id):
    return (f'''query{{register(id: {register_id}){{id}}}}''')


registers_query = '''
        query{
            registers{
                id
                name
            }
        }
'''
