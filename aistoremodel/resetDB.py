from sqlalchemy import create_engine
import pandas as pd
s_df = pd.read_csv('./static/stores.csv')
p_df = pd.read_csv('./static/products.csv')
i_df = pd.read_csv('./static/inventory.csv')

engine = create_engine('sqlite:///tmp/aistore.db', convert_unicode=True)

# stores.csv 데이터프레임으로 불러온 후 sql stores 테이블로 저장
# products.csv 데이터프레임으로 불러온 후 sql products 테이블로 저장
# inventory.csv 데이터프레임으로 불러온 후 sql inventory 테이블로 저장

s_df['sPassword'] = ['s1','s2','s3']
s_df.to_sql('stores', con=engine, if_exists='replace', index= False)

i_df.to_sql('inventory', con=engine, if_exists='replace', index= False)
p_df.to_sql('products', con=engine, if_exists='replace', index= False)

