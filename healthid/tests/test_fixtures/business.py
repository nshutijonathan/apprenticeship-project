authentic_business = '''
                    mutation{
                        createBusiness(
                            legalName:"Kyamoka Knght"
                            tradingName:"Kyamokya Phar"
                            businessEmail:"Kyamoka@andla.com"
                            addressLine1:"30 Bukoto Street"
                            addressLine2:"Kamwokya"
                            city: "Kampala"
                            country: "Uganda"
                            localGovernmentArea: "Kamwokya"
                            phoneNumber:"+2567099988"
                            website:"andela.com"
                            twitter:"andela@twitter.com"
                            instagram:"instragram.andela.com"
                            logo:"rtyuio/tyuio/rtyuhij"
                            facebook: "andela.facebook.com"
                        ){
                            business{
                            id
                            legalName
                            user{
                                id
                                mobileNumber
                                    isSuperuser
                            }
                            }
                            success
                        }
                        }
                    '''

missing_business_email = '''
                    mutation{
                        createBusiness(
                            legalName:"Kyamoka Knght"
                            tradingName:"Kyamokya Phar"
                            businessEmail:""
                            addressLine1:"30 Bukoto Street"
                            addressLine2:"Kamwokya"
                            city: "Kampala"
                            country: "Uganda"
                            localGovernmentArea: "Kamwokya"
                            phoneNumber:"+2567099988"
                            website:"andela.com"
                            twitter:"andela@twitter.com"
                            instagram:"instragram.andela.com"
                            logo:"rtyuio/tyuio/rtyuhij"
                            facebook: "andela.facebook.com"
                        ){
                            business{
                            id
                            legalName
                            user{
                                id
                                mobileNumber
                                    isSuperuser
                            }
                            }
                            success
                        }
                        }
                    '''

missing_trading_name = '''
                    mutation{
                        createBusiness(
                            legalName:"Kyamoka Knght"
                            tradingName:""
                            businessEmail:"Kyamoka@andla.com"
                            addressLine1:"30 Bukoto Street"
                            addressLine2:"Kamwokya"
                            city: "Kampala"
                            country: "Uganda"
                            localGovernmentArea: "Kamwokya"
                            phoneNumber:"+2567099988"
                            website:"andela.com"
                            twitter:"andela@twitter.com"
                            instagram:"instragram.andela.com"
                            logo:"rtyuio/tyuio/rtyuhij"
                            facebook: "andela.facebook.com"
                        ){
                            business{
                            id
                            legalName
                            user{
                                id
                                mobileNumber
                                    isSuperuser
                            }
                            }
                            success
                        }
                        }
                    '''

missing_address_line_1 = '''
                    mutation{
                        createBusiness(
                            legalName:"Kyamoka Knght"
                            tradingName:"Kyamoka Knght"
                            businessEmail:"Kyamoka@andla.com"
                            addressLine1:""
                            addressLine2:"Kamwokya"
                            city: "Kampala"
                            country: "Uganda"
                            localGovernmentArea: "Kamwokya"
                            phoneNumber:"+2567099988"
                            website:"andela.com"
                            twitter:"andela@twitter.com"
                            instagram:"instragram.andela.com"
                            logo:"rtyuio/tyuio/rtyuhij"
                            facebook: "andela.facebook.com"
                        ){
                            business{
                            id
                            legalName
                            user{
                                id
                                mobileNumber
                                    isSuperuser
                            }
                            }
                            success
                        }
                        }
                    '''

missing_city = '''
                mutation{
                    createBusiness(
                        legalName:"Kyamoka Knght"
                        tradingName:"Kyamoka Knght"
                        businessEmail:"Kyamoka@andla.com"
                        addressLine1:"30 Bukoto Street"
                        addressLine2:"Kamwokya"
                        city: ""
                        country: "Uganda"
                        localGovernmentArea: "Kamwokya"
                        phoneNumber:"+2567099988"
                        website:"andela.com"
                        twitter:"andela@twitter.com"
                        instagram:"instragram.andela.com"
                        logo:"rtyuio/tyuio/rtyuhij"
                        facebook: "andela.facebook.com"
                    ){
                        business{
                        id
                        legalName
                        user{
                            id
                            mobileNumber
                                isSuperuser
                        }
                        }
                        success
                    }
                    }
                '''

missing_phone_number = '''
                mutation{
                    createBusiness(
                        legalName:"Kyamoka Knght"
                        tradingName:"Kyamoka Knght"
                        businessEmail:"Kyamoka@andla.com"
                        addressLine1:"30 Bukoto Street"
                        addressLine2:"Kamwokya"
                        city: "Kampala"
                        country: "Uganda"
                        localGovernmentArea: "Kamwokya"
                        phoneNumber:""
                        website:"andela.com"
                        twitter:"andela@twitter.com"
                        instagram:"instragram.andela.com"
                        logo:"rtyuio/tyuio/rtyuhij"
                        facebook: "andela.facebook.com"
                    ){
                        business{
                        id
                        legalName
                        user{
                            id
                            mobileNumber
                                isSuperuser
                        }
                        }
                        success
                    }
                    }
                '''


def update_business(business_id):
    return (f'''mutation{{
                updateBusiness(
                    id: \"{business_id}\"
                    legalName: "Bio Pain Killers"
                    tradingName: "qwerty"
                    addressLine1: "30 Bukoto Street"
                    phoneNumber: "+2567099988"
                    website: "andela.com"
                    twitter: "andela@twitter.com"
                    instagram: "instragram.andela.com"
                    logo: "rtyuio/tyuio/rtyuhij"
                    facebook: "andela.facebook.com"
                ){{
                    business{{
                        id
                        legalName
                        tradingName
                        addressLine1
                        phoneNumber
                        businessEmail
                        instagram
                        website
                        twitter
                        facebook

                    }}
                    success

                }}
            }}
            ''')


def delete_business(business_id):
    return (f'''
                mutation{{
                    deleteBusiness(
                        id: \"{business_id}\"
                        ){{
                            success
                            }}
                        }}
                ''')
