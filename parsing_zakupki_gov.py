import requests    # by Kirill Kasparov, 2023
from bs4 import BeautifulSoup
import pandas as pd
import time

# программа берет список ИНН из файла и проверяет наличие конкурсов на сайте zakupki.gov.

start = time.time()    # для таймера выполнения

head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
       ' Chrome/86.0.4240.185 YaBrowser/20.11.2.78 Yowser/2.5 Safari/537.36', 'accept': '*/*'}

inn_list_df = pd.read_csv('inn_list.csv', sep=';', encoding='windows-1251', dtype='unicode', nrows=1000)
inn_list = list(inn_list_df['ИНН'])

total_results_df = []
last_purchase = []
count = 0

for inn in inn_list:
    url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=' + str(inn) + '&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&ca=on&pc=on&pa=on&currencyIdGeneral=-1'
    r = requests.get(url, headers=head)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        total_results = soup.findAll('div', class_='search-results__total')
        for elem in total_results:
            total_results_df.append(elem.text.strip())
        data_value = soup.findAll('div', class_="data-block__value")
        if len(data_value) > 1:
            last_purchase.append(data_value[0].text.strip())
        else:
            last_purchase.append('нет')
    count += 1
    if count % 50 == 0:
        end = time.time()
        while True:  # проверка, если файл открыт
            try:
                inn_list_df.to_csv('inn_list_export.csv', sep=';', encoding='windows-1251', index=False, header=True,
                                   mode='a')
                print('Загружено строк:', count, "|  Время выполнения:", end-start, '|  Данные добавлены в файл inn_list_export.csv')
                break
            except IOError:  # PermissionError
                input('Необходимо закрыть файл inn_list.csv перед сохранением данных')


inn_list_df['Всего записей на zakupki.gov'] = total_results_df
inn_list_df['Последняя закупка'] = last_purchase


while True:  # проверка, если файл открыт
    try:
        inn_list_df.to_csv('inn_list_export.csv', sep=';', encoding='windows-1251', index=False, header=True)
        end = time.time()
        print('Загружено строк:', count, "|  Время выполнения:", end-start, '|  Итоговые данные сохранены в файл inn_list_export.csv')
        break
    except IOError:    # PermissionError
        input('Необходимо закрыть файл inn_list.csv перед сохранением данных')

