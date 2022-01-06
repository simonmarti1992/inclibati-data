def PieAndHist(adresse, entryData):
    import json
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.set(font_scale = 1.5)
    sns.set_style("ticks")
    osm = './0-urbain-actual/{}_urb/rsu_lcz.geojson'.format(adresse)
    with open(osm) as f:
      myGeoJsonClimate = json.load(f)
    listID = []
    listLCZ = []
    for data in myGeoJsonClimate['features']:
        listID.append(data['properties']['ID_RSU'])
        listLCZ.append(data['properties']['LCZ_PRIMARY'])
    dlcz = pd.DataFrame()
    dlcz['ID'] = listID
    dlcz['param'] = listLCZ
    dlcz.index = listID
    osm = './0-urbain-actual/{}_urb/rsu_indicators.geojson'.format(adresse)
    with open(osm) as f:
      myGeoJsonClimate = json.load(f)
    listID = []
    listAREA = []
    for data in myGeoJsonClimate['features']:
        listID.append(data['properties']['ID_RSU'])
        listAREA.append(data['properties']['AREA'])
    drsu = pd.DataFrame()
    drsu['IDrsu'] = listID
    drsu['area'] = listAREA
    drsu.index = listID
    tableCorresp = {   
        1 :['LCZ 1: Compact high-rise', '#8b0101'],
        2 :['LCZ 2: Compact mid-rise', '#cc0200'],
        3 :['LCZ 3: Compact low-rise', '#fc0001'],
        4 :['LCZ 4: Open high-rise', '#be4c03'],
        5 :['LCZ 5: Open mid-rise', '#ff6602'],
        6 :['LCZ 6: Open low-rise', '#ff9856'],
        7 :['LCZ 7: Lightweight low-rise', '#fbed08'],
        8 :['LCZ 8: Large low-rise', '#bcbcba'],
        9 :['LCZ 9: Sparsely built', '#ffcca7'],
        10 :['LCZ 10: Heavy industry', '#57555a'],
        101 :['LCZ A: Dense trees', '#006700'],
        102 :['LCZ B: Scattered trees', '#05aa05'],
        103 :['LCZ C: Bush,scrub', '#648423'],
        104 :['LCZ D: Low plants', '#bbdb7a'],
        105 :['LCZ E: Bare rock or paved', '#010101'],
        106 :['LCZ F: Bare soil or sand', '#fdf6ae'],
        107 :['LCZ G: Water', '#6d67fd']
    }
    concat = pd.concat([dlcz, drsu], axis=1, join="inner")
    dataBilan = pd.pivot_table(concat, values='area', index=['param'], aggfunc=np.sum)/concat['area'].sum()
    dataBilan['c'] = [tableCorresp[x][1] for x in dataBilan.index]
    dataBilan['name'] = [tableCorresp[x][0] for x in dataBilan.index]
    explode = [0.05 for x in dataBilan['area']]

    fig, (ax0, ax1) = plt.subplots(1,2, figsize = (15,10))
    # les plots
    ax0.pie(dataBilan['area'], explode=explode, labels=dataBilan['name'], autopct='%1.1f%%',
            shadow=False, startangle=90, colors=dataBilan['c'],wedgeprops={'alpha':0.8}, textprops={'fontsize': 15})
    ax1.bar(entryData[adresse]['urb'].keys(), entryData[adresse]['urb'].values(), color='g')
    # ax1.set_ylim([0, 1])
    ax1.set_title('{}\nHmoy = {} m'.format(adresse, entryData[adresse]['height']))

    plt.setp(ax1.get_xticklabels(), rotation=45, horizontalalignment='right')
    fig.tight_layout()
    
def HeatMapPlot(adresse):
    import os
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    import epw_columns
    import pandas as pd
    import glob
    files = glob.glob(os.getcwd()+'/0-urbain-actual/{}_urb/*.epw'.format(adresse))
    initPath = files[0]
    uwgPath = files[1]
    epw_columns = epw_columns.get()
    data = {}
    for run, path in zip(['ref', 'uwg'], [initPath, uwgPath]):
        data[run] = pd.read_csv(path, header=None, skiprows=8, names=epw_columns, index_col=False)
        data[run].index = pd.date_range(start='2020-01-01', end='2020-12-30 23:00:00', freq='1h')
    '''
    ===
    COMPARE les températures ambiantes
    ===
    '''
    # Le type de toit
    VALUE = 'Dry Bulb Temperature' # chambres, TOP_Appt_sud_R2, 'TOP_entree'
    myData = pd.DataFrame()
    myData[VALUE] = data['uwg'][VALUE] - data['ref'][VALUE]
    myData.index= data['ref'].index
    myData['hours'] = myData.index.hour
    myData['days'] = myData.index.date
    # STYLES (font size, etc...)
    sns.set(font_scale = 1.5)
    sns.set_style("ticks")
    # style options: 'darkgrid', 'whitegrid', 'white', 'dark', 'ticks'
    # context options: 'paper', 'notebook', 'talk', 'poster'
    cmap = plt.cm.coolwarm
    piv = pd.pivot_table(myData, values=VALUE, index=["hours"], columns=["days"])
    pmin_max = pd.pivot_table(myData, values=VALUE, index=["days"], aggfunc= [min, max]) # get min and max values for each day
    ## To plot heatmap of a single column
    label = u'$\Delta$T [°C]'
    f, (ax0, ax) = plt.subplots(2,1, figsize=(15, 10), gridspec_kw = {'height_ratios':[1, 3], 'hspace':0.1})
    # ax0.autoscale(enable=True, axis='x', tight=True)
    ax0.get_xaxis().set_visible(False)
    df = pd.DataFrame()
    df['zero'] = [0 for x in pmin_max.index]
    df.index = pmin_max.index
    df['zero'].plot(ax = ax0, linestyle = '--', color = 'k')
    # joli démarcation....
    #-------------------------------------------------------------------
    ax0.fill_between(pmin_max.index, pmin_max['min',VALUE], df['zero'],
                     where= pmin_max['min',VALUE] >= df['zero'],
                     edgecolor='k', facecolor = 'red', alpha = 0.5,
                     label = label)
    ax0.fill_between(pmin_max.index, pmin_max['min',VALUE], df['zero'],
                     where=  df['zero']>= pmin_max['min',VALUE],
                     edgecolor='k', facecolor = 'darkblue', alpha = 0.5,
                     label = label)
    ax0.fill_between(pmin_max.index, df['zero'], pmin_max['max',VALUE],
                     where=  pmin_max['max',VALUE]>= df['zero'],
                     edgecolor='k', facecolor = 'red', alpha = 0.5,
                     label = label)
    ax0.fill_between(pmin_max.index, df['zero'], pmin_max['max',VALUE],
                     where=  df['zero']>= pmin_max['max',VALUE],
                     edgecolor='k', facecolor = 'darkblue', alpha = 0.5,
                     label = label)
    #-------------------------------------------------------------------
    sns.heatmap(piv, vmin = piv.min().min(), vmax = piv.max().max(), center = 0, xticklabels = 30, yticklabels = 6,
                ax = ax, cmap = cmap,
                cbar_ax = f.add_axes([.91,.19,.015,.5]),
                cbar_kws = {'use_gridspec': True, 'label': label})
    ax.invert_yaxis()
    # ax0.legend(loc = 'lower center')

    ax0.set_title(adresse)
    # ax0.set_title(u'$\mathrm{\ %s_{min, max}}$'%VALUE)
    ax0.set_ylabel(u'$\Delta$T [°C]')
    ax.autoscale(enable=True, axis='x', tight=True)
    plt.subplots_adjust(bottom=0.2)
    plt.show()
    return files[0], files[1]


def foliumMap(adresse):
    import numpy as np
    import json
    from geopy.geocoders import Nominatim
    import branca.colormap as cmp
    import pandas as pd
    from shapely.geometry import Polygon
    geolocator = Nominatim(user_agent="my_user_agent")
    country = "France"
    osm = './0-urbain-actual/{}_urb/rsu_lcz.geojson'.format(adresse)
    with open(osm) as f:
        myGeoJsonClimate = json.load(f)


    '''
    ===
    Construction du dataframe
    ===
    '''

    dgeo = pd.DataFrame()
    maListe = []
    for data in myGeoJsonClimate['features']:
        records = []
        for x in data['properties'].keys():
            records.append(data['properties'][x])
        maListe.append(records)
    dgeo = pd.DataFrame.from_records(maListe)
    dgeo.columns = list(data['properties'].keys())
    tableCorresp = {
        1 :['LCZ 1: Compact high-rise', '#8b0101'],
        2 :['LCZ 2: Compact mid-rise', '#cc0200'],
        3 :['LCZ 3: Compact low-rise', '#fc0001'],
        4 :['LCZ 4: Open high-rise', '#be4c03'],
        5 :['LCZ 5: Open mid-rise', '#ff6602'],
        6 :['LCZ 6: Open low-rise', '#ff9856'],
        7 :['LCZ 7: Lightweight low-rise', '#fbed08'],
        8 :['LCZ 8: Large low-rise', '#bcbcba'],
        9 :['LCZ 9: Sparsely built', '#ffcca7'],
        10 :['LCZ 10: Heavy industry', '#57555a'],
        11 :['LCZ A: Dense trees', '#006700'],
        12 :['LCZ B: Scattered trees', '#05aa05'],
        13 :['LCZ C: Bush,scrub', '#648423'],
        14 :['LCZ D: Low plants', '#bbdb7a'],
        15 :['LCZ E: Bare rock or paved', '#010101'],
        16 :['LCZ F: Bare soil or sand', '#fdf6ae'],
        17 :['LCZ G: Water', '#6d67fd']
    }
    step = cmp.StepColormap(
     [tableCorresp[k][1] for k in tableCorresp.keys()],
     vmin=0, vmax=18,
     index=tableCorresp.keys(),  #for change in the colors, not used fr linear
     caption='Color Scale for Map'    #Caption for Color scale or Legend
    )
    '''
    ===
    Modif du .geojson
    ===
    '''
    for k, item in enumerate(myGeoJsonClimate['features']):
        try:myGeoJsonClimate['features'][k]['properties']['legend'] = tableCorresp[myGeoJsonClimate['features'][k]['properties']['LCZ_PRIMARY']][0]
        except:myGeoJsonClimate['features'][k]['properties']['legend'] = tableCorresp[int(str(myGeoJsonClimate['features'][k]['properties']['LCZ_PRIMARY']).replace('0',''))][0]


    for x in myGeoJsonClimate['features']:
        if x['properties']['LCZ_PRIMARY'] in [101, 102, 103, 104, 105, 106, 107]:
            x['LCZ_PRIMARY'] = int(str(x['properties']['LCZ_PRIMARY']).replace('0',''))
        else:
            x['LCZ_PRIMARY'] = x['properties']['LCZ_PRIMARY']

    '''
    ===
    Tracé de la carte
    ===
    '''
    import branca.colormap as cm

    # loc = geolocator.geocode('8 Rue Isabelle Autissier, 17140 Lagord')
    if "20 Rue Four de la Terre" in adresse:
        adresse = '10 rue Amphoux, 84000 Avignon'
    else:pass
    if "2 Rue Général Foy" in adresse:
        adresse = '1 rue Michel Rondet, 42000 Saint-Étienne'
    else:pass
    if "George V" in adresse:
        adresse = '16 avenue Paul Dufourmantel, 06000 Nice'
    else:pass
    if "Mabille" in adresse:
        adresse = '1 Rue Eugène Quinton, 35200 Rennes'
    else:pass
    if "Amigas" in adresse:
        adresse = '13 Av. Emile Barla, 83000 Toulon'
    else:pass
    
    loc = geolocator.geocode(adresse)
    lat = loc.latitude
    long = loc.longitude
    import folium

    fig = folium.Figure(width=600, height = 600)
    map_osm = folium.Map(location=[loc.latitude, loc.longitude],
        zoom_start=12, tiles="stamentoner")
    folium.GeoJson(
        myGeoJsonClimate,
        style_function=lambda feature: {
            'fillColor': step(feature['LCZ_PRIMARY']),
            'color': 'black',
            'weight': 1,
            'alpha': 1,
            "fillOpacity": 0.35},
        #         'dashArray' : '5, 5'
        tooltip=folium.features.GeoJsonTooltip(
            fields=['legend'],
            aliases=['LCN n°:'],
        )

    ).add_to(map_osm)

    colormap = step
    colormap.caption = "LCZ map"
    map_osm.add_child(colormap)

    fig.add_child(map_osm)
    return map_osm, myGeoJsonClimate, tableCorresp
    
    
    
def indicatorCalculation(adresse):
    import os
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    import epw_columns
    import pandas as pd
    import glob
    files = glob.glob(os.getcwd()+'/0-urbain-actual/{}_urb/*.epw'.format(adresse))
    initPath = files[0]
    uwgPath = files[1]
    epw_columns = epw_columns.get()
    data = {}
    for run, path in zip(['ref', 'uwg'], [initPath, uwgPath]):
        data[run] = pd.read_csv(path, header=None, skiprows=8, names=epw_columns, index_col=False)
        data[run].index = pd.date_range(start='2020-01-01', end='2020-12-30 23:00:00', freq='1h')
    '''
    ===
    COMPARE les températures ambiantes
    ===
    '''
    # Le type de toit
    VALUE = 'Dry Bulb Temperature' # chambres, TOP_Appt_sud_R2, 'TOP_entree'
    myData = pd.DataFrame()
    myData[VALUE] = data['uwg'][VALUE] - data['ref'][VALUE]
    myData.index= data['ref'].index
    myData['hours'] = myData.index.hour
    myData['days'] = myData.index.date
    # STYLES (font size, etc...)
    sns.set(font_scale = 1.5)
    sns.set_style("ticks")
    # style options: 'darkgrid', 'whitegrid', 'white', 'dark', 'ticks'
    # context options: 'paper', 'notebook', 'talk', 'poster'
    cmap = plt.cm.coolwarm
    piv = pd.pivot_table(myData, values=VALUE, index=["hours"], columns=["days"])
    pmin_max = pd.pivot_table(myData, values=VALUE, index=["days"], aggfunc= [min, max]) # get min and max values for each day
    ## To plot heatmap of a single column
    # label = u'$\Delta$T [°C]'
    # f, (ax0, ax) = plt.subplots(2,1, figsize=(15, 10), gridspec_kw = {'height_ratios':[1, 3], 'hspace':0.1})
    # # ax0.autoscale(enable=True, axis='x', tight=True)
    # ax0.get_xaxis().set_visible(False)
    # df = pd.DataFrame()
    # df['zero'] = [0 for x in pmin_max.index]
    # df.index = pmin_max.index
    # df['zero'].plot(ax = ax0, linestyle = '--', color = 'k')
    # # joli démarcation....
    # #-------------------------------------------------------------------
    # ax0.fill_between(pmin_max.index, pmin_max['min',VALUE], df['zero'],
                     # where= pmin_max['min',VALUE] >= df['zero'],
                     # edgecolor='k', facecolor = 'red', alpha = 0.5,
                     # label = label)
    # ax0.fill_between(pmin_max.index, pmin_max['min',VALUE], df['zero'],
                     # where=  df['zero']>= pmin_max['min',VALUE],
                     # edgecolor='k', facecolor = 'darkblue', alpha = 0.5,
                     # label = label)
    # ax0.fill_between(pmin_max.index, df['zero'], pmin_max['max',VALUE],
                     # where=  pmin_max['max',VALUE]>= df['zero'],
                     # edgecolor='k', facecolor = 'red', alpha = 0.5,
                     # label = label)
    # ax0.fill_between(pmin_max.index, df['zero'], pmin_max['max',VALUE],
                     # where=  df['zero']>= pmin_max['max',VALUE],
                     # edgecolor='k', facecolor = 'darkblue', alpha = 0.5,
                     # label = label)
    # #-------------------------------------------------------------------
    # sns.heatmap(piv, vmin = piv.min().min(), vmax = piv.max().max(), center = 0, xticklabels = 30, yticklabels = 6,
                # ax = ax, cmap = cmap,
                # cbar_ax = f.add_axes([.91,.19,.015,.5]),
                # cbar_kws = {'use_gridspec': True, 'label': label})
    # ax.invert_yaxis()
    # # ax0.legend(loc = 'lower center')

    # ax0.set_title(adresse)
    # # ax0.set_title(u'$\mathrm{\ %s_{min, max}}$'%VALUE)
    # ax0.set_ylabel(u'$\Delta$T [°C]')
    # ax.autoscale(enable=True, axis='x', tight=True)
    # plt.subplots_adjust(bottom=0.2)
    # plt.show()
    return myData