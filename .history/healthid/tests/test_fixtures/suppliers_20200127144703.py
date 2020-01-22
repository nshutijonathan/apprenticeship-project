supplier_mutation = '''
        mutation{
          addSupplier(
            input:{
              name: "shadik.",
              tierId: 1
            },
            contactsInput: {
              email: "email@ntale.com",
              mobileNumber:"+256702260027",
              addressLine1:"address",
              addressLine2:"addressline2",
              lga: "lga",
              cityId: 1
              countryId:1,
            },
            metaInput: {
              creditDays:4,
              logo:"logo",
              paymentTerms: "ON_CREDIT",
              commentary: "no comment"
            }
          ){
            supplier{
              id
              name
              tier { name }
              supplierContacts{
                email
                mobileNumber
                addressLine1
                city {}
                country
              }
              supplierMeta{
                displayName
                creditDays
                logo
                paymentTerms
                commentary
              }
            }
          }
        }
'''

email_invalid = '''
        mutation{
          addSupplier(
            input:{
              name: "shadik.",
              tierId: 1
            },
            contactsInput: {
              email: "email",
              mobileNumber:"+256702260027",
              addressLine1:"address",
              addressLine2:"addressline2",
              lga: "lga",
              cityId: 1
              countryId:1,
            },
            metaInput: {
              creditDays:4,
              logo:"logo",
              paymentTerms: "ON_CREDIT",
              commentary: "no comment"
            }
          ){
            supplier{
              id
              name
              tier { name }
              supplierContacts{
                email
                mobileNumber
                addressLine1
                city{
                  name
                }
                country {
                  name
                }
              }
              supplierMeta{
                displayName
                creditDays
                logo
                paymentTerms
                commentary
              }
            }
          }
        }
'''

mobile_invalid = '''
        mutation{
          addSupplier(
            input:{
              name: "shadik.",
              tierId: 1
            },
            contactsInput: {
              email: "email@ntale.com",
              mobileNumber:"+256",
              addressLine1:"address",
              addressLine2:"addressline2",
              lga: "lga",
              cityId: 1
              countryId:1,
            },
            metaInput: {
              creditDays:4,
              logo:"logo",
              paymentTerms: "ON_CREDIT",
              commentary: "no comment"
            }
          ){
            supplier{
              id
              name
              tier { name }
              supplierContacts{
                email
                mobileNumber
                addressLine1
                city {
                  name
                }
                country {
                  name
                }
              }
              supplierMeta{
                displayName
                creditDays
                logo
                paymentTerms
                commentary
              }
            }
          }
        }
'''

suppliers_query = '''
        query{
            allSuppliers{
                id
                name
            }
        }

'''


supplier_query_by_id = '''
            query{{
              singleSupplier(id: "{id}"){{
              id
              name
              }}
            }}
'''

supplier_query_by_name = '''
            query{{
              singleSupplier(name: "{name}"){{
              id
              name
              }}
            }}
'''
suppliers_totalnumber_query = '''
        query{
            allSuppliers{
                id
                name
            }
            totalNumberOfSuppliers
        }

'''
approved_suppliers = '''
        query{
            approvedSuppliers{
                id
                name
            }
        }

'''

approve_supplier = '''
        mutation{{
          approveSupplier(id:"{supplier_id}"){{
            success
          }}
        }}

'''
delete_supplier = '''
        mutation{{
          deleteSupplier(id:"{supplier_id}"){{
            success
          }}
        }}

'''

edit_request = '''
        mutation{{
          editSupplier(
            id: "{supplier_id}"
            name: "shack",
            tierId:1,
            meta: {{
              creditDays:4,
              logo:"logo",
              paymentTerms: "ON_CREDIT",
              commentary: "no comment",
              displayName: "Shak 2"
            }}
          ){{
            message,
            editRequest{{
              id
              name
            }}
          }}
        }}

'''

edit_proposal = '''
        mutation{{
          editProposal(
            id: "{proposal_id}"
            name: "sean2",
          ){{
            message,
            editRequest{{
              name
            }}
          }}
        }}

'''

edit_requests = '''
        query{
            editSuppliersRequests{
            id
            name
            isApproved
          }
        }
'''
approve_request = '''
        mutation{{
          approveEditRequest(id:"{request_id}"){{
            message
          }}
        }}
'''
decline_request = '''
        mutation{{
          declineEditRequest(
          id:"{request_id}"
          comment: "No way!"){{
            message
          }}
        }}
'''
filter_suppliers = '''
        query{
          filterSuppliers(name_Icontains: "sha"){
            edges{
              node{
                id
                name
              }
            }
          }
        }
'''

empty_search = '''
        query{
          filterSuppliers(name_Icontains: "Kenya"){
            edges{
              node{
                id
                name
              }
            }
          }
        }
'''
invalid_search = '''
        query{
          filterSuppliers(tier_Name_Icontains: ""){
            edges{
              node{
                id
                name
              }
            }
          }
        }
'''

user_requests = '''
        query{
            userRequests{
            id
            name
          }
        }
'''

create_suppliers_note = '''
      mutation{{
        createSuppliernote(
          supplierId:"{supplier_id}",
          note:"{note}",
          outletIds:[{outlet_id}]
        ){{
          message
          supplierNote{{
            id
            note
            user{{
              id
              email
            }}
          }}
          supplier{{
            id
            name
          }}

        }}
      }}

'''

update_suppliers_note = '''
      mutation{{
        updateSuppliernote(
          id:{supplier_note},
          note:"{note}",
          outletIds:[{outlet_id}]
        ){{
          success
          supplierNote{{
                id
                note
                user{{
                  id
                  email
                  }}
            supplier{{
              id
              name
            }}
          }}
        }}
      }}

'''


all_suppliers_note = '''
    query{
      allSuppliersNote{
        id
        note
        user{
          id
          email
        }
        supplier{
          id
          name
        }
      }
    }

'''

all_suppliers_default_paginated = '''
{
  allSuppliers{
    id
    name
  }
  totalSuppliersPagesCount
}
'''

approved_suppliers_default_pagination_query = '''
        {
            approvedSuppliers{
                id
                name
            }
            totalSuppliersPagesCount
        }

'''
suppliers_notes_default_pagination = '''
{
  allSuppliersNote{
    supplier {
      id
    }
  }
  totalSuppliersPagesCount
}

'''

all_suppliers_custom_paginated = '''
{{
  allSuppliers(pageCount:{pageCount} pageNumber:{pageNumber}){{
    id
    name
  }}
  totalSuppliersPagesCount
}}
'''

approved_suppliers_custom_pagination_query = '''
    {{
      approvedSuppliers(pageCount:{pageCount} pageNumber:{pageNumber}){{
            id
            name
        }}
        totalSuppliersPagesCount
    }}

'''
suppliers_notes_custom_pagination = '''
{{
  allSuppliersNote(pageCount:{pageCount} pageNumber:{pageNumber}){{
    supplier {{
      id
    }}
  }}
  totalSuppliersPagesCount
}}

'''

rate_supplier = '''
mutation{{
  rateSupplier(supplierId:"{supplier_id}", deliveryPromptness:\
  {delivery_promptness},serviceQuality:{service_quality}){{
    message
    supplierRating{{
      id
      rating
      supplier{{
        name
      }}
    }}
  }}
}}
'''

get_supplier_rating = '''query{{supplierRating(\
  supplierId: "{supplier_id}")}}'''


def supplier_notes(supplier_id):
    return (f'''query{{suppliersNote(id: "{supplier_id}"){{id}}}}''')


def delete_supplier_note(supplier_note):
    return f'''mutation{{
                deleteSuppliernote(id: {supplier_note}){{success}}
                    }}'''
