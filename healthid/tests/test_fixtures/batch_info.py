batch_info_query = '''
mutation createBatchInfo {{
createBatchInfo (
    supplierId:"{supplier_id}",
     product: [{product_id}],
    dateReceived:"2019-12-03",
    packSize:"10",
    quantityReceived:10,
    expiryDate:"{expiry_date}",
    unitCost:100,
    commentary:"5 packs pending"
  ) {{
    errors
    message
    batchInfo {{
      id
      batchNo
      expiryDate
      dateReceived
      supplier{{
        name
      }}
      product {{
        id
        productName
      }}
      unitCost
      quantityReceived
    }}
  }}
}}
'''

update_batch_info = '''
mutation updateBatchInfo {{
updateBatchInfo (
    batchId: "{batch_id}",
    product: [{product_id}],
    supplierId: "{supplier_id}",
    dateReceived: "2019-04-12",
    packSize:"56",
    quantityReceived: {quantity_received},
    expiryDate: "2020-04-02",
    unitCost: 50,
    commentary:"Delivered on time"
  ) {{
    errors
    message
    batchInfo {{
      batchNo
      expiryDate
      dateReceived
      supplier{{
        name
      }}
      unitCost,
      quantityReceived,
      commentary
      product {{
        id
        productName
      }}
      unitCost
    }}
  }}
}}
'''

query_product_batch_info = '''
query {{
  productBatchInfo (id:{product_id}){{
    batchNo
    quantityReceived
    unitCost
    supplier {{
      id
      name
    }}
  }}
}}
'''

single_batch_info = '''
query {{
  batchInfo (id:"{batch_id}") {{
    batchNo
    supplier {{
      id
      name
    }}
    unitCost
    dateReceived
    product {{
      id
      productName
    }}
  }}
}}
'''

all_batch_info = '''
query {
 allBatchInfo {
   batchNo
      supplier {
        name
      }
      unitCost
      quantityReceived
      }
      }
'''

delete_batch_info = '''
mutation deleteBatchInfo {{
  deleteBatchInfo (batchId:"{batch_id}") {{
    message
  }}
}}
'''
