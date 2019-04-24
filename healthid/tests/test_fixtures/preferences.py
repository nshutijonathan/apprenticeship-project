timezone_query = '''
 query{
  outletPreference(id:"%s"){
    outletTimezone{
      id
      timeZone
    }
    id
  }
}
 '''

timezones_query = '''
 query {
  timezones{
    id
    name
    timeZone
  }
}
 '''

update_timezone_query = '''
mutation{
  updatePreference(
    outletTimezone: "285461788",
    preferenceId: "%s"
  ){
    outletTimezone{id}
  }
}
'''

wrong_timezone = '''
mutation{
  updatePreference(
    outletTimezone: "28546178845757",
    preferenceId: "%s"
  ){
    outletTimezone{id}
  }
}
'''

wrong_query = '''
query{
  outletTimezone(outletId: 2345){
    outletTimezone{
      id
      timeZone
    }
    id
  }
}
'''
