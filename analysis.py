import pandas as pd
import peewee
import plotly.express as px
import streamlit as st

from database import DbYear, DbBirthRecord, DbName
from favorites import favorites


## set up the basic sidebar widgets
sex = st.sidebar.radio('Sex:', ['M', 'F'], index=0)
country = st.sidebar.radio('Country:', ['US', 'UK'], index=0).lower()
min_year = st.sidebar.slider('Min year:', min_value=1900, max_value=2021, value=1980, format="%s")


## get the yearly total birth counts for the chosen sex, country, and years
total_query = (DbYear
               .select(
                    DbYear.year,
                    DbYear._meta.fields.get(f'births_{country}_{sex.lower()}').alias('total'))
               .where(DbYear.year >= min_year)
               .order_by(+DbYear.year))

connection = total_query._database.connection()

sql, params = total_query.sql()
df_total = pd.read_sql_query(sql, connection, params=params)


## get a list of the top N most popular US names for the given sex, since 1900
## as options for the sidebar multiselect widget
n = 4500
for s in ['M', 'F']:
    top_cte = (DbBirthRecord
            .select(
                DbName.name.alias('name'),
                peewee.fn.SUM(DbBirthRecord.births).alias('sum'),
                peewee.fn.RANK().over(order_by=[-peewee.fn.SUM(DbBirthRecord.births)]).alias('rank'))
            .join(DbName)
            .switch(DbBirthRecord)
            .join(DbYear)
            .where(
                    DbYear.year >= 1900,
                    DbBirthRecord.country == 'us',
                    DbBirthRecord.sex == s)
            .group_by(DbName.name)
            .cte('top_cte', columns=['name', 'sum', 'rank']))
    top_query = (DbName
                .select(DbName.name)
                .join(top_cte, on=(DbName.name == top_cte.c.name))
                .where(top_cte.c.rank <= n)
                .order_by(+top_cte.c.rank)
                .with_cte(top_cte))

    sql, params = top_query.sql()

    r = pd.read_sql_query(sql, connection, params=params)

    if s == 'M':
        df_top_m = r
    elif s == 'F':
        df_top_f = r

names = st.sidebar.multiselect(f'{sex} names:', df_top_m if sex == 'M' else df_top_f, default=favorites[sex])


## get the names and birth counts that will actually be plotted
## and then add the calculated births_per_k field
names_query = (DbBirthRecord
               .select(
                   DbName.name,
                   DbYear.year,
                   DbBirthRecord.births)
               .join(DbName)
               .switch(DbBirthRecord)
               .join(DbYear)
               .where(
                   DbBirthRecord.country == country,
                   DbBirthRecord.sex == sex,
                   DbName.name.in_(names),
                   DbYear.year >= min_year)
               .order_by(+DbName.name, +DbYear.year))

sql, params = names_query.sql()
df_names = pd.read_sql_query(sql, connection, params=params)

result = pd.merge(df_names, df_total, how="left", on="year")
result = result.assign(births_per_k = result['births'] / (result['total'] / 1000))


## make the plot
fig = px.line(result, x='year', y='births_per_k', color='name', log_y=True)
fig.update_layout(height=570, yaxis_title='Births per thousand', xaxis_title=None)
st.plotly_chart(fig)
