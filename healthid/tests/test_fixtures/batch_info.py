batch_info_query = '''
mutation createBatchInfo {{
createBatchInfo (
    supplierId:"{supplier_id}",
     product: [{product_id}],
    dateReceived:"2019-12-03",
    packSize:"10",
    quantities: [10],
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
      unitCost
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
      commentary
      unitCost
    }}
  }}
}}
'''

query_product_batch_info = '''
query {{
  productBatchInfo (id:{product_id}){{
    batchNo
    quantity
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
      quantity
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
