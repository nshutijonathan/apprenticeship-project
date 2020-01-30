order = '''
mutation{{
  initiateOrder(
    name:"Important order",
    deliveryDate:"2019-05-30",
    productAutofill: true,
    supplierAutofill: true,
    destinationOutlet: {outlet_id}
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
edit_order = '''
mutation{{
  editInitiatedOrder(
    orderId:{order_id},
    name:"Important order",
    deliveryDate:"2019-05-30",
    productAutofill: false,
    supplierAutofill: false,
    destinationOutletId: {outlet_id}
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
      supplierOrderNumber
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
      supplierOrderNumber
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
      supplierOrderNumber
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

modify_order_quantities = '''
mutation{{
  addOrderDetails(
    orderId: {order_id},
    products: [{product}]
    quantities: [{quantity}]
    costPerItems: ["{costPerItems}"],
    prices: ["{prices}"]
  ){{
    message
    orderDetails{{
      id
      supplierOrderNumber
      product{{
        id
      }}
    }}
    suppliersOrderDetails{{
      id
      orderDetails {{
        orderedQuantity
      }}
    }}
  }}
}}
'''

modify_order_quantities_only = '''
mutation{{
  addOrderDetails(
    orderId: {order_id},
    products: [{product}]
    quantities: [{quantity}]
    message
    orderDetails{{
      id
      supplierOrderNumber
      product{{
        id
      }}
    }}
    suppliersOrderDetails{{
      id
      orderDetails {{
        orderedQuantity
      }}
    }}
  }}
}}
'''

remove_order_detail = '''
mutation{{
  deleteOrderDetail(
    orderDetailId:"{order_detail_id}",
  ){{
     message
  }}
}}
'''

products_query = '''
query{
  productAutofill {
    id
    productName
    autofillQuantity
  }
}
'''

supplier_autofill_query = '''
query{
  supplierAutofill {
    preferredSupplier {
      id
      supplierId
      name
    }
    backupSupplier {
      id
      supplierId
      name
    }
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
      orderedQuantity
      supplier {{
        name
      }}
    }}
    supplierOrderName
    supplierOrderNumber
    deliverTo
    deliveryDue
    additionalNotes
    grandTotal
  }}
}}
'''


all_suppliers_order_forms = '''{{
  allSuppliersOrderForms {{
     supplierOrderFormId
     orderId
     orderName
     status
     supplierId
     supplierOrderName
     supplierOrderNumber
     numberOfProducts
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
      orderedQuantity
      supplier {{
        name
      }}
    }}
    supplierOrderName
    supplierOrderNumber
    deliverTo
    deliveryDue
    additionalNotes
  }}
}}
'''

approve_supplier_order = '''
mutation{{
  approveSupplierOrder(
    additionalNotes: "{additional_notes}",
    orderId: {order_id},
    supplierOrderIds: {supplier_order_ids}
    ){{
      message
      supplierOrderDetails {{
        id
        approved
      }}
    }}
  }}
'''

send_supplier_order_emails = '''
mutation{{
  sendSupplierOrderEmails(
    orderId: {order_id},
    supplierOrderIds: {supplier_order_ids}
    ){{
      message
    }}
  }}
'''

mark_supplier_order_as_sent = '''
mutation{{
  markSupplierOrderAsSent(
    orderId: {order_id},
    supplierOrderIds: {supplier_order_ids}
    ){{
      message
    }}
  }}
'''

retrieve_orders = '''
query {
  orders {
    id
    name
    orderNumber
    status
    supplierorderdetailsSet {
      id
      supplierOrderName
      supplierOrderNumber
      numberOfProducts
      supplier {
        id
        name
      }
    }
  }
}
'''

retrieve_order = '''
query {{
  order(orderId: {order_id}) {{
    id
  }}
}}
'''

retrieve_open_orders = '''
query {{
  ordersSortedByStatus(status: "{status}") {{
    id
  }}
}}
'''

retrieve_closed_orders = '''
query {
  closedOrders {
    id
  }
}
'''

close_order = '''
mutation{{
  closeOrder(
    orderId:{order_id}
  ){{
    message
  }}
}}
'''

retrieve_orders_default_paginated = '''
query {
  orders {
    id
  }
  totalOrdersPagesCount
}
'''

retrieve_open_orders_default_paginated = '''
query {{
  ordersSortedByStatus(status: "{status}") {{
    id
    closed
  }}
  totalOrdersPagesCount
}}
'''

retrieve_closed_orders_default_paginated = '''
query {
  closedOrders {
    id
    closed
  }
  totalOrdersPagesCount
}
'''
retrieve_orders_custom_paginated = '''
query {{
  orders(pageCount:{pageCount} pageNumber: {pageNumber}) {{
    id
  }}
  totalOrdersPagesCount
}}
'''

retrieve_open_orders_custom_paginated = '''
query {{
  ordersSortedByStatus(pageCount:{pageCount}
  pageNumber: {pageNumber} status: "{status}")
    {{
    id
    closed
  }}
  totalOrdersPagesCount
}}
'''

retrieve_closed_orders_custom_paginated = '''
query {{
  closedOrders(pageCount:{pageCount} pageNumber: {pageNumber}) {{
    id
    closed
  }}
  totalOrdersPagesCount
}}
'''

auto_order = '''
query{
  autosuggestProductOrder{
    productName,
    suggestedQuantity
  }
}
'''

order_details_status_change = '''
mutation{{
  markSupplierOrderStatusApproved(
    supplierOrderId: "{supplier_order_id}"
    ){{
      message
    }}
  }}
'''

add_order_notes = '''
mutation{{
  addOrderNotes(
    orderId: {order_id},
    supplierOrderId: "{supplier_order_id}",
    additionalNotes: "Testing add note"
    ){{
      message
    }}
  }}
'''
