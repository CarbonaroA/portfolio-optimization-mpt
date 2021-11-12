import requests
import pandas as pd
from datetime import datetime
from dateutil import relativedelta
import matplotlib.pyplot as plt

def scrape_data_from_morningstar(funds_dict, scrape_cumul_returns = True):
    userInput_metric = input(
        'Choose target metric:\n\t1. Price (NAV)\n\t2. Daily returns\n\t3. Cumulative returns\n\n -->: ')
    userDict_metric = {'1': 'price', '2': 'return', '3': 'cumulativereturn'}
    # For optimization, need to import daily returns only

    userInput = input(
        'Choose time window:\n\t1. 3 Month\n\t2. 6 Month\n\t3. 1 Year\n\t4. 3 Year\n\t5. 5 Year\n\t6. 10 Year\n\n -->: ')
    userDict = {'1': 3, '2': 6, '3': 12, '4': 36, '5': 60, '6': 120}

    n = datetime.now()
    n = n - relativedelta.relativedelta(days=1)
    n = n - relativedelta.relativedelta(months=userDict[userInput])
    dateStr = n.strftime('%Y-%m-%d')

    if scrape_cumul_returns and userDict_metric[userInput_metric]!='cumulativereturn':
        scrape_df(funds_dict=funds_dict, string_date=dateStr, metric='cumulativereturn').plot(
            x="date", y=list(funds_dict.keys()), kind="line")
        plt.title("Cumulative return")
        plt.show()

    data_df = scrape_df(funds_dict=funds_dict, string_date=dateStr, metric=userDict_metric[userInput_metric])

    return data_df, userDict_metric[userInput_metric]


def scrape_df(funds_dict, string_date, metric):
    url = f'https://tools.morningstar.co.uk/api/rest.svc/timeseries_{metric}/t92wz0sj7c'
    data = []

    for k, v in funds_dict.items():
        payload = {
            'currencyID': 'EUR',
            'idtype': 'Morningstar',
            'frequency': 'daily',
            'startDate': string_date,
            'performanceType': '',
            'outputType': 'COMPACTJSON',
            'id': v,
            'decPlaces': '8',
            'applyTrackRecordExtension': 'false'}

        temp_data = requests.get(url, params=payload).json()
        df = pd.DataFrame(temp_data)
        df['timestamp'] = pd.to_datetime(df[0], unit='ms')
        df['date'] = df['timestamp'].dt.date
        df = df[['date', 1]]
        df.columns = ['date', k]
        data.append(df)

    final_df = pd.concat(
        (iDF.set_index('date') for iDF in data),
        axis=1, join='inner'
    ).reset_index()

    return final_df

if __name__=="__main__":

    idDict = {
        #"JPM_D": "F000003WKM]2]0]FOITA$$ALL",
        #"JPM_HY": "F00000P2HD]2]0]FOITA$$ALL",
        #"JPM_CHI": "F00000J5HX]2]0]FOITA$$ALL",
        "JPM_USTech": "F000005MPD]2]0]FOITA$$ALL",
    }
    scrape_data_from_morningstar(funds_dict=idDict, scrape_cumul_returns=True)
    #pass