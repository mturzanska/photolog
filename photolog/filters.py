def _ordinalize(day):
    if day % 100 in range(11, 13):
        return 'th'
    else:
        day_mod = day % 10
        if day_mod == 1:
            return 'st'
        elif day_mod == 2:
            return 'nd'
        elif day_mod == 3:
            return 'rd'
        else:
            return 'th'


def jinja2_nice_datetime(date):
    day_suffix = _ordinalize(date.day)
    return date.strftime('%A, %B {0}{1} %Y'.format(date.day, day_suffix))
