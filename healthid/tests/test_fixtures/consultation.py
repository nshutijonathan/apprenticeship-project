from healthid.apps.consultation.models import (Consultation,
                                               ScheduleConsultation)

consultations = '''
  query{{consultation(id:{id}){{
    id
    consultationName
  }}
  }}
'''


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


def create_consultation(outlet_id, consultation_name):
    consultation = Consultation()
    consultation.consultation_name = consultation_name
    consultation.price_per_session = 34
    consultation.approved_delivery_formats_id = 2
    consultation.expected_time_id = 1
    consultation.consultant_role_id = 1
    consultation.outlet_id = outlet_id
    consultation.save()
    return consultation


def post_consultation(consultation_type):
    schedule_consultation = ScheduleConsultation()
    schedule_consultation.customer_name = "Nangai"
    schedule_consultation.consultation_type = consultation_type
    schedule_consultation.save()
    return schedule_consultation


def schedule_mutation(consultation_type_id, user_id, start_date):
    return f'''
        mutation {{
            schedule(
                consultationTypeId: {consultation_type_id},
                customerName: "Nangai",
                email: "arthur.nangai@gmail.com",
                paymentStatus: NOT_PAID,
                consultants: [\"{user_id}\"],
                startDate: \"{start_date}\",
                endDate: "2019-04-06",
                startTime: "12:30",
                endTime: "01:30",
                eventTypeId: "x7f36lbw1"
            ) {{
                scheduleConsultation {{
                customerName
                consultants{{
                    id
                }}
                event{{
                    startDate
                }}
                }}
            }}
            }}
        '''
