## Instructions

### 1. Install

```bash
$ git clone <this repo>
$ cd birth-names
$ mkvirtualenv birth-names
$ pip install -r requirements.txt
```

### 2. Start a PostgreSQL server and save the access credentials

For local use, you can spin up a database in [Postgres.app](https://postgresapp.com/). Then, using the example provided in `.env.sample` as a template, save your access credentials in a new file named `.env`.

Afterward, don't forget to:

```bash
$ source .env
```

### 3. Download source data from web and save to local folder

```bash
$ python3 download.py
```

The result should be two folders, `data/us` and `data/uk`. Each should contain many files with annual birth records for the respective country plus one summary file of total births with a name like `us_births_by_year.csv` (or `uk_…`).

### 4. Create the database tables

```bash
$ python3 database.py
```

The result should be three new empty tables in your database: `year`, `birth_record`, and `name`.


### 5. Load the database tables

```bash
$ python3 process.py
```

Creates a data model for birth records and initializes a database schema using [Peewee ORM](http://docs.peewee-orm.com/en/latest/). Loops through all U.S. and U.K. data files in `/data/` and loads the records into a PostgreSQL database. This could take as long as a half hour to complete.
