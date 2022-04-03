import tkinter
from news import news_looker
from stock import stock_list_requester, Stock

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


class GUI:

    def __init__(self):
        self.window = tkinter.Tk()
        self.plot = tkinter.Frame(self.window)
        self.news_frame = tkinter.LabelFrame(self.window)
        self.search_frame = tkinter.LabelFrame(self.window)
        self.stock_info_frame = tkinter.LabelFrame(self.window)
        self.window.title("Stock Locker v. 1.0")

        self.company_list = []
        self.news_list = []
        self.looker = None

        # API KEYS
        self.stock_key_label = tkinter.Label(self.window, text="Enter a stock API key:")
        self.stock_key_entry = tkinter.Entry()

        self.news_key_label = tkinter.Label(self.window, text="Enter a news API key:")
        self.news_key_entry = tkinter.Entry()

        # API KEYS POSITIONING
        self.stock_key_label.grid(row=2, column=0)
        self.stock_key_entry.grid(row=2, column=1)
        self.news_key_label.grid(row=3, column=0)
        self.news_key_entry.grid(row=3, column=1)

        # HELP BUTTON
        self.help_button = tkinter.Button(self.window, text="Help", width=50, command=self._help_button)
        self.help_button.grid(row=6, column=0, columnspan=2)

        # Stock Finder
        self.search_frame.grid(row=0, column=0, sticky='nsew')
        self.search_label = tkinter.Label(self.search_frame, text="Enter a stock name:")
        self.search_label.grid(row=1, column=0)

        self.all_company_list = tkinter.Listbox()
        self.company_name = tkinter.StringVar()
        self.company_name.trace_variable("w",
                                         lambda name, index, mode, sv=self.company_name: self._company_finder_mananger())

        self.search_entry = tkinter.Entry(self.search_frame, textvariable=self.company_name)
        self.search_entry.grid(row=1, column=1)

        self.company_listbox = tkinter.Listbox(self.search_frame, width=30, exportselection=False)
        self.company_listbox.grid(row=2, column=0, columnspan=3)
        self.company_listbox.bind("<<ListboxSelect>>", self._stock_plotter)

        # News frame
        self.news_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.news_listbox = tkinter.Listbox(self.news_frame, width=20, height=3, exportselection=False)
        self.news_listbox.grid(row=0, column=0)

        self.news_title = tkinter.Label(self.news_frame, text="Chosen news here!")
        self.news_title.grid(row=0, column=1, columnspan=2)

        self.news_url = tkinter.Label(self.news_frame, text="Waiting until you chose a company!")
        self.news_url.grid(row=0, column=3)

        self.news_listbox.bind("<<ListboxSelect>>", self._news_plotter)

        self.window.mainloop()

    def _company_finder_mananger(self):
        try:
            self.window.after_cancel(self.looker)
            self.looker = self.window.after(2000, self._company_finder)
        except ValueError:
            self.looker = self.window.after(2000, self._company_finder)

    def _company_finder(self):
        name = self.search_entry.get()
        if not self.stock_key_entry.get() == "":
            if not self.search_entry.get() == "":

                self.company_list = stock_list_requester(name, self.stock_key_entry.get())
                # print(company_list)

                company_names = list(self.company_list.keys())
                self.company_listbox.delete(0, tkinter.END)
                for name in company_names:
                    self.company_listbox.insert(tkinter.END, name)
            else:
                # Error - no company to search
                self._error_manager(5)
        else:
            # Error - API key required
            self._error_manager(0)

    def _stock_plotter(self, event):
        try:
            name = self.company_listbox.get((self.company_listbox.curselection()))
        except tkinter.TclError:
            name = 'Tesla'

        # print(name)
        # print(self.company_list)
        company = self.company_list[name][0]
        # print(self.company_list[name])
        # print(company)
        if not self.news_key_entry.get() == "":
            if not self.stock_key_entry.get() == "":
                if name == "Error":
                    self._error_manager(3)
                else:
                    # Prepare company data: stock and news
                    self.news_list = news_looker(name, self.news_key_entry.get())
                    company = Stock(company, self.stock_key_entry.get())

                    # Show company stock
                    plot = company.avg_price_plotter()
                    canvas = FigureCanvasTkAgg(plot, master=self.plot)
                    canvas.draw()

                    toolbar = NavigationToolbar2Tk(canvas, self.plot, pack_toolbar=False)
                    toolbar.update()

                    self.plot.grid(row=0, column=1)
                    canvas.get_tk_widget().grid(row=0, column=0)
                    toolbar.grid(row=1, column=0)

                    # Show company statistic
                    self._stock_info_plotter(company)

                    # Show news
                    self.news_listbox.delete(0, tkinter.END)
                    for new_news in list(self.news_list.keys()):
                        self.news_listbox.insert(tkinter.END, new_news)
            else:
                self._error_manager(0)
        else:
            self._error_manager(1)

    def _news_plotter(self, event):
        news = self.news_listbox.get((self.news_listbox.curselection()))
        self.news_title.config(text=self.news_list[news]['title'])
        self.news_url.config(text=self.news_list[news]['url'])

    def _stock_info_plotter(self, company):
        self.stock_info_frame.destroy()
        self.stock_info_frame = tkinter.LabelFrame(self.window)
        self.stock_info_frame.grid(row=0, column=2, sticky="ns")
        self.company_name_label = tkinter.Label(self.stock_info_frame, text=company.name)
        self.company_name_label.grid(row=0, column=0)

        self.stock_info = tkinter.Label(self.stock_info_frame, text="Last 6 hours information")
        self.stock_info.grid(row=1, column=0)

        self.max_stock_label = tkinter.Label(self.stock_info_frame, text="Maximum stock price in [$]:")
        self.max_stock_label.grid(row=2, column=0)

        self.max_stock_value = tkinter.Label(self.stock_info_frame, text=company.max_price)
        self.max_stock_value.grid(row=3, column=0)

        self.min_stock_label = tkinter.Label(self.stock_info_frame, text="Minimum stock price in [$]:")
        self.min_stock_label.grid(row=4, column=0)

        self.min_stock_value = tkinter.Label(self.stock_info_frame, text=company.min_price)
        self.min_stock_value.grid(row=5, column=0)

        self.average_stock_label = tkinter.Label(self.stock_info_frame, text="Average stock price in [$]:")
        self.average_stock_label.grid(row=6, column=0)

        self.average_stock_value = tkinter.Label(self.stock_info_frame, text=company.avg_price)
        self.average_stock_value.grid(row=7, column=0)

    def _error_manager(self, case):
        if case == 0:
            tkinter.messagebox.showwarning(title="No Stock API key",
                                           message="Please, enter your stock API Key.\nAPI key available here: \n"
                                                   "https://www.alphavantage.co/documentation/")
        elif case == 1:
            tkinter.messagebox.showwarning(title="No News API key",
                                           message="Please, enter your news API Key.\nAPI key available here: \n"
                                                   "https://newsapi.org/")
        elif case == 2:
            tkinter.messagebox.showwarning(title="No API Keys", message="Please enter API Keys first")

        elif case == 3:
            tkinter.messagebox.showwarning(title="Wait!", message="Wait one minute (Alphavantage delay time).")

        elif case == 4:
            tkinter.messagebox.showwarning(title="No company found!", message=
            "This company doesn't exist in our records")

        elif case == 5:
            tkinter.messagebox.showwarning(title="Enter a company name!", message="Please enter a company name!")

    def _help_button(self):
        tkinter.messagebox.showinfo(title="App info", message="Welcome to Stock Looker vol. 1.0 \n"
                                                              "Before use: please enter your API Keys\n"
                                                              "Stock API Key (Stock API by AlphaVantage)\n"
                                                              "https://www.alphavantage.co/documentation/\n"
                                                              "News API key (News API by NewsApi)\n"
                                                              "https://newsapi.org/\n"
                                                              "Created by Michal Malek, 2022")
