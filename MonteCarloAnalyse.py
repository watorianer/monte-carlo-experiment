import pandas as pd

data = pd.read_csv('C:\\Users\\Martin\\Downloads\\MonteCarloVerbessert2.csv')


print(data.loc[data['avg_profig'].idxmax()])

#data.drop(columns=['Unnamed: 0', 'mindestreichweite_sofort', 'mindestreichweite_spaeter', 'verlust_prozent', 'standdauer', 'avg_profig'], inplace=True)

print(data.head())

print(data.iat[20, 0])
# data.to_csv('C:\\Users\\Martin Wolff\\Downloads\\MonteCarloSchlank2.csv')

