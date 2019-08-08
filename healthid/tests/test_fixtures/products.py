from healthid.apps.products.models import Product

create_product = '''
        mutation{{
            createProduct(
                productCategoryId:1,
                productName :"panadol",
                measurementUnitId :1,
                description :"first treatment people try for mild to moderate pain",  # noqa E501
                brand :"ventolinllke",
                manufacturer:"Harmon Northrop",
                vatStatus:true,
                loyaltyWeight: 1
                preferredSupplierId :"{supplier_id}",
                backupSupplierId:"{backup_id}",
                tags :["painkillers"]
                    ){{
                product{{
                    id
                    tags
                    salesPrice
                    productName
                    vatStatus
                }}
            }}
            }}
'''

supplier_mutation = '''
        mutation{
            addSupplier(input:{
                name: "shadik.",
                email: "email@ntale.com",
                mobileNumber:"+256702260027",
                addressLine1:"address",
                addressLine2:"addressline2",
                lga: "lga",
                tierId: 1,
                cityId: 1
                rating:5,
                creditDays:4,
                logo:"logo",
                paymentTermsId: 1,
                commentary: "no comment"
            }){
                supplier{
                supplierId
                id
                user{
                    email
                }
                city{
                    name
                }
                supplierId
                }
            }
            }
'''
create_proposed_product = '''
mutation {{
    createProduct(
        productCategoryId:1,
        productName :"gfcds",
        measurementUnitId :1,
        description :"first treatment people try for mild to moderate pain",
        brand :"ventolinllke mklllll",
        manufacturer:"vbn",
        vatStatus: true,
        loyaltyWeight: 1
        preferredSupplierId : "{0}",
        backupSupplierId:"{0}",
        tags:["painkillers","panadol"]

    ){{
      product{{
        id
        salesPrice
        productName
        vatStatus
        skuNumber
        tags
      }}

    }}
}}
'''
backup_supplier = '''
        mutation{
            addSupplier(input:{
                name: "shadik.",
                email: "shadik@email.com",
                mobileNumber:"+256702260027",
                addressLine1:"address",
                addressLine2:"addressline2",
                lga: "lga",
                tierId: 1,
                cityId: 1
                rating:5,
                creditDays:4,
                logo:"logo",
                paymentTermsId: 1,
                commentary: "no comment"
            }){
                supplier{
                supplierId
                id
                city{
                    name
                }
                supplierId
                }
            }
            }
'''

approved_product_query = '''
query{
    approvedProducts {
        skuNumber
        productName
    }
}
'''

proposed_product_query = '''
query{
    proposedProducts {
        skuNumber
        productName
    }
}
'''


def create_product_2(supplier_id, backup_id, user, outlet):
    return Product.objects.create(
        product_category_id=1,
        product_name='Panadol',
        measurement_unit_id=1,
        description='first treatment people try',
        brand='ventolinllke',
        manufacturer="Harmon Northrop",
        vat_status=True,
        sales_price=1000,
        preferred_supplier_id=supplier_id,
        backup_supplier_id=backup_id,
        tags="painkillers",
        is_approved=True,
        outlet=outlet,
        user=user)


def create_new_product(name, description, brand, manufacturer,
                       category, supplier_id, backup_id, user, outlet):
    return Product.objects.create(
        product_category=category,
        product_name=name,
        measurement_unit_id=1,
        description=description,
        brand=brand,
        manufacturer=manufacturer,
        vat_status=True,
        sales_price=1000,
        preferred_supplier_id=supplier_id,
        backup_supplier_id=backup_id,
        tags="painkillers",
        is_approved=True,
        outlet=outlet,
        user=user)


def update_product(product_id, product_name):
    return (f'''
            mutation {{
                updateProduct(
                    id: {product_id},
                    productName: "{product_name}",
                    description :"forever younger",
                    brand :"ventolinllke",
                    manufacturer:"Harmon",
                    vatStatus:true,
                    salesPrice :1400,
                    tags :["painkillers","headache"]
                ){{
                product{{
                    productName
                    id
                    user{{id}}
                }}
                message
                }}
            }}
        ''')


def delete_product(product_id):
    return (f'''
            mutation{{
            deleteProduct(
                    id: {product_id}
            ){{
                success
            }}
            }}
    ''')


approve_product = '''
        mutation {{
            approveProduct(
            productId:{product_id}
            ){{
            product{{
                id
            }}
            success
            }}
        }}
    '''
set_price_string = '''
    mutation{{
        updatePrice(
            markup:{markup}
            productIds:{product_ids}
            autoPrice:{auto_price}
            salesPrice:{sales_price}
        ){{
            products{{
            id
            unitCost
            markup
            salesPrice
            }}
            errors
            message
        }}
    }}
'''
product_search_query = '''
query{{
    filterProducts(
        productName_Istartswith: "{search_term}"
        ){{
        edges {{
            node {{
            id
            productName
            tags
            }}
        }}
    }}
}}
'''

generalised_product_search_query = '''
query{{
    products(search: "{search_term}"){{
        id
        productName
        description
        brand
        skuNumber
        manufacturer
        productCategory{{
        id
        name
        }}
        preferredSupplier{{
        id
        name
        }}
    }}
}}
'''

update_loyalty_weight = '''
mutation{{
  updateLoyaltyWeight (productCategoryId:{product_category},
      loyaltyValue: {loyalty_value}
) {{
      category {{
    id
    name
    productSet {{
       edges {{
        node {{
          id
          productName
          loyaltyWeight
        }}
      }}
    }}
  }}
  }}
  }}
'''

update_a_product_loyalty_weight = '''
mutation{{
  productLoyaltyWeightUpdate (id:{product_id},
      loyaltyValue: {loyalty_value}
) {{
    product{{
      id
      productName
      loyaltyWeight
    }}
  }}
  }}
'''

proposed_edits_query = '''
query{
    proposedEdits {
        id
        productName
    }
}
'''

product_query = '''
query{
    products {
        id
        productName
    }
}
'''

create_product_category = '''
    mutation {{
    createProductCategory(
        name:"panadol",
        outletId: {outlet_id}
        isVatApplicable: true
        loyaltyWeight: 1
        markup: 20
        ){{
        productCategory{{
            id
            name
            isVatApplicable
            markup
        }}
        message
        }}
}}
    '''

edit_product_category = '''
    mutation {
    editProductCategory(
      id:6,
      name:"panadolextra"
    ){
      productCategory{
        id
        name
      }
    message

    }
}

'''

delete_product_category = '''
    mutation{
    deleteProductCategory(
        id:7
    ){
    success
    }
    }

'''
create_measuremt_unit = '''
        mutation {
        createMeasurementUnit(
            name:"tablets"

        ){
        measurementUnit{
            id
            name
        }
        message

        }
    }


'''

edit_measurement_unit = '''
    mutation {
        editMeasurementUnit(
        id:6,
            name:"syrup"

        ){
        measuremntUnit{
            id
            name
        }
        message

    }
}


'''


def deactivate_product(product_ids):
    return (f'''
            mutation {{
                deactivateProduct(productIds: {product_ids}){{
                    success
                }}
            }}
    ''')


def retrieve_deactivated_products(outlet_id):
    return (f'''
            query {{
                deactivatedProducts {{
                    id
                    productName
                }}
            }}
    ''')


def activate_product(product_ids):
    return (f'''
            mutation {{
                activateProduct(productIds: {product_ids}){{
                    success
                }}
            }}
    ''')


approve_proposed_edits = '''
    mutation {{
        approveProposedEdits(
        productId:{product_id}
        editRequestId:{edit_request_id}
        ){{
        product{{
        productName
        parent{{
            id
        }}
            isApproved
        }}
        message
        }}
    }}
'''

decline_proposed_edits = '''
mutation {{
    declineProposedEdits(
        productId:{product_id}
        editRequestId:{edit_request_id},
        comment:"Your edit request has not been accepted"
    ){{
    editRequest{{
    productName
    parent{{
        id
    }}
        isApproved
    }}
            message
    }}
}}
'''
