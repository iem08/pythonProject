import numpy as np
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def funk():
    print("Введите ИНН")
    inn = input()

    kod_otdela = str(inn[0:4])

    conn = sqlite3.connect('D:/data/data')  # подключение к бд
    cursor = conn.cursor()

    cursor.execute('pragma table_info(data_2016)')  # Таблица со всеми показатклями (колонками)
    table_info = np.array(cursor.fetchall())
    column_name = table_info[::, 1]

    potential_years = ["2012", "2013", "2014", "2015", "2016", "2017", "2018"]  # все возможные года отчетов
    otceti = {}  # Словарь {год: {показатель: значение}}
    q = 0

    for year in potential_years:  # перебираем все табилцы с отчетами по годам в поисках строк с нужными ИНН
        cursor.execute(f'SELECT * FROM data_{year} where inn = {inn}')
        o = np.array(cursor.fetchall())
        if o.shape[0] == 1:  # Если получаем не пустой массив
            o = o[0]
            o = np.reshape(o, (266, 1))  # Переварачиваем его
            column_name = np.reshape(column_name, (266, 1))  # и переварачиваем массив с колонками
            o = np.hstack((column_name, o))  # и стакаем с массивом - показателями
            o = dict(o)  # делаем его словарем
            o = {year: o}  # и совмещаем с годом к которому он принадлежит
            otceti.update(
                o)  # полученый словарь добавляем в словарь словарей чтобы получился словарь вида {Год: {Показатель: Значение}}
        del year  # удаляем переменную чтобы в будущем не путать

    real_years = [*otceti]  # список годов, по которым есть отчеты
    last_year = real_years[-1]  # последий год по которому есть отчет (для не числовых показателей)

    type_ko = otceti[last_year]['type']

    if type_ko == 0:
        type_ko = "Социально ориентированная некоммерческая организация"
    elif type_ko == 1:
        type_ko = "Субъект малого предпринимательства и/или УСН"
    else:
        type_ko = "Коммерческая компания на ОСН"

    cursor.execute(f"SELECT Description FROM okved where Code like '{otceti[f'{real_years[0]}']['okved']}'")
    r_okved = np.array(cursor.fetchall())
    cursor.close()

    print(f"Название компании: {otceti[last_year]['name']}")
    # print(f"Код отдела ФНС: {kod_otdela}")
    # print(f"Тип: {type_ko}")
    print(f"ОКВЕД компании: {otceti[f'{last_year}']['okved']} ({r_okved[0, 0]})")

    ch_pribil_list = []
    viruchka_list = []
    valovaya_list = []

    for year_of_pokazatel in real_years:
        ch_pribil_list.append(int(otceti[year_of_pokazatel]['24003']))
        valovaya_list.append(int(otceti[year_of_pokazatel]['21003']))
        viruchka_list.append(int(otceti[year_of_pokazatel]['21103']))


    print('Выручка и прибыль:')
    osnov_df = pd.DataFrame(
        {'Выручка': viruchka_list, 'Валовая прибыль': valovaya_list, 'Чистая прибыль': ch_pribil_list},
        index=real_years)
    print(osnov_df)

    t_likvid_list = []
    b_likvid_list = []
    a_likvid_list = []

    for year_of_likvid in real_years:
        otceti[year_of_likvid]['12003'] = int(otceti[year_of_likvid]['12003'])
        otceti[year_of_likvid]['15103'] = int(otceti[year_of_likvid]['15103'])
        otceti[year_of_likvid]['15203'] = int(otceti[year_of_likvid]['15203'])
        otceti[year_of_likvid]['15503'] = int(otceti[year_of_likvid]['15503'])
        otceti[year_of_likvid]['12503'] = int(otceti[year_of_likvid]['12503'])
        otceti[year_of_likvid]['12303'] = int(otceti[year_of_likvid]['12303'])
        otceti[year_of_likvid]['12403'] = int(otceti[year_of_likvid]['12403'])

        t_likvid = round((otceti[year_of_likvid]['12003']) / (otceti[year_of_likvid]['15103'] + otceti[year_of_likvid]['15203'] + otceti[year_of_likvid]['15503']), 3)
        t_likvid_list.append(t_likvid)

        b_likvid = (otceti[year_of_likvid]['12303'] + otceti[year_of_likvid]['12403'] + otceti[year_of_likvid]['12503']) / (otceti[year_of_likvid]['15103'] + otceti[year_of_likvid]['15203'] + otceti[year_of_likvid]['15503'])
        b_likvid_list.append(round(b_likvid, 3))

        a_likvid = otceti[year_of_likvid]['12503'] / (otceti[year_of_likvid]['15203'] + otceti[year_of_likvid]['15103'])
        a_likvid_list.append(round(a_likvid, 3))

    likvid_df = pd.DataFrame({'Текущая ликвидность': t_likvid_list, 'Быстрая ликвидность': b_likvid_list,
                              'Абсолютная ликвидность': a_likvid_list}, index=real_years)
    print('Ликвидность')
    print(likvid_df)

    # структура доходов
    # сумма доходов = viruchka_list[х] + 23013 + 23203 + 23203

    # viruchka_list - обычные доходы от деятельности
    #23013 - доходы от участия в других организациях (дивиденды)
    #23203 - проценты по займам
    #23403 - прочие доходы

    struktura_dohodov_i_rashodov_list = []
    dividendi_list = []
    procenti_list = []
    prochie_dohodi_list = []

    for year_of_rashod in real_years:
        dividendi_list.append(int(otceti[year_of_rashod]['23103']))
        procenti_list.append(int(otceti[year_of_rashod]['23203']))
        prochie_dohodi_list.append(int(otceti[year_of_rashod]['23403']))
    dohodi_df = pd.DataFrame({'Выручка(Обычные доходы от деятельности)': viruchka_list,
                           'Дивиденды от участия в других компаниях': dividendi_list,
                           'Проценты по займам': procenti_list,
                           'Прочие доходы': prochie_dohodi_list}, index=real_years)
    print(dohodi_df)
    def graf():
        plt.plot(real_years, b_likvid_list, marker='x')
        plt.xlabel('Год', fontsize=15)
        plt.ylabel('Коэфициэнт быстрой ликвидности', fontsize=15)
        plt.title('Быстрая ликвидность по годам')
        plt.show()

        plt.plot(real_years, a_likvid_list, marker='x')
        plt.xlabel('Год', fontsize=15)
        plt.ylabel('Коэфициэнт абсолютной ликвидности', fontsize=15)
        plt.title('Абсолютная ликвидность по годам')
        plt.show()

        plt.plot(real_years, t_likvid_list, marker='x')
        plt.xlabel('Год', fontsize=15)
        plt.ylabel('Коэфициэнт текущей ликвидности', fontsize=15)
        plt.title('Текущая ликвидность по годам')
        plt.show()

        plt.plot(real_years, viruchka_list, marker='x')
        plt.xlabel('Год', fontsize=15)
        plt.ylabel('Выручка', fontsize=15)
        plt.title('Выручка по годам')
        plt.show()

        plt.plot(real_years, valovaya_list, marker='x')
        plt.xlabel('Год', fontsize=15)
        plt.ylabel('Валовая прибыль', fontsize=15)
        plt.title('Валовая прибыль по годам')
        plt.show()

        plt.plot(real_years, ch_pribil_list, marker='x')
        plt.xlabel('Год', fontsize=15)
        plt.ylabel('Чистая прибыль', fontsize=15)
        plt.title('Чистая прибыль по годам')
        plt.show()


    graf()

funk()

# try:
#     funk()
# except:
#     print('Попробуйте еще раз')
#     funk()