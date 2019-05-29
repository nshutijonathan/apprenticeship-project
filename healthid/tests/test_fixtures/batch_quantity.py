propose_quantity = '''
mutation proposeQuantity {{
   proposedQuantity (
    batchId: "{batch_id}"
    product: [{product_id}],
    proposedQuantities: [11],

  ) {{
    notification
    batchInfo {{
      batchNo
      expiryDate
      dateReceived
      quantity
      supplier{{
        name
      }}
      unitCost,
      quantity,
      commentary,
      unitCost
    }}
  }}
}}
'''

propose_quantity2 = '''
mutation proposeQuantity {{
   proposedQuantity (
    batchId: "{batch_id}"
    product: [{product_id}],
    proposedQuantities: [11, 90],

  ) {{
    notification
    batchInfo {{
      batchNo
      expiryDate
      dateReceived
      quantity
      supplier{{
        name
      }}
      unitCost,
      quantity,
      commentary,
      unitCost
    }}
  }}
}}
'''

approve_quantity = '''
mutation approveProposedQuantity {{
   approveQuantity (
    batchId: "{batch_id}" ,
    product: {product_id},
    isApproved: {value},
    comment: "Reject"


  ){{
   message
   quantityInstance{{
    id
    isApproved
    quantityReceived
    product{{
      productName
      id
     productQuantity
    }}
    authorizedBy{{
      id
      email
    }}
  }}
  }}
}}
'''
