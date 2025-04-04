import pandas as pd
import os
import re
import openpyxl # noqa: F401
from typing import Optional
from .cnc_constants import COLUMNS_MAPPING, FREE_DISTRIBUTORS_MAPPING, PAYING_DISTRIBUTORS_MAPPING, COUNTRIES_MAPPING

class ExtractCncDataFromExcel:
    """
    This class is responsible for extracting and cleaning CNC data from an Excel file.
    It handles loading the data, cleaning it, and transforming it into a structured format.
    """
    def __init__(self, file_path=None):
        if file_path is None:
            # Compute default path relative to this file
            base_dir = os.path.dirname(__file__)
            file_path = os.path.join(
                base_dir,
                "dataset5050_cnc_films_agrees_2003_2024.xlsx"
            )
        self.file_path = file_path
        self.df = None

    def load_data(self):
        """
        Load data from the Excel file, skipping the first 4 rows and renaming columns.
        """
        if not os.path.exists(self.file_path):
            print(f"File not found: {self.file_path}")
            return None

        try:
            all_sheets = pd.read_excel(self.file_path, sheet_name=None, engine='openpyxl', skiprows=4)
            year_sheets = list(all_sheets.keys())[1:] # Skip the first sheet (summary tab)

            combined_data = []

            for sheet_name in year_sheets:
                if not sheet_name.isdigit():
                    continue  # skip if sheet name is not a year

                sheet_df = all_sheets[sheet_name].reset_index(drop=True)

                # Rename specific column that has two names: "PAYANT", "PAYANTE"
                if "PAYANT" in sheet_df.columns and "PAYANTE" not in sheet_df.columns:
                    sheet_df.rename(columns={"PAYANT": "PAYANTE"}, inplace=True)

                sheet_df['year'] = sheet_name

                combined_data.append(sheet_df)

            self.df = pd.concat(combined_data, ignore_index=True)
            
            self.df.rename(columns=COLUMNS_MAPPING, inplace=True)

            if self.df.empty:
                print("No valid data found in any sheet.")
                return None

            print("Data loaded successfully")
            return self.df

        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    
    def clean_data(self):
        """
        Clean the loaded data by dropping empty columns, converting types, and parsing specific fields.
        """
        if self.df is None:
            print("No data to clean. Please load data first.")
            return None

        # Drop columns that are completely empty
        self.df.dropna(axis=1, how='all', inplace=True)

        # Clean specific columns
        self.df["cnc_rank"] = self.df["cnc_rank"].astype(str).str.extract(r'(\d+)')
        self.df["asr"]= self.df["asr"].fillna("").str.replace("apres", "après", regex=False)
        self.df["original_name"] = self.df["original_name"].apply(self._clean_title)

        # Reformating colums to correct format
        self._reformat_columns_to_boolean(["parity_bonus", "sofica_funding", "tax_credit", "regional_funding", "eof"])
        self._reformat_columns_to_numeric(["cnc_agrement_year", "cnc_rank", "budget", "visa_number", "cnc_rank"])
        self._reformat_columns_to_array(["directors_names", "producers_names"])

        # Convert columns to dicts or arrays
        self.df["film_country_budget_allocation_rates"] = self.df["film_country_budget_allocation_rates"].apply(self._parse_country_budget_allocations)
        self.df["free_distributors"] = self.df["free_distributors"].apply(lambda x: self._parse_distributor_string(x, FREE_DISTRIBUTORS_MAPPING))
        self.df["paying_distributors"] = self.df["paying_distributors"].apply(lambda x: self._parse_distributor_string(x, PAYING_DISTRIBUTORS_MAPPING))

        return self.df
    

    def _reformat_columns_to_boolean(self, columns: Optional[list] = None) -> None:
        columns = columns or []
        for column in columns:
            if column in self.df.columns:
                self.df[column] = self.df[column].fillna('').str.strip().str.upper().isin(['X', 'OUI'])


    def _reformat_columns_to_numeric(self, columns: Optional[list] = None) -> None:
        columns = columns or []
        for column in columns:
            if column in self.df.columns:
                self.df[column] = pd.to_numeric(self.df[column], errors='coerce')


    def _reformat_columns_to_array(self, columns: Optional[list] = None) -> None:
        columns = columns or []
        for col in columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("").apply(lambda x: [item.strip() for item in x.split("/") if item.strip()])


    def _clean_title(self, title: str) -> str:
        """
        Cleans the title by putting back to the start of title the articles in parentheses at the end of the title.
        It also converts full uppercase titles to proper case.
        """
        if not isinstance(title, str):
            return title

        # Supprimer les articles en fin de titre entre parenthèses
        match = re.search(r'\s*\((L\'|Le|La|Les|LE|LA|LES)\)$', title)
        if match:
            article = match.group(1)
            title = re.sub(r'\s*\((L\'|Le|La|Les|LE|LA|LES)\)$', '', title)
            if article == "L'":
                title = f"{article}{title[0].lower() + title[1:]}"  
            else:
                title = f"{article} {title[0].lower() + title[1:]}" if title else article

        # Supprimer toute parenthèse fermante isolée à la fin
        title = re.sub(r'\s*\)+$', '', title)

        # Convert full uppercase titles to proper case
        if title.isupper():
            title = title.capitalize()

        return title.strip()


    def _parse_country_budget_allocations(self, value: str) -> dict:
        """
        Parses a string of country budget allocation rates into a dictionary.
        """
        if not isinstance(value, str) or not value.strip():
            return {}

        entries = re.split(r'\s*/\s*', value.strip())
        result = {}

        for entry in entries:
            try:
                country_code, rate = entry.strip().rsplit("-", 1)
                country_key = country_code.strip().lower()
                rate_value = int(rate.strip())
                country = COUNTRIES_MAPPING.get(country_key, country_code.strip().capitalize())  # fallback to raw label if no match
                result[country] = rate_value
            except Exception:
                continue  # skip malformed parts

        return result
    

    def _parse_distributor_string(self, distributor_string: str, mapping: Optional[dict] = None) -> list:
        mapping = mapping or {}
        if not isinstance(distributor_string, str):
            return []

        parts = distributor_string.strip().split()
        result = []

        for part in parts:
            normalized = part.strip().lower()
            mapped = mapping.get(normalized)
            result.append(mapped) if mapped else None

        return result

