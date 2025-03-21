import os
import time
from functools import wraps

from psycopg2 import Error
from sqlalchemy import create_engine, text
import dotenv
import pandas as pd
from termcolor import colored
dotenv.load_dotenv()

def emptyDf():
    return pd.DataFrame()

def get_connection_parameters():
    PG_USERNAME = os.environ.get("POSTGRES_USER", "postgres")
    PG_PWD = os.environ.get("POSTGRES_PASSWORD", "postgres")
    PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    PG_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
    PG_DB = os.environ.get("POSTGRES_DB", "ric_db")
    return (PG_USERNAME, PG_PWD, PG_HOST, PG_PORT, PG_DB)

def get_connection():
    PG_USERNAME, PG_PWD, PG_HOST, PG_PORT, PG_DB = get_connection_parameters()
    return create_engine(f'postgresql://{PG_USERNAME}:{PG_PWD}@{PG_HOST}:{PG_PORT}/{PG_DB}')

def print_query_decorator():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(colored("Running query", "blue"))
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(colored(f"Query run ended in {end_time - start_time:.2f} seconds", "blue"))
            return result
        return wrapper
    return decorator

def execute_query(query, parameters=None, verbose=False):
    try:
        with get_connection().connect() as conn:
            conn.execute(text(query), parameters)
    except Error as e:
        print(colored("ERROR EXECUTE_QUERY: An error occurred while executing the query.\n-- Error: ", "red"))
        print(colored(e, "red"))
        print(colored("-- Query: ", "red"))
        print(colored(query, "red"))
        print(colored("EXECUTE_QUERY: Parameters:\n-- Parameters: ", "red"))
        print(colored(parameters, "red"))

# @print_query_decorator()
def query_data(query, parameters=None, use_cache=True, verbose=False):
    try:
        engine = get_connection()
        df = pd.read_sql_query(query, engine, params=parameters)
            
        if verbose:
            print(colored(parameters, "magenta"))
            print(colored(query, "magenta"))
            print(colored(df, "magenta"))

    except Exception as e:
        print(colored("ERROR GET_DATA: An error occurred while querying the data.\n-- Error: ", "red"))
        print(colored(e, "red"))
        print(colored("-- Query: ", "red"))
        print(colored(query, "red"))
        print(colored("GET_DATA: Parameters:\n-- Parameters: ", "red"))
        print(colored(parameters, "red"))
        df = None

    return df if df is not None else emptyDf()

def check_connection(verbose=False):
    PG_USERNAME, PG_PWD, PG_HOST, PG_PORT, PG_DB = get_connection_parameters()
    if verbose:
        print(colored(f"PG_HOST: {PG_HOST}", "yellow"))
        print(colored(f"PG_PORT: {PG_PORT}", "yellow"))
        print(colored(f"PG_USERNAME: {PG_USERNAME}", "yellow"))
        print(colored(f"PG_DB: {PG_DB}", "yellow"))

    try:
        with get_connection().connect() as conn:
            conn.execute("SELECT 1")
            if verbose:
                print(colored("Connection successful", "green"))
            return True
    except Error as err:
        print(
            colored(f"ERROR CHECK_CONNECTION PG: An error occurred while checking the connection.-- Host: {PG_HOST} -- Port: {PG_PORT} -- User: {PG_USERNAME} -- DB: {PG_DB} --Error: {err}", "red"),
        )
        return False

if __name__ == "__main__":
    check_connection(verbose=True)