create_consultations = '''
    mutation {
        createConsultationItem (
        consultationName:"Bone marrow",
        description:"would like to seek medical advise regarding bone marrow",
        outletId:6,
        approvedDeliveryFormatIds:[2],
        consultantRoleId:2,
        minutesPerSession: 10,
        pricePerSession:30000
        ){
        consultation{
            id
            description
            consultationName
        business{
            tradingName
            }
        }
        success
    }
    }
'''

retrieve_consultations = '''
query {
  consultations {
        id
        description
        consultationName
       business{
          tradingName
        }
  }
}
'''

retrieve_consultation = '''
query {{
  consultation(consultationId: {consultation_id}) {{
        id
        description
        consultationName
       business{{
          tradingName
        }}
    }}
}}
'''

consultation_id_query = '''
    query {{consultation(consultationId: {consultation_id}){{
        id
        description
        consultationName
        business{{
            tradingName
            }}
    }}
    }}
'''

retrieve_schedule_consultations = '''
    query {
      bookings {
        bookingDate
        status
        consultant
        id
        bookedBy{
          lastName
          firstName
          profileImage
          email
        }
        outlet{
          id
        }
      }
    }
  '''
retrieve_booking = '''
  query {{
  booking (id: {id}) {{
    bookingDate
    status
    consultant
    bookedBy{{
      lastName
      firstName
      profileImage
      email
    }}
    id
  }}
}}
'''
