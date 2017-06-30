def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
import operator

class WeekDaysChoices:
    _weekdays = [ 2**x for x in range(0,7)]
    @classmethod
    def days_from_int(self, val):
        return [self._weekdays.index(i) for i in self._weekdays if i & val]
    @classmethod
    def int_from_days(self, days):
        return reduce(operator.add,[self._weekdays[i] for i in days])