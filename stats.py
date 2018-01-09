import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_graphviz
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib
import geocoder
from sklearn.cluster import KMeans
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import datetime





clf = joblib.load('randomforest.pkl')
kmeans = joblib.load('kmeans.pkl')
df = pd.read_pickle('rentals.pkl')


clean_df = df.drop(['building_id','created','district','description','display_address','features','listing_id',
              'manager_id','date_created','photos','street_address'],axis=1)
X = clean_df.drop(['interest_level'],axis=1)
y = clean_df['interest_level']

min_max_scaler = MinMaxScaler()
np_scaled = pd.DataFrame(min_max_scaler.fit_transform(X), columns=X.columns, index=X.index)
X = pd.DataFrame(np_scaled)

# ['bathrooms', 'bedrooms', 'latitude', 'longitude', 'price', 'cats',
#        'dogs', 'hardwood', 'prewar', 'terrace', 'patio', 'parking', 'roof',
#        'num_owner_locations', 'num_listings_building', 'num_photos',
#        'num_features', 'description_len', 'age', 'cluster__0', 'cluster__1',
#        'cluster__10', 'cluster__11', 'cluster__12', 'cluster__13',
#        'cluster__14', 'cluster__15', 'cluster__16', 'cluster__17',
#        'cluster__18', 'cluster__19', 'cluster__2', 'cluster__3', 'cluster__4',
#        'cluster__5', 'cluster__6', 'cluster__7', 'cluster__8', 'cluster__9',
#        'in_manhattan', 'price_per_bathroom', 'price_per_bedroom']


# address = StringField('Location Address')
# features = StringField('List of features separated by commas',)
# manager_id = StringField('Manager id (leave blank if uknown)')
# building_id = StringField('building id (leave blank if uknown)')
# photos = StringField('URLs to photos separated by commas')
# description = StringField('Description of listing')
# bathrooms = StringField('Number of bathrooms')
# bedrooms = StringField('Number of bedrooms')
# price = StringField('Price')
# created = datetime.date
# submit = SubmitField('Submit')

def findKeyWord(keyword,features):
    for word in features.split():
        if keyword in word:
            return 1
    return 0


def predicter(address, features, manager_id, building_id, photos,description, bathrooms, bedrooms, price):
    # ['bathrooms', 'bedrooms', 'latitude', 'longitude', 'price', 'cats',
#        'dogs', 'hardwood', 'prewar', 'terrace', 'patio', 'parking', 'roof',
#        'num_owner_locations', 'num_listings_building', 'num_photos',
#        'num_features', 'description_len', 'age', 'cluster__0', 'cluster__1',
#        'cluster__10', 'cluster__11', 'cluster__12', 'cluster__13',
#        'cluster__14', 'cluster__15', 'cluster__16', 'cluster__17',
#        'cluster__18', 'cluster__19', 'cluster__2', 'cluster__3', 'cluster__4',
#        'cluster__5', 'cluster__6', 'cluster__7', 'cluster__8', 'cluster__9',
#        'in_manhattan', 'price_per_bathroom', 'price_per_bedroom']
    data = pd.Series()
    data['bathrooms'] = bathrooms
    data['bedrooms'] = bedrooms
    g = geocoder.arcgis(address)

    data['latitude'] = g.json['lat']
    data['longitude'] = g.json['lng']

    data['price'] = price

    data['cats'] = findKeyWord(keyword='cat',features=features)
    data['dogs'] = findKeyWord(keyword='dog',features=features)
    data['hardwood'] = findKeyWord(keyword='hardwood',features=features)
    data['prewar'] = findKeyWord(keyword='prewar',features=features)
    data['terrace'] = findKeyWord(keyword='terrace',features=features)
    data['patio'] = findKeyWord(keyword='patio',features=features)
    data['parking'] = findKeyWord(keyword='parking',features=features)
    data['roof'] = findKeyWord(keyword='roof',features=features)

    df['num_owner_locations'] = [manager_popularity[x]
                       if x in manager_popularity
                       else 1
                       for x in df['manager_id']]
    if manager_id in df.manager_id.value_counts():
        data['num_owner_locations'] = df.manager_id.value_counts()[manager_id]
    else:
        data['num_owner_locations'] = 0
    
    if building_id in df.building_id.value_counts():
        data['num_listings_building'] = df.building_id.value_counts()[building_id]
    else:
        data['num_listings_building'] = 0
    
    data['num_photos'] = len(photos)

    #        'num_features',
    data['num_features'] = len(features.split()) 
    # 'description_len', 
    data['description_len'] = len(description)

    # 'age', 
    earliest = max(df['date_created'])
    data['age'] = int((earliest-datetime.datetime.now()).days)

    # 'cluster__0', 
    district = kmeans.predict(data['longitude','latitude'])[0]
    for i in range(0,20):
        word = "cluster_"+str(i)
        if i == district:
            data[word] = 1
        else:
            data[word] = 0

    #'in_manhattan', 
    nw = (40.883982, -73.932266)
    sw =  (40.706982, -74.032860)
    se = (40.695009, -73.981361)
    ne = (40.800089, -73.913040)
    tip = (40.699434, -74.025650)
    tip2 = (40.699174, -74.006081)
    tip3 = (40.708804, -73.977585)
    tip4 = (40.732482, -73.965569)
    tip5 = (40.748090, -73.959732)
    tip6 = (40.777215, -73.937416)
    tip7 = (40.801648, -73.925057)
    tip8= (40.873598, -73.904800)
    manhattan = Polygon([nw, sw, tip, tip2, tip3, tip4, tip5, tip6, tip7, tip8])
    p = Point(data['latitutde'],data['longitude'])
    if manhattan.contains(Point(x)):
        data['in_manhattan'] = 1
    else:
        data['in_manhattan'] = 0

    # 'price_per_bathroom', 
    data['price_per_bathroom'] = price/bathrooms
    # 'price_per_bedroom']
    data['price_per_bedroom'] = price/bedrooms

    #minmaxscale
    min_max_scaler = MinMaxScaler()
    np_scaled = pd.DataFrame(min_max_scaler.fit_transform(data), columns=data.columns, index=data.index)
    data = pd.DataFrame(np_scaled)

    return data







def printer():
    print(clf.predict(X[0:20]))
    return(y[0:20])