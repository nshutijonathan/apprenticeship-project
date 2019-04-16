
personal_event = '''
        mutation{
            createEvent(
                eventTypeId: "xaf36lbw1",
                start: "2019-04-06",
                end: "2019-04-06",
                eventTitle: "HealthID end of year party",
                description: "This is the party of the year"
            ){
                event{
                    id,
                    start,
                    end,
                    eventTitle,
                    description
            }
            }
            }
        '''

business_event = '''
            mutation{
                createEvent(
                    eventType: "852k75gnn",
                    start: "2019-04-06",
                    end: "2019-04-06",
                    eventTitle: "HealthID end of year party",
                    description: "This is the party of the year"
                ){
                    event{
                        id,
                        start,
                        end,
                        eventTitle,
                        description
                }
                }
                }
            '''

new_event = '''
                mutation{
                updateEvent(
                    id: "4",
                    eventTypeId: "xaf36lbw1",
                    start: "2019-04-06",
                    end: "2019-04-06",
                    eventTitle: "HealthID end of party",
                    description: "This is the party of the year"
                ){
                    event{
                        id,
                        start,
                        end,
                        eventTitle,
                        description
                }
                }
                }
            '''


def wrong_user_update_event(event_id):
    return (f'''
                mutation{{
                updateEvent(
                    id: \"{event_id}\",
                    eventTypeId: "xaf36lbw1",
                    start: "2019-04-06",
                    end: "2019-04-06",
                    eventTitle: "HealthID end of party",
                    description: "This is the party of the year"
                ){{
                    event{{
                        id,
                        start,
                        end,
                        eventTitle,
                        description
                }}
                }}
                }}
            ''')


def delete_event(event_id):
    return (f'''
                mutation{{
                    deleteEvent(
                        id: \"{event_id}\"
                        ){{
                            success
                            }}
                        }}
            ''')


view_events = '''
                query{
                    events{
                        id,
                        eventTitle,
                        start,
                        end,
                        description,
                        user{
                        id,
                        email
                        }
                    }
                    }
            '''


def view_event(event_id):
    return (f'''
                query{{
                    event(id: \"{event_id}\"){{
                        eventTitle,
                        start,
                        end,
                        description,
                        user{{
                        id,
                        email
                        }}
                    }}
                    }}
            ''')


view_wrong_event = '''
                query{
                    event(id: "2"){
                        eventTitle,
                        start,
                        end,
                        description,
                        user{
                        id,
                        email
                        }
                    }
                    }
            '''


def wrong_user_delete_event(event_id):
    return (f'''
                mutation{{
                    deleteEvent(
                        id: \"{event_id}\"
                        ){{
                            success
                            }}
                        }}
            ''')


outlet_event = '''
            mutation{
                createEvent(
                    eventType: "16lbwaaf3",
                    start: "2019-04-06",
                    end: "2019-04-06",
                    eventTitle: "HealthID end of year party",
                    description: "This is the party of the year"
                ){
                    event{
                        id,
                        start,
                        end,
                        eventTitle,
                        description
                }
                }
                }
            '''

event_type = '''
                mutation{
                    createEventType(
                        name: "Personal"
                    ){
                        eventType{
                        id
                        name
                        }
                    }
                    }
            '''

view_event_types = '''
                    query{
                        eventTypes{
                            id
                            name
                        }
                        }
                '''

wrong_event_type = '''
        mutation{
            createEvent(
                eventTypeId: "f36bw1",
                start: "2019-04-06",
                end: "2019-04-06",
                eventTitle: "HealthID end of year party",
                description: "This is the party of the year"
            ){
                event{
                    id,
                    start,
                    end,
                    eventTitle,
                    description
            }
            }
            }
        '''
