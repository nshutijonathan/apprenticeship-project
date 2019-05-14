order = '''
mutation{{
  initiateOrder(
    name:"Important order",
    destinationOutlets:[{outlet_id}],
    deliveryDate:"2019-05-30",
    productAutofill: true,
    supplierAutofill: true
  ){{
  order{{
      id
      orderNumber
  }}
  }}
  }}

'''
