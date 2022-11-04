import pandas as pd
import os

df_url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/ilc_peps01n.tsv.gz"
# Dit bestand gebruikt zowel komma als tab om kolommen te scheiden.
df = pd.read_csv(df_url, sep="\t|,", engine="python", compression="gzip")

# Hernoem de titels van de kolommen en haal overtollige spaties weg
df.columns.values[3] = "Land"
df.columns = df.columns.map(lambda x: x.strip())

# Er staan extra spaties bij de getallen, haal die weg met strip()
# Sommige getallen worden gevolgd door een letter, haal die weg met een regular expression.
# De regular expression vervangt een getal gevolgd door meer dan één spatie of letter, door alleen dat getal
# Waar ":" staat, dit vervangen door NA
for columnNumber in range(4, len(df.columns)):
    try:
        df.iloc[:,columnNumber] = df.iloc[:,columnNumber].astype(str).str.strip().replace(r'(\d+)[ a-z]+', r'\1', regex=True).replace(':', pd.NA)
    except Exception as e:
        print(columnNumber, e)

# Selecteer de rijen met gegevens voor alle genders en leeftijden
dfAllAgesPC = df[(df['age'] == 'TOTAL') & (df['unit'] == 'PC') & (df['sex'] == 'T')].drop(columns=['unit','age','sex']).reset_index(drop=True).rename(columns={'geo\time': 'Land'})
dfAllAgesNumber = df[(df['age'] == 'TOTAL') & (df['unit'] == 'THS_PER') & (df['sex'] == 'T')].drop(columns=['unit','age','sex']).reset_index(drop=True)

# Alleen het meest recente jaar exporteren.
dfAllAgesPCRecent = dfAllAgesPC.drop(dfAllAgesPC.columns[2:len(dfAllAgesPC)], axis=1).dropna()
dfAllAgesNumberRecent = dfAllAgesNumber.drop(dfAllAgesNumber.columns[2:len(dfAllAgesNumber)], axis=1).dropna()

# Percentage omzetten naar float
dfAllAgesPCRecent.iloc[:,1] = dfAllAgesPCRecent.iloc[:,1].astype(float) / 100.0
# Dit is een aantal per duizend. Omzetten naar absoluut aantal
dfAllAgesNumberRecent.iloc[:,1] = dfAllAgesNumberRecent.iloc[:,1].astype(int) * 1000

# Sorteren en exporteren naar csv
dfAllAgesPCRecent.sort_values(by = dfAllAgesPC.columns[1], ascending=False).to_csv('RiskOfPovertyOrSocialExclusionPercent.csv', index = False)
dfAllAgesNumberRecent.sort_values(by = dfAllAgesNumber.columns[1], ascending=False).to_csv('RiskOfPovertyOrSocialExclusionNumber.csv', index = False)
