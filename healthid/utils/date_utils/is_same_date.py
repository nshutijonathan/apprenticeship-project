import datetime


def is_same_date(datetime1, datetime2):
    dt1 = datetime1 - datetime.timedelta(microseconds=datetime1.microsecond)
    dt2 = datetime2 - datetime.timedelta(microseconds=datetime2.microsecond)
    return dt1 == dt2
