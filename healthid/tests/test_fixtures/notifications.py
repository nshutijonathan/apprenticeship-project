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
