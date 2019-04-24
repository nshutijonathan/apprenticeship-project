batch_expiry_query = '''
query{
  batchExpiries(endDate:"2019-05-30"){
      id
      batchNo
      expiryDate
      product{
          id
          productName
          }
        supplier{
            name
            }
        }
    }
'''
wrong_expiry_date = '''
query{
  batchExpiries(
    date:"2019-30"
    ){
        id
        batchNo
        expiryDate
    product {
      id
      productName
    }
    supplier{
      name
    }
    }
}
'''

query_expired_products = '''
query{
  expiredBatches{
    id
    batchNo
    expiryDate
    product {
      id
      productName
    }
    supplier{
      name
    }
  }
}
'''
