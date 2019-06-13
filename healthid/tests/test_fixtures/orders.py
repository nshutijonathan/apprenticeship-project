order = '''
mutation{{
  initiateOrder(
    name:"Important order",
    deliveryDate:"2019-05-30",
    productAutofill: true,
    supplierAutofill: true
  ){{
  order{{
      id
      orderNumber
      destinationOutlet{{
        id
      }}
  }}
  }}
  }}

'''

suppliers_autofill = '''
mutation{{
  addOrderDetails(
    orderId: {order_id},
    products: [{product}]
  ){{
    message
    orderDetails{{
      id
      product{{
        id
      }}
      order{{
        id
        name
      }}
    }}
  }}
}}
'''

add_suppliers = '''
mutation{{
  addOrderDetails(
    orderId: {order_id},
    products: [{product}]
    suppliers: ["{supplier}"]
  ){{
    message
    orderDetails{{
      id
      product{{
        id
      }}
      order{{
        id
        name
      }}
      supplier{{
        id
      }}
    }}
  }}
}}
'''
add_quantities = '''
mutation{{
  addOrderDetails(
    orderId: {order_id},
    products: [{product}]
    quantities: [23]
  ){{
    message
    orderDetails{{
      id
      product{{
        id
      }}
      order{{
        id
        name
      }}
    }}
  }}
}}
'''
products_query = '''
    query{
      productAutofill{
        id
        productName
        autofillQuantity
      }
    }
'''

suppliers_order_details = '''
query {{
  suppliersOrderDetails(orderId: {order_id}){{
    id
    orderDetails {{
      product {{
        productName
      }}
      quantity
      supplier {{
        name
      }}
    }}
    supplierOrderName
    supplierOrderNumber
    deliverTo {{
      id
    }}
    deliveryDue
    additionalNotes
  }}
}}
'''

supplier_order_details = '''
query {{
  supplierOrderDetails(orderId: {order_id}, supplierId: "{supplier_id}"){{
    id
    orderDetails {{
      product {{
        productName
      }}
      quantity
      supplier {{
        name
      }}
    }}
    supplierOrderName
    supplierOrderNumber
    deliverTo {{
      id
    }}
    deliveryDue
    additionalNotes
  }}
}}
'''
