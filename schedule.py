shevchenko_to_rialto_text = 'Т.Шевченка -> Риальто'
rialto_to_shevchenko_text = 'Риальто -> Т.Шевченка'

times = {
    'mon_thu': {
        '08:05': shevchenko_to_rialto_text,
        '08:20': shevchenko_to_rialto_text,
        '08:40': shevchenko_to_rialto_text,
        '08:50': shevchenko_to_rialto_text,
        '09:10': shevchenko_to_rialto_text,
        '09:35': shevchenko_to_rialto_text,
        '09:50': shevchenko_to_rialto_text,
        '10:15': shevchenko_to_rialto_text,
        '10:35': shevchenko_to_rialto_text,
        '10:50': shevchenko_to_rialto_text,
        '11:05': shevchenko_to_rialto_text,
        '17:40': rialto_to_shevchenko_text,
        '18:05': rialto_to_shevchenko_text,
        '18:10': rialto_to_shevchenko_text,
        '18:35': rialto_to_shevchenko_text,
        '18:45': rialto_to_shevchenko_text,
        '19:05': rialto_to_shevchenko_text,
        '19:30': rialto_to_shevchenko_text,
        '20:10': rialto_to_shevchenko_text,
        '20:30': rialto_to_shevchenko_text
    },
    'friday': {
        '08:05': shevchenko_to_rialto_text,
        '08:20': shevchenko_to_rialto_text,
        '08:40': shevchenko_to_rialto_text,
        '08:50': shevchenko_to_rialto_text,
        '09:10': shevchenko_to_rialto_text,
        '09:35': shevchenko_to_rialto_text,
        '09:50': shevchenko_to_rialto_text,
        '10:15': shevchenko_to_rialto_text,
        '10:35': shevchenko_to_rialto_text,
        '10:50': shevchenko_to_rialto_text,
        '11:05': shevchenko_to_rialto_text,
        '16:40': rialto_to_shevchenko_text,
        '16:55': rialto_to_shevchenko_text,
        '17:05': rialto_to_shevchenko_text,
        '17:20': rialto_to_shevchenko_text,
        '17:40': rialto_to_shevchenko_text,
        '18:10': rialto_to_shevchenko_text,
        '18:40': rialto_to_shevchenko_text,
        '19:10': rialto_to_shevchenko_text,
        '19:40': rialto_to_shevchenko_text,
        '20:10': rialto_to_shevchenko_text
    }
}

lunch = {
    'Риальто -> АльтаЦентрМолл': '13:30',
    'Риальто -> ТЦ Городок':  '13:30',
    'АльтаЦентрМолл -> Риальто':  '14:23',
    'ТЦ Городок -> Риальто': '14:20'
}

next_day_texts = {
    'mon_thu': 'В пятницу в {} утра 🤷‍'.format(list(times['friday'])[0]),
    'friday': 'В понедельник в {} утра 🤷‍'.format(list(times['mon_thu'])[0])
}