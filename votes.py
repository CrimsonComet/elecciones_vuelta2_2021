# -*- coding: utf-8 -*-
"""
Autor: Javier Abad
"""

# Importing libraries
import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

path_to_folder = 'D:\\python_scripts\\map_votes'

'''
Open votes information as a pandas DataFrame
'''

## Data was download from 
## 'https://www.datosabiertos.gob.pe/dataset/resultados-por-mesa-de-las-elecciones-presidenciales-2021-segunda-vuelta-oficina-nacional-de'
path_to_vote_file = os.path.join(path_to_folder, 'resultados.csv')
votes_df = pd.read_csv(path_to_vote_file, sep=',', encoding='utf-8', index_col=False) #To avoid error ' byte 0xbf' encode with 'latin-1'
votes_df = votes_df.rename(columns={'ï»¿UBIGEO':'UBIGEO'}) # correct some column names
votes_df = votes_df.fillna(0) # Avoid nan values

# 'UBIGEO' >= 910101 aren't inside Peru
votes_df = votes_df[votes_df['UBIGEO'] < 910101]

# information
# P1:Peru Libre
# P2:Fuerza Popular

# Group by district (DISTRITO) and sort alphabetically
votes_by_district = votes_df.groupby(['UBIGEO', 'DISTRITO']).sum()
votes_by_district = votes_by_district.reset_index ()
votes_by_district = votes_by_district.sort_values(by=['DISTRITO'])
votes_by_district = votes_by_district.reset_index ()
votes_by_district = votes_by_district.drop(['index'], axis=1)

'''
Open a shapefile with distrital limits information
'''
path_to_dist_limits = os.path.join(path_to_folder, 'limite_distrital/DISTRITOS.shp')
distrital_limits = gpd.read_file(path_to_dist_limits)

# Sort districts alphabetically
distrital_limits = distrital_limits.sort_values(by=['DISTRITO'])


'''
Equalize district names in both dataframes
'''

# In votes_by_districts
votes_by_district = votes_by_district.drop([951,1136])
# In distrital_limits
distrital_limits = distrital_limits.drop(671)


# Adding 1 column to votes_by_district with pertentual rate of votes 
# -1 -> +1 
# -1 : 100% for Fuerza Popular
# +1 : 100% for Peru Libre
votes_by_district['rate'] = round(2*(-.5+votes_by_district['VOTOS_P1']/(votes_by_district['VOTOS_P1']+votes_by_district['VOTOS_P2'])),2)
votes_by_district['absenteeism'] = round(votes_by_district['N_CVAS']/votes_by_district['N_ELEC_HABIL'], 2)
distrital_limits['rate'] = votes_by_district['rate']
distrital_limits['absenteeism'] = votes_by_district['absenteeism']

# Plot

fig, ax = plt.subplots(1, figsize=(15,18), facecolor='lightblue')
plt.title('Distribución espacial por distritos de los\nvotos de la 2a vuelta presidencial 2021\n-1: 100% Fuerza Popular; +1: 100% Perú Libre', fontsize=20)
distrital_limits.plot(ax=ax, column = 'rate', cmap='seismic')
ax.set_xlabel('Longitud', fontsize = 13)
ax.set_ylabel('Latitud', fontsize = 13)
min_p = min(distrital_limits['rate'])
max_p = max(distrital_limits['rate'])
bar = plt.cm.ScalarMappable(cmap='seismic', norm = plt.Normalize(vmin = -1, vmax = 1))

bar._A = []
cax = plt.axes([0.85, 0.15, 0.03, 0.7])
cbar = fig.colorbar(bar, cax=cax)
cbar.set_label('Fuerza Popular vs Perú Libre', fontsize = 12)

plt.savefig('segunda_vuelta_distritos.jpg', dpi=300)

