
## Installation

```bash
$ mkvirtualenv birth-names
$ pip install -r requirements.txt
```

## Configuration

1. Download national birth record files from the U.S. Social Security Administration [here](https://www.ssa.gov/oact/babynames/names.zip)
2. Extract to `/data/us` folder
  - _you should see many files named `yob{YYYY}.txt`_
3. Start a PostgreSQL server and save the access credentials in `.env`
4. Run `download.py` to retrieve national birth records from the U.K. Office for National Statistics (ONS)
  - _this should produce many `.xls` files in the `/data/uk` folder_

## Use

Create the database tables:

```bash
$ python3 database.py
```

Load the database:

```bash
$ python3 process.py
```

Creates a data model for birth records and initializes a database schema using [Peewee ORM](http://docs.peewee-orm.com/en/latest/). Loops through all U.S. and U.K. data files in `/data/` and loads the records into a PostgreSQL database.
