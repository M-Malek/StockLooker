import requests

from matplotlib.figure import Figure


def stock_list_requester(user_input, api_k):
    url = "https://www.alphavantage.co/query"
    params={
        "function": "SYMBOL_SEARCH",
        "keywords": user_input,
        "apikey": api_k
    }
    request = requests.get(url, params=params)
    request.raise_for_status()
    company_list = request.json()
    result = {}
    # print(company_list)
    try:
        if company_list["Note"] != "":
            result = {"Error": "Wait 1 minute!"}
    except KeyError:
        for company in company_list['bestMatches']:
            # Return list of company's: name, symbol, currency
            if company['4. region'] == 'United States':
                name = company['2. name']
                symbol = company['1. symbol']
                currency = company['8. currency']
                result[name] = [symbol, currency]

    return result


def stock_requester(name, api_k):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": name,
        "interval": "1min",
        "apikey": api_k
    }
    request = requests.get(url, params=params)
    request.raise_for_status()
    data = request.json()
    try:
        meta_data = data["Meta Data"]
        stock_data = data["Time Series (1min)"]
    except KeyError:
        meta_data = data
        stock_data = data
    return meta_data, stock_data


class Stock:

    def __init__(self, company_name, api_key):
        self.name = company_name
        self.meta_data = None
        self.stock_data = None
        self.key = api_key

        self.meta_data, self.stock_data = stock_requester(self.name, self.key)

        self.avg_price_list = []
        self.date = []
        self.max_price = 0
        self.min_price = 0
        self.avg_price = 0
        self.main_data_manager()

    def main_data_manager(self):
        try:
            max_p = []
            min_p = []
            for date in self.stock_data:
                high = float(self.stock_data[date]['2. high'])
                low = float(self.stock_data[date]['3. low'])
                avg = abs((high + low) / 2)
                self.avg_price_list.append(avg)

                hour = date.split(" ")[1]
                self.date.append(hour)

                min_p.append(low)
                max_p.append(high)

            self.max_price = max(max_p)
            self.min_price = min(min_p)
            self.avg_price = sum(self.avg_price_list) / len(self.avg_price_list)
            self.avg_price_plotter()
        except TypeError:
            self.max_price = "No data"
            self.min_price = "No data"
            self.avg_price = "No data"

    def avg_price_plotter(self):
        fig = Figure()
        ax = fig.add_subplot()
        stock = ax.plot(self.date, self.avg_price_list)
        ax.xaxis.set_visible(False)
        ax.set_xlabel("Date [yyyy.mm.dd hh.mm.ss]")
        ax.set_ylabel("Price [$]")
        ax.grid()

        return fig
        # plt.plot(self.avg_price_list, self.date)
        # plt.title(f"Averange {self.name} stock price (last 6 hours)")
        # plt.grid()
        # plt.show()
