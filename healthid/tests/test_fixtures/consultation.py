def add_consultation(outlet_id, consultationName):
    return (f'''mutation {{
                createConsultation(
                    consultationName:"{consultationName}",
                    description:"I would like to seek medical advise",
                    approvedDeliveryFormatsId:2,
                    expectedTimeId:1,
                    consultantRoleId:1,
                    outletId:{outlet_id},
                    pricePerSession:5
                  ){{
                    consultation{{
                      id
                      description
                      consultationName
                    outlet{{
                        name
                      }}
                  }}
                  success
                  }}
                  }}
                  ''')


consultations = '''
  query{{consultation(id:{id}){{
    id
    consultationName
  }}
  }}
'''
