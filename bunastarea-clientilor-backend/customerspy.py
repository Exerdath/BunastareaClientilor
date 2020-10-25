#%%

import pandas as pd
import numpy as np

import matplotlib as plt
import seaborn as sns

import pickle

import datetime

from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_samples, silhouette_score, davies_bouldin_score, calinski_harabasz_score

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from sklearn import metrics

import plotly.graph_objects as go
import plotly.express as px
pd.set_option('display.max_rows', 100)

%config InlineBackend.figure_format = 'svg'

#%%

file = 'OnlineRetail.xlsx'

#%%

customers = pd.read_excel(file, sheet_name = 'onlineretail')
customers.head()

#%%

customers.info()

#%%

customers.dropna(inplace = True)

#%%

customers['CustomerID'] = customers['CustomerID'].astype('object')

#%%

customers.describe()

#%%

customers[customers['Quantity']<0]

#%%

customers = customers[customers['Quantity']>0]

#%%

import re

def abnormal_code(code):
    '''remove stockcodes or invoices that start with a letter'''
    pattern =  '^[a-zA-Z]'
    if re.search(pattern, str(code)):
        return(np.nan)
    else: return(code)

#%%

customers['StockCode'] = customers['StockCode'].apply(lambda x:abnormal_code(x))
customers['InvoiceNo'] = customers['InvoiceNo'].apply(lambda x:abnormal_code(x))
customers.dropna(inplace = True)

#%%

customers['StockCode_length'] = customers['StockCode'].apply(lambda x:len(str(x)))

#%%

customers.drop(columns = 'StockCode_length', inplace = True)

#%%

print(len(customers['InvoiceNo'].unique()))
print(len(customers['StockCode'].unique()))
print(len(customers['Description'].unique()))
#Unique StockCodes don't appear to tally with unique descriptions

print(len(customers['CustomerID'].unique()))
print(len(customers['Country'].unique()))

#%%

customers['Country'].value_counts()

#%%

customers.reset_index(drop = True, inplace = True)

#%%

customers['total_for_item'] = customers['UnitPrice']*customers['Quantity']

#%%

total_invoice_price = customers[['InvoiceNo','total_for_item']]

total_invoice_price = total_invoice_price.groupby(['InvoiceNo']).sum()

total_invoice_price.columns = ['invoice_price']

total_invoice_price


#%%

customers = customers.merge(total_invoice_price, on = 'InvoiceNo')

#%%

customer_orders = customers[['CustomerID','InvoiceDate','InvoiceNo']].drop_duplicates('InvoiceNo').sort_values(['CustomerID','InvoiceNo'])

#%%

customer_orders['time_diff'] = customer_orders.groupby(['CustomerID'])['InvoiceDate'].diff()
customer_orders.drop(columns = ['CustomerID','InvoiceDate'], inplace = True)

#%%

customer_orders.min()

#%%

customers = customers.merge(customer_orders, on = 'InvoiceNo')

#%%

total_invoice_quantity = customers[['InvoiceNo','Quantity']]
total_invoice_quantity = total_invoice_quantity.groupby(['InvoiceNo']).sum()
total_invoice_quantity.columns= ['total_quantity']

#%%


total_invoice_quantity

#%%

customers = customers.merge(total_invoice_quantity, on = 'InvoiceNo')

#%%

customer_profile = (customers[['CustomerID','InvoiceNo','invoice_price']]
                    .drop_duplicates(subset=['InvoiceNo'], keep='last'))

#%%

customer_profile =  pd.DataFrame(customer_profile.groupby(['CustomerID']).agg({'InvoiceNo':'count',
                                                                    'invoice_price':'sum'}))

#%%

customer_profile.reset_index(inplace = True)
customer_profile['CustomerID'] = customer_profile['CustomerID'].astype('object')

#%%

customer_profile

#%%

customers[customers['CustomerID']==18286].drop_duplicates(['InvoiceNo'])

#%%

customers['InvoiceDate'].max()

#%%

time_since_last_purchase = (customers[['CustomerID','InvoiceNo','InvoiceDate']]
                            .sort_values(['InvoiceDate'])
                            .drop_duplicates(subset=['CustomerID'], keep='last'))

#%%

date_today = datetime.datetime.strptime('2011-12-09 12:50:00','%Y-%m-%d %H:%M:%S')

#%%

time_since_last_purchase['last_purchase'] = (time_since_last_purchase['InvoiceDate']
                                             .apply(lambda x: date_today-x)
                                             .apply(lambda x:x.days))

#%%

customer_profile = customer_profile.merge(time_since_last_purchase[['CustomerID','last_purchase']], on='CustomerID')

#%%

customer_profile.columns = ['CustomerID','Frequency','Monetary Value','Recency']

#%%


X = customer_profile[['Frequency','Monetary Value','Recency']].copy()
scaler = StandardScaler()
X = scaler.fit_transform(X)

#%%

fig = px.scatter_3d(X, x=X[:,0], y=X[:,1], z=X[:,2])
fig.show()


#%%

X = customer_profile[['Frequency','Monetary Value','Recency']].copy()

def replace_outliers(x):
    if x>4 or x<-4:
        return np.nan
    else: return x

for column in X.columns:
    mean = X[column].mean()
    std = X[column].std()
    X[column] = (X[column]-mean)/std
    X[column] = X[column].apply(lambda x:replace_outliers(x))

X.dropna(inplace = True)

#%%

X = X.values

#%%

km = KMeans(n_clusters=5,random_state=77)
km.fit(X)
#%%


customer_profile[['Frequency_raw','Monetary Value_raw','Recency_raw']] = customer_profile[['Frequency','Monetary Value','Recency']].copy()

X = customer_profile[['Frequency','Monetary Value','Recency']].copy()

for column in X.columns:
    mean = customer_profile[column].mean()
    std = customer_profile[column].std()
    customer_profile[column] = (customer_profile[column]-mean)/std
    customer_profile[column] = customer_profile[column].apply(lambda x:replace_outliers(x))


customer_profile.dropna(inplace = True)

#%%
customer_profile['clusters'] = km.labels_


#%%

customer_profile
#%%

customer_profile.groupby('clusters').describe().transpose()
#%%

customer_profile.drop(columns=['Frequency','Monetary Value','Recency'], inplace = True)
#%%

customer_profile
#%%

customer_profile.columns=['CustomerID','Frequency','Monetary Value','Recency','Clusters']
#%%


fig = px.scatter_3d(customer_profile, x='Frequency',
                    y='Recency', z='Monetary Value',
                    color='Clusters', color_continuous_scale='sunset')
fig.show()
#%%

customer_profile
