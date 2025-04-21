import pandas as pd
from openpyxl import load_workbook

# Cesta k Excel souboru
excel_path = 'Rozbor_duchod.xlsx'

# Read the CSV file into a DataFrame
df = pd.read_csv('pocet_duchodcu.csv', sep=';', encoding='utf-8')

# Informace o DataFrame
print (df.head(10))
print (df.info())
print (df.describe())
print (df.columns)

# změna sloupce 'datum' na typ datetime
df['datum'] = pd.to_datetime(df['datum'])
print (df.info())

# přídání sloupce "pohlavi" na zakládě kódu pohlavi
df['pohlavi'] = df['pohlavi_kod'].map({"M": 'Muž', "F": 'Žena', "T": 'Celkem'})

# přídání sloupce "druh_duchodu" na zakládě kódu druh_duchodu_kod
df_druh_duchodu = pd.read_csv('Druh_duchodu.csv', sep=';', encoding='utf-8')
df = df.merge(df_druh_duchodu, on='druh_duchodu_kod', how='inner')

# Poměr důchodců s exekucí podle pohlaví a kraje

# 1. Vzít pouze Muž / Žena pro výpočet poměru
df_pohlavi = df[df['pohlavi'].isin(['Muž', 'Žena'])].copy()
df_pohlavi = df_pohlavi.groupby(['kraj', 'pohlavi']).agg({'pocet_duchodcu': 'sum'}).reset_index()

# 2. Výpočet podílu v rámci každého kraje
df_pohlavi['pomer'] = df_pohlavi.groupby('kraj')['pocet_duchodcu'].transform(lambda x: x / x.sum())

# 3. Získat Celkem z původního df
df_celkem = df[df['pohlavi'] == 'Celkem'].copy()
df_celkem = df_celkem.groupby(['kraj', 'pohlavi']).agg({'pocet_duchodcu': 'sum'}).reset_index()
df_celkem['pomer'] = 1.0  # ručně doplnit

# 4. Spojit dohromady
df_vystup = pd.concat([df_pohlavi, df_celkem], ignore_index=True)

# 5. Seřazení podle kraje a pohlaví
df_vystup = df_vystup.sort_values(by=['kraj', 'pohlavi'])

#6. Výpis bez indexu
print(df_vystup.to_string(index=False))

# 7. Uložení do xlsx souboru
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='w') as writer:
    df_vystup.to_excel(writer, sheet_name='Poměr', index=False)

######################################################################################################################

#Porovnání průměrné výše starobního důchodu podle pohlaví a kraje (bez celkem v ČR)

# 1.Zkopírování df pro další zpracování
df_prumer2 = df.copy()

# 2.Odstranění řádků s druhem důchodu "Celkem v ČR"
df_prumer2 = df_prumer2[df_prumer2['druh_duchodu'] != 'Celkem v ČR']

# 3.Zgrupování podle druhu důchodu, pohlaví a kraje
df_prumer2 = df_prumer2.groupby(['druh_duchodu','pohlavi', 'kraj']).agg({'prumerna_vyse_duchodu': 'mean'}).reset_index()

# 4.Seřazení podle druhu důchodu, kraje a pohlaví
df_prumer2 = df_prumer2.sort_values(by=['druh_duchodu','kraj', 'pohlavi'])

# 5.Výpis bez indexu
#df_prumer2_vystup = df_prumer2.to_string(index=False)    
#print (df_prumer2_vystup)

# 6.Uložení do xlsx souboru
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_prumer2.to_excel(writer, sheet_name='Průměr', index=False)

#######################################################################################################################
