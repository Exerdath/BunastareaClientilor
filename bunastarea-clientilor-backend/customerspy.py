import pandas as pd
import numpy as np
import datetime
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.preprocessing import StandardScaler
import re
import copy
import pickle
import os.path
from os import path


class DataAnalysis:

    def __init__(self):
        pd.set_option('display.max_rows', 100)
        self.setup()
        self.customers = pickle.load(open('customers_final.pickle', 'rb'))
        self.customer_profile = pickle.load(open('customer_profile_final.pickle', 'rb'))

    def setup(self):
        file = 'OnlineRetail.xlsx'
        if not path.exists('customers.pickle'):
            customers = self.get_customers(file)
        else:
            customers = pickle.load(open('customers.pickle', 'rb'))

        if not path.exists('total_invoice_price.pickle'):
            total_invoice_price = self.get_total_invoice_price(customers)
        else:
            total_invoice_price = pickle.load(open('total_invoice_price.pickle', 'rb'))

        customers = customers.merge(total_invoice_price, on='InvoiceNo')
        customer_orders = customers[['CustomerID', 'InvoiceDate', 'InvoiceNo']].drop_duplicates(
            'InvoiceNo').sort_values(['CustomerID', 'InvoiceNo'])
        customer_orders['time_diff'] = customer_orders.groupby(['CustomerID'])['InvoiceDate'].diff()
        customer_orders.drop(columns=['CustomerID', 'InvoiceDate'], inplace=True)
        customers = customers.merge(customer_orders, on='InvoiceNo')

        if not path.exists('total_invoice_quantity.pickle'):
            total_invoice_quantity = self.get_total_invoice_quantity(customers)
        else:
            total_invoice_quantity = pickle.load(open('total_invoice_quantity.pickle', 'rb'))

        customers = customers.merge(total_invoice_quantity, on='InvoiceNo')

        if not path.exists('customer_profile.pickle'):
            customer_profile = self.get_customer_profile(customers)
        else:
            customer_profile = pickle.load(open('customer_profile.pickle', 'rb'))

        time_since_last_purchase = (customers[['CustomerID', 'InvoiceNo', 'InvoiceDate']]
                                    .sort_values(['InvoiceDate'])
                                    .drop_duplicates(subset=['CustomerID'], keep='last'))
        date_today = datetime.datetime.strptime('2011-12-09 12:50:00', '%Y-%m-%d %H:%M:%S')

        time_since_last_purchase['last_purchase'] = (time_since_last_purchase['InvoiceDate']
                                                     .apply(lambda x: date_today - x)
                                                     .apply(lambda x: x.days))
        customer_profile = customer_profile.merge(time_since_last_purchase[['CustomerID', 'last_purchase']],
                                                  on='CustomerID')

        customer_profile.columns = ['CustomerID', 'Frequency', 'Monetary Value', 'Recency']
        X = customer_profile[['Frequency', 'Monetary Value', 'Recency']].copy()
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        X = customer_profile[['Frequency', 'Monetary Value', 'Recency']].copy()
        for column in X.columns:
            mean = X[column].mean()
            std = X[column].std()
            X[column] = (X[column] - mean) / std
            X[column] = X[column].apply(lambda x: self.replace_outliers(x))
        X.dropna(inplace=True)
        X = X.values
        km = KMeans(n_clusters=5, random_state=77)
        km.fit(X)

        if not path.exists('process_customer_profile.pickle'):
            customer_profile = self.process_customer_profile(customer_profile, km)
        else:
            customer_profile = pickle.load(open('process_customer_profile.pickle', 'rb'))

        customer_id_cluster = customer_profile[['CustomerID', 'Clusters']]
        customers = customers.merge(customer_id_cluster, on='CustomerID', how='left')
        customers['time_diff'] = customers['time_diff'].apply(lambda x: x.days)

        if not path.exists('total_orders.pickle'):
            total_orders = self.get_total_orders(customers)
        else:
            total_orders = pickle.load(open('total_orders.pickle', 'rb'))

        customers = customers.merge(total_orders, on='CustomerID', how='left')
        pickle.dump(customers, open('customers_final.pickle', 'wb'))
        customer_profile = customer_profile.merge(total_orders, on='CustomerID', how='left')
        pickle.dump(customer_profile, open('customer_profile_final.pickle', 'wb'))

    def abnormal_code(self, code):
        pattern = '^[a-zA-Z]'
        if re.search(pattern, str(code)):
            return np.nan
        else:
            return code

    @staticmethod
    def replace_outliers(x):
        if x > 4 or x < -4:
            return np.nan
        else:
            return x

    @staticmethod
    def get_total_invoice_price(customers):
        total_invoice_price = customers[['InvoiceNo', 'total_for_item']]
        total_invoice_price = total_invoice_price.groupby(['InvoiceNo']).sum()
        total_invoice_price.columns = ['invoice_price']
        pickle.dump(total_invoice_price, open('total_invoice_price.pickle', 'wb'))
        return total_invoice_price

    def get_customers(self, file):
        customers = pd.read_excel(file, sheet_name='onlineretail')
        customers.dropna(inplace=True)
        customers['CustomerID'] = customers['CustomerID'].astype('object')
        customers = customers[customers['Quantity'] > 0]
        customers['StockCode'] = customers['StockCode'].apply(lambda x: self.abnormal_code(x))
        customers['InvoiceNo'] = customers['InvoiceNo'].apply(lambda x: self.abnormal_code(x))
        customers.dropna(inplace=True)
        customers['StockCode_length'] = customers['StockCode'].apply(lambda x: len(str(x)))
        customers.drop(columns='StockCode_length', inplace=True)
        customers.reset_index(drop=True, inplace=True)
        customers['total_for_item'] = customers['UnitPrice'] * customers['Quantity']
        pickle.dump(customers, open('customers.pickle', 'wb'))
        return customers

    @staticmethod
    def get_total_invoice_quantity(customers):
        total_invoice_quantity = customers[['InvoiceNo', 'Quantity']]
        total_invoice_quantity = total_invoice_quantity.groupby(['InvoiceNo']).sum()
        total_invoice_quantity.columns = ['total_quantity']
        pickle.dump(total_invoice_quantity, open('total_invoice_quantity.pickle', 'wb'))
        return total_invoice_quantity

    @staticmethod
    def get_customer_profile(customers):
        customer_profile = (customers[['CustomerID', 'InvoiceNo', 'invoice_price']]
                            .drop_duplicates(subset=['InvoiceNo'], keep='last'))
        customer_profile = pd.DataFrame(customer_profile.groupby(['CustomerID']).agg({'InvoiceNo': 'count',
                                                                                      'invoice_price': 'sum'}))
        customer_profile.reset_index(inplace=True)
        customer_profile['CustomerID'] = customer_profile['CustomerID'].astype('object')
        pickle.dump(customer_profile, open('customer_profile.pickle', 'wb'))
        return customer_profile

    def process_customer_profile(self, customer_profile, km):
        customer_profile[['Frequency_raw', 'Monetary Value_raw', 'Recency_raw']] = customer_profile[
            ['Frequency', 'Monetary Value', 'Recency']].copy()
        X = customer_profile[['Frequency', 'Monetary Value', 'Recency']].copy()
        for column in X.columns:
            mean = customer_profile[column].mean()
            std = customer_profile[column].std()
            customer_profile[column] = (customer_profile[column] - mean) / std
            customer_profile[column] = customer_profile[column].apply(lambda x: self.replace_outliers(x))
        customer_profile.dropna(inplace=True)
        customer_profile['clusters'] = km.labels_
        customer_profile.groupby('clusters').describe().transpose()
        customer_profile.drop(columns=['Frequency', 'Monetary Value', 'Recency'], inplace=True)
        customer_profile.columns = ['CustomerID', 'Frequency', 'Monetary Value', 'Recency', 'Clusters']
        pickle.dump(customer_profile, open('process_customer_profile.pickle', 'wb'))

        return customer_profile

    @staticmethod
    def get_total_orders(customers):
        total_orders = customers.drop_duplicates(['InvoiceNo']).groupby(['CustomerID'])['InvoiceNo'].count()
        total_orders = pd.DataFrame(total_orders)
        total_orders.columns = ['total_orders']
        pickle.dump(total_orders, open('total_orders.pickle', 'wb'))
        return total_orders

    def get_top_5_buying_customers(self):
        buyers = self.customer_profile.sort_values(by=['total_orders'], ascending=False).iloc[:5]
        top_buyers = []
        for index, row in buyers.iterrows():
            buyer = {
                "CustomerID": row["CustomerID"],
                "Frequency": row["Frequency"],
                "MonetaryValue": float("{:.2f}".format(row["Monetary Value"])),
                "Recency": row["Recency"],
                "Clusters": row["Clusters"],
                "TotalOrders": row["total_orders"],
            }
            top_buyers.append(buyer)
        return top_buyers

    def avg_invoice_spent_top_5_customers(self):
        customer_profile_avg = copy.deepcopy(self.customer_profile)
        customer_profile_avg['avg_spend'] = self.customer_profile['Monetary Value']/self.customer_profile['total_orders']
        customers_avg = customer_profile_avg.sort_values(by=['avg_spend'], ascending=False).iloc[:5]
        customers_avg_list = []
        for index, row in customers_avg.iterrows():
            avg_cutomser = {
                "CustomerID": row["CustomerID"],
                "Frequency": row["Frequency"],
                "MonetaryValue": float("{:.2f}".format(row["Monetary Value"])),
                "Recency": row["Recency"],
                "Clusters": row["Clusters"],
                "TotalOrders": row["total_orders"],
                "AvgSpend": float("{:.2f}".format(row["avg_spend"])),
            }
            customers_avg_list.append(avg_cutomser)
        return customers_avg_list

    def avg_spent_per_invoice_by_id(self, customer_id):
        customer_profile_avg = copy.deepcopy(self.customer_profile)
        customer_profile_avg['avg_spend'] = self.customer_profile['Monetary Value'] / self.customer_profile['total_orders']
        avg_by_user = customer_profile_avg.loc[customer_profile_avg['CustomerID'] == customer_id]
        avg_spent_list = []
        for index, row in avg_by_user.iterrows():
            avg_spent = {
                "CustomerID": row["CustomerID"],
                "Frequency": row["Frequency"],
                "MonetaryValue": row["Monetary Value"],
                "Recency": row["Recency"],
                "Clusters": row["Clusters"],
                "TotalOrders": row["total_orders"],
                "AvgSpend": float("{:.2f}".format(row["avg_spend"])),
            }
            avg_spent_list.append(avg_spent)
        return avg_spent_list

    def last_invoices_by_id(self, customer_id):
        last_invoices = self.customers.sort_values(by=['InvoiceDate'], ascending = False).drop_duplicates(['InvoiceNo']).loc[self.customers['CustomerID'] == customer_id].iloc[:5]
        top_last_invoices = []
        for index, row in last_invoices.iterrows():
            product = {
                "CustomerID": row["CustomerID"],
                "InvoiceNo": row["InvoiceNo"],
                "StockCode": row["StockCode"],
                "Description": row["Description"],
                "Quantity": row["Quantity"],
                "InvoiceDate": str(row["InvoiceDate"]),
                "UnitPrice": row["UnitPrice"],
                "Country": row["Country"],
                "TotalForinvoice": float("{:.2f}".format(row["total_for_item"])),
                "InvoicePrice": float("{:.2f}".format(row["invoice_price"])),
                "TimeDiff": row["time_diff"],
                "TotalQuantity": row["total_quantity"],
                "Clusters": row["Clusters"],
                "TotalOrders": row["total_orders"],
            }
            top_last_invoices.append(product)
        return top_last_invoices

    def get_suggestions(self, customer_id):
        customer_cluster = self.customer_profile.loc[self.customer_profile['CustomerID'] == customer_id]['Clusters'].iloc[0]
        customer_monetary_value = self.customer_profile.loc[self.customer_profile['CustomerID'] == customer_id]['Monetary Value'].iloc[0]
        top_ten_cluster_users = self.customer_profile.loc[self.customer_profile['Clusters'] == customer_cluster].loc[abs(self.customer_profile['Monetary Value'] - customer_monetary_value) < 100].iloc[:10].values.tolist()
        products_list = []
        for customer in top_ten_cluster_users:
            customer_in_customers = self.customers.sort_values(by=['InvoiceDate'], ascending=False).loc[self.customers['CustomerID'] == customer[0]].iloc[0]
            product_name = customer_in_customers['Description']
            product_stock_code = customer_in_customers['StockCode']
            product_price = customer_in_customers['UnitPrice']
            product= {
                "product_name": str(product_name),
                "product_stock_code": str(product_stock_code),
                "product_price": str(product_price)
            }
            products_list.append(product)
        return products_list

    def get_new_customer_id(self, last_customer_id):
        new_customer_id_data_frame = self.customer_profile.sort_values(by=['CustomerID'], ascending=True).loc[self.customer_profile['CustomerID'] > last_customer_id].iloc[0]
        return new_customer_id_data_frame['CustomerID']
