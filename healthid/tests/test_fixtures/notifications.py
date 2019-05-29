view_notifications = '''
                    query{
                        notifications{
                            id,
                            message,
                            createdAt
                        }
                        }
            '''

toggle_permissions = '''
                    mutation{
                        toggleEmailPermissions{
                            success,
                            errors
                        }
                        }
                '''
update_notification_status = '''
                mutation {{
                    updateReadStatus(id: "{notification_id}"){{
                        success
                        notification {{
                            message
                        }}
                    }}
                }}
'''

delete_notification = '''
                mutation {{
                    deleteNotification(id: "{notification_id}"){{
                        success
                    }}
                }}
'''
