def create_fieldset(template_id):
    return (f'''
                mutation{{
                    createFieldSet(
                        cashier: "Cashier is",
                        discountTotal: "Discounted by",
                        totalTax: "A tax of",
                        subtotal: "subtotal of",
                        purchaseTotal: "total",
                        changeDue: "your change",
                        loyalty: "loyalty yes",
                        loyaltyEarned: "new points",
                        loyaltyBalance: "total points",
                        amountToPay: "pay",
                        receipt: "your receipt",
                        receiptNo: "no",
                        footer: "Thank you for comming here",
                        receiptTemplateId: \"{template_id}\",
                )
                {{
                    fieldSet{{
                    cashier
                    }}
                }}
                }}
            ''')


def update_fieldset(fieldset_id):
    return (f'''
            mutation{{
                updateFieldSet(
                    id: \"{fieldset_id}\",
                    cashier: "No cashier",
                    discountTotal: "Discounted by",
                    totalTax: "A tax of",
                    subtotal: "subtotal of",
                    purchaseTotal: "total",
                    changeDue: "your change",
                    loyalty: "loyalty yes",
                    loyaltyEarned: "new points",
                    loyaltyBalance: "total points",
                    amountToPay: "pay",
                    receipt: "your receipt",
                    receiptNo: "no",
                    footer: "Thank you for coming here",
                )
                {{
                    fieldSet{{
                    id
                    cashier
                    }}
                }}
            }}
            ''')


def delete_fieldset(fieldset_id):
    return f'''mutation{{
                deleteFieldSet(id: \"{fieldset_id}\"){{success}}
                    }}'''
