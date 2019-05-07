
create_sales_prompts = '''
mutation{{
  createSalesprompts(
    productIds:[{product_id}],
    outletIds:[{outlet_id}],
    promptTitles:["{title}"],
    descriptions:["{description}"]
  ){{
  message
  }}
  }}

'''

incomplete_sales_entry = '''
mutation{{
  createSalesprompts(
    productIds:[{product_id},{product_id}],
    outletIds:[{outlet_id}],
    promptTitles:["{title}"],
    descriptions:["{description}"]
  ){{
  message
  }}
  }}

'''

update_sales_prompt = '''
mutation{{
   updateSalesprompt(id:{sales_prompt_id},
    promptTitle:"{title}",
    description:"{description}",
    productId:{product_id},
    outletId:{outlet_id}){{
    salesPrompt{{
      id
      promptTitle
      description
    }}
    success
  }}
}}

'''


def delete_sales_prompt(sales_prompt_id):
    return f'''mutation{{
                deleteSalesprompt(id: {sales_prompt_id}){{success}}
                    }}'''


query_all_sales_prompt = '''
        query{
         salesPrompts{
                id
                promptTitle
                description
                product{
                  id
                  productName
                }
               }
}
'''


def query_a_sales_prompt(sales_prompt_id):
    return (f'''query{{salesPrompt(id: {sales_prompt_id}){{id}}}}''')
