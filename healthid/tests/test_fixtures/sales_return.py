initiate_sales_return_query = '''
mutation{{
  initiateSalesReturn(outletId:{outlet_id}
    saleId: {sale_id}
    returnAmount:6000
    returnNote: "bad product"
    refundCompensationType: Cash
  returnedProducts:[{{productId: {product_id},
    quantity: 1, price: 3000,
    resellable: false,
    returnReason: ExpiredProduct}}]
  ){{
    message
  }}
}}
'''
