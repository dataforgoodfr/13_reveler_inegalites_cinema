import pandas as pd 
import os
import tqdm
import uuid
import unicodedata

script_dir = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(script_dir, '../database/data/dataset_5050_CNC_films.xlsx')
DISTRIBUTORS_COLUMNS = ['PAYANTE', 'PAYANT', 'CLAIR']

def remove_accents(input_str: str) -> str:
    """
    This function removes accents from a string.

    Args:
        input_str (str): The input string from which accents need to be removed.

    Returns:
        str: A new string with all accents removed.
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def get_sheet_names(file_path: str) -> list:
    """
    This function extracts the names of the sheets containing the movies data.

    Args:
        file_path (str): The path to the Excel file.

    Returns:
        list: A list containing the names of the sheets in the Excel file.
    """
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    print(f"{len(sheet_names)} feuilles trouvés dans le fichier {file_path}")
    sheet_names = [sheet for sheet in sheet_names if '20' in sheet]
    return sheet_names


def get_distributors_from_sheet(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function extracts the distributors from the parameters sheet of the dataset.

    Args:
        df (pd.DataFrame): a dataframe containing the parameters sheet of the dataset.

    Returns:
        pd.DataFrame: a dataframe containing the distributors with the information for the database.
    """
    # get unique values from the parameters sheet
    unique_distributors = [value for value in df.iloc[:,1].fillna("").unique().tolist()]
    unique_distributors.remove("")

    df_distributors = pd.DataFrame(unique_distributors, columns=["legal_name"])
    # add a column for the type of credit_holders with a default value
    df_distributors['type'] = "company"
    # add UUID column
    df_distributors['uuid'] = [uuid.uuid4() for _ in range(len(df_distributors))]
    # add other columns with empty values
    new_columns = ["first_name", "last_name", "gender", "birthdate"]
    for col in new_columns:
        df_distributors[col] = pd.NA

    return df_distributors


def get_distributors_mapping(df_distributors: pd.DataFrame, df_parameters: pd.DataFrame, 
                             merge_column: str) -> pd.DataFrame:
    """
    This function creates a mapping between the distributors and the parameters values to get the id of the distributors.
    
    Args:
        df_distributors (pd.DataFrame): a dataframe containing the distributors.
        df_parameters (pd.DataFrame): a dataframe containing the parameters values.
        merge_column (str): the column to merge on.

    Returns:
        pd.DataFrame: a dataframe containing the value that should be matched within the dataset and the uuid of the distributor.
    """
    df_mapping = df_distributors.merge(
        df_parameters, how='right', 
        left_on=merge_column, right_on=merge_column
    )
    df_mapping = df_mapping[['code', 'uuid']]
    df_mapping['code'] = df_mapping['code'].map(lambda x: remove_accents(x).lower())
    
    return df_mapping


def match_roles(row, columns: list, df_mapping: pd.DataFrame) -> list:
    """
    This function matches the value of the dataset with a mapping of the value linked to an uuid.
    This function has to be used with the apply method of a pandas dataframe.

    Args:
        row (pd.Series): the row of the dataset.
        columns (list): the columns that contains the values to match.
        df_mapping (pd.DataFrame): the mapping between the values and the uuid.

    Returns:
        list: a list of uuids of the matched values.
    """
    roles = []
    
    for col in columns:
        # if the value is missing, return an empty list
        if pd.isna(row[col]):
            continue
    
        # remove accents and convert to lower case to better match the values
        row_value = remove_accents(row[col]).lower()
    
        # for each code, check if the value is in the row
        for iter, mapping in df_mapping.iterrows():
            if mapping['code'] in row_value:
                roles.append(mapping['uuid'])

    return list(set(roles))


sheet_names = get_sheet_names(DATASET)

df_parameters = pd.read_excel(DATASET, sheet_name="parameters", header=0)
df_parameters.rename(columns={'Chaîne correspondante': 'legal_name', 'Liste des chaînes': 'code'}, inplace=True)

# the following dataframe can be inserted to the database credit_holders table with a DELETE/INSERT strategy
df_distributors = get_distributors_from_sheet(df_parameters)

# Iterate on each sheet to extract and clean the data
# for sheet in tqdm.tqdm(sheet_names, desc="Processing sheets"):

df_films = pd.read_excel(DATASET, sheet_name=sheet_names[0], skiprows=4)

distributors_columns = [column for column in DISTRIBUTORS_COLUMNS if column in df_films.columns]
distributors_mapping = get_distributors_mapping(df_distributors, df_parameters, 'legal_name')

df_films['distributors_id'] = df_films.apply(match_roles, axis=1, columns=distributors_columns, df_mapping=distributors_mapping)

# the following dataframe can be appended to the database films_credits table
# you will find Nan values because the parameters sheet does not contain all the distributors
films_distributors = df_films[['TITRE','distributors_id']].explode('distributors_id')

print(df_films.head())
print(films_distributors.head())