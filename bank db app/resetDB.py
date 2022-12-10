from sqlalchemy import create_engine
import pandas as pd
c_df = pd.read_csv('./static/customers.csv')
a_df = pd.read_csv('./static/accounts.csv')


engine = create_engine('sqlite:///tmp/bank.db', convert_unicode=True)

c_df.to_sql('customers', con=engine, if_exists='replace', index= False)
a_df.to_sql('accounts', con=engine, if_exists='replace', index= False)


