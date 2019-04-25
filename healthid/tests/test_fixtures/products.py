from healthid.apps.products.models import Product

create_product = '''
        mutation{{
            createProduct(
                productCategoryId:1,
                productName :"panadol",
                measurementUnitId :1,
                packSize :"2kgs",
                description :"first treatment people try for mild to moderate pain",  # noqa E501
                brand :"ventolinllke",
                manufacturer:"Harmon Northrop",
                vatStatus:"VAT",
                quality : "meet the pharmacopoeia specification",
                salesPrice :1000,
                preferedSupplierId :{supplier_id},
                backupSupplierId:{backup_id},
                tags :"painkillers"
                    ){{
                product{{
                    id
                    tags
                    salesPrice
                    quality
                    packSize
                    productName
                    vatStatus
                    nearestExpiryDate
                    skuNumber
                }}
            }}
            }}
'''

supplier_mutation = '''
        mutation{
            addSupplier(input:{
                name: "shadik.",
                email: "email@ntale.com",
                mobileNumber:"0702260027",
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
create_proposed_product = '''
mutation {
    createProduct(
        productCategoryId:1,
        productName :"gfcds",
        measurementUnitId :1,
        packSize :"2kgs",
        description :"first treatment people try for mild to moderate pain",
        brand :"ventolinllke mklllll",
        manufacturer:"vbn",
        vatStatus:"VAT",
        quality : "meet the pharmacopoeia specification",
        salesPrice :1000,
        unitCost:10.2,
        preferedSupplierId :1,
        backupSupplierId:2,
        tags:["painkillers","panadol"]

    ){
      product{
        id
        salesPrice
        quality
        packSize
        productName
        vatStatus
        skuNumber
        tags
      }

    }
}
'''
backup_supplier = '''
        mutation{
            addSupplier(input:{
                name: "shadik.",
                email: "shadick@email.com",
                mobileNumber:"0702260027",
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

product_query = '''
        query{
            approvedProducts{
                skuNumber
                productName
            }
        }
'''

proposed_product_query = '''
        query{
            proposedProducts{
                skuNumber
                productName
            }
        }
'''


def create_product_2(supplier_id, backup_id):
    return Product.objects.create(
        product_category_id=1,
        product_name='Panadol',
        measurement_unit_id=1,
        pack_size="2kgs",
        description='first treatment people try',
        brand='ventolinllke',
        manufacturer="Harmon Northrop",
        vat_status="VAT",
        quality="meet the pharmacopoeia specification",
        sales_price=1000,
        prefered_supplier_id=supplier_id,
        backup_supplier_id=backup_id,
        tags="painkillers",
        unit_cost=10.65
    )


def update_product(product_id, product_name):
    return (f'''
            mutation {{
                updateProposedProduct(
                    id: {product_id},
                    productName: "{product_name}",
                    packSize :"3kgs",
                    description :"forever younger",
                    brand :"ventolinllke",
                    manufacturer:"Harmon",
                    vatStatus:"VAT",
                    quality : "meet the pharmacopoeia specification",
                    salesPrice :1400,
                    tags :["painkillers","headache"]
                ){{
                product{{
                    productName
                }}
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
        filterProducts(productName_Istartswith: "{search_term}"){{
            edges {{
                node {{
                id
                quality
                productName
                tags
                }}
            }}
        }}
    }}
'''
