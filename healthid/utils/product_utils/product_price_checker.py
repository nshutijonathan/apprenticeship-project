
def round_off_selling_price(val):

    price = float(val) + 0.001
    selling_price = round(price, -1)

    return int(selling_price)
