create_product = '''
        mutation{{
            createProduct(
                productCategoryId:1,
                productName :"",
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
            products{
                skuNumber
                productName
            }
        }

'''
