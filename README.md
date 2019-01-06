
## Installation

```bash
$ mkvirtualenv names
$ pip install -r requirements.txt
```

## Configuration

1. Download national birth record files from the U.S. Social Security Administration [here](https://www.ssa.gov/oact/babynames/names.zip)
2. Extract to `/data/` folder
  - _should contain many files like `yob{YYYY}.txt`_
3. Start a PostgreSQL server and save the access credentials in `.env` and in `database.py`

## Use

```bash
$ python3 run.py
```

Creates a data model for birth records and initializes a database schema using [Peewee ORM](http://docs.peewee-orm.com/en/latest/). Loops through all data files in `/data/` and loads them into the model/database.

Explore the data in the database with a PostgreSQL client.
