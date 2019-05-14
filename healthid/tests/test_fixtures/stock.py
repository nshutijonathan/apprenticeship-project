
create_stock_template_string = '''
        mutation{{
        createStockCountTemplate(
            productIds:{product_ids}
            assignedUserIds:{assigned_user_ids}
            designatedUserIds:{dessignate_user_ids}
            outletId:{outlet_id}
            eventId:{event_id}
        ){{
            stockTemplate{{
            id
            products{{
                pageInfo{{
                hasNextPage
                hasPreviousPage
                endCursor
                }}
                edges{{
                node{{
                    productName
                    id
                    unitCost
                }}
                }}
            }}
            assignedUsers{{
                    id
            }}
            designatedUsers{{
                id
                role{{
                name
                }}
            }}
            }}
            success
        }}
        }}
'''


edit_stock_template_string = '''
        mutation{{
        editStockCountTemplate(
            templateId:{template_id}
            productIds:{product_ids}
            assignedUserIds:{assigned_user_ids}
            designatedUserIds:{dessignate_user_ids}
            outletId:{outlet_id}
            eventId:{event_id}
        ){{
            stockTemplate{{
            id
            products{{
                pageInfo{{
                hasNextPage
                hasPreviousPage
                endCursor
                }}
                edges{{
                node{{
                    productName
                    id
                    unitCost
                }}
                }}
            }}
            assignedUsers{{
                    id
            }}
            designatedUsers{{
                id
                role{{
                name
                }}
            }}
            }}
            success
        }}
        }}
'''

delete_stock_template_string = '''
        mutation deleteTemplate{{
        deleteStockCountTemplate(templateId:{id}){{
            success
            errors
        }}
        }}
'''


query_all_templates = '''
        query {{
        stockTemplates(outletId:{outlet_id}) {{
            id
            assignedUsers {{
            id
            email
            }}
            designatedUsers {{
            id
            email
            }}
            createdAt
            outlet {{
            id
            name
            }}
            scheduleTime {{
            eventTitle
            description
            }}
            products{{
            edges{{
                node{{
                id
                productName
                }}
            }}
            }}
        }}
        }}

'''

query_single_template = '''
        query singleTemplate {{
        stockTemplate(templateId:{template_id}, outletId:{outlet_id}) {{
            id
            assignedUsers {{
            id
            email
            }}
            designatedUsers {{
            id
            email
            }}
            scheduleTime {{
            eventTitle
            description
            }}
            products {{
            edges {{
                node {{
                id
                productName
                }}
            }}
            }}
        }}
        }}

'''
