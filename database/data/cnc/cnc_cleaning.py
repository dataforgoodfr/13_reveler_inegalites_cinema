# Importer les library
import pandas as pd
import re

#### Importer le fichier xlsx et concatener les feuilles dans un dataframe unique  ######

def importer_et_concatener_cnc(file_path, sommaire_name='Sommaire'):
    try:
        xls = pd.ExcelFile(file_path)
        sheet_data = {}
        for sheet_name in xls.sheet_names:
            if sheet_name != sommaire_name:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=4)
                # Ajouter une colonne avec le nom de la feuille (qui sera l'année)
                if sheet_name.isdigit():
                    year = int(sheet_name)
                    df['CNC AGREMENT YEAR'] = year
                else:
                    df['CNC AGREMENT YEAR'] = None
                sheet_data[sheet_name] = df

        final_df = pd.concat(sheet_data.values(), ignore_index=True)

        return final_df
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{file_path}' n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier: {e}")
        return None

if __name__ == '__main__':
    nom_sommaire = 'Sommaire'
    df_cnc = importer_et_concatener_cnc('/content/Dataset5050_CNC Films Agréés 2003-2024.xlsx', sommaire_name=nom_sommaire)



#### Nettoyer les titres ######

def clean_title(title):
    if isinstance(title, str):
        cleaned_title = title.strip()  # Supprimer les espaces en début et fin

        # Rechercher un article en fin de titre entre parenthèses
        match = re.search(r'\s*\((L\'|Le|La|Les)\)$', cleaned_title)
        if match:
            article = match.group(1)  # Extraire l'article
            cleaned_title_sans_article = re.sub(r'\s*\((L\'|Le|La|Les)\)$', '', cleaned_title).strip()
            if cleaned_title_sans_article:
                cleaned_title = f"{article.lower()} {cleaned_title_sans_article[0].upper() + cleaned_title_sans_article[1:]}"
            else:
                cleaned_title = article.lower() # Si le titre ne contenait que l'article entre parenthèses

        # Supprimer toute parenthèse fermante isolée en fin de titre
        cleaned_title = re.sub(r'\s*\)+$', '', cleaned_title).strip()

        return cleaned_title
    return title

# Appliquer la fonction au DataFrame
df_cnc["TITRE"] = df_cnc["TITRE"].apply(clean_title)


#### Convertir en booléen ######

df_cnc["BONUS PARITE "] = df_cnc["BONUS PARITE "].notna()
df_cnc["SOFICA"] = df_cnc["SOFICA"].notna()
df_cnc["CREDIT D'IMPOT"] = df_cnc["CREDIT D'IMPOT"].notna()
df_cnc["AIDE REGIONALE"] = df_cnc["AIDE REGIONALE"].notna()
df_cnc["EOF"] = df_cnc["EOF"].apply(lambda x: True if x.lower() == "oui" else False)

# Convertir en les Nan en N/A
df_cnc["ASR"]= df_cnc["ASR"].fillna("N/A")


#### Mise à jour des Dtype ######

df_cnc['RANG'] = df_cnc['RANG'].astype(int)
df_cnc['DEVIS'] = df_cnc['DEVIS'].astype(float)



###### Conversion des codes pays en noms complets  ######

# Dictionnaire de conversion des codes pays en noms complets
country_mapping = {
 'NC': [''],
 'Afrique du sud' : ['Af du sud',],'Af. du sud'
 'Algérie': ['Algerie'],
 'Allemagne': ['All'],
 'Argentine' : ['Arg'],
 'Arménie': ['Armenie'],
 'Belgique': ['Belg','Bel','Be'],
 'Bosnie-Herzégovine': ['Bosnie herz','Bosnie','Bosnie herzegovine','Bosnie herzégovine'],
 'Brésil': ['Bresil'],
 'Bulgarie': ['Bulg'],
 'Canada': ['Can'],
 'Corée': ['Coree'],
 'Danemark': ['Dan'],
 'Espagne': ['Es','Esp'],
 'Etats unis': ['Us'],
 'Finlande': ['Fin'],
 'France': ['Fr'],
 'Grande-Bretagne': ['Gb','Grande bretagne','R-U'],
 'Grèce': ['Grece'],
 'Géorgie': ['Georgie'],
 'Irlande': ['Irl'],
 'Israël': ['Israel','Isr'],
 'Italie': ['It'],
 'Luxembourg': ['Lux'],
 'Macédoine': ['Macédoine du n','Macedoine'],
 'Mexique': ['Mex'],
 'Norvège': ['Norvege','Norv'],
 'Nouvelle-Zélande': ['Nouvelle zelande'],
 'Pays-Bas': ['Pays bas'],
 'Pologne': ['Pol'],
 'Portugal': ['Port'],
 'Roumanie': ['Roum'],
 'République tchèque': ['Rép. tch.','Rép tchèque','Rép tch','Republique tcheque','Rep tchèque','Rep tcheque','Rep tcheq'],
 'Slovénie': ['Slovenie'],
 'Suède': ['Suede'],
 'Sénégal': ['Senegal'],
 'Taïwan':['Taiwan'],
 'Turquie': ['Turquiee'],
}


# Fonction pour extraire les noms des pays
def extract_nationalities(champ):
    result = []
    if isinstance(champ, str):
        morceaux = [part.strip().capitalize() for part in champ.split("/")]
        for morceau in morceaux:
            match = re.match(r'([A-Za-zÀ-ÿ\s\.]+)-(\d+)', morceau)
            if match:
                code, _ = match.groups()
                cles = [cle for cle, val_liste in country_mapping.items() if code in val_liste]
                nom_pays = cles[0] if cles else code
                result.append(nom_pays.strip().title().replace("  ", " "))
            else:
                result.append(morceau)
    return ", ".join(result)

# Fonction pour extraire les pourcentages
def extract_ratios(champ):
    result = []
    if isinstance(champ, str):
        morceaux = [part.strip().capitalize() for part in champ.split("/")]
        for morceau in morceaux:
            match = re.match(r'([A-Za-zÀ-ÿ\s\.]+)-(\d+)', morceau)
            if match:
                _, ratio = match.groups()
                result.append(ratio)
            else:
                result.append("")  # ou None si tu préfères
    return ", ".join(result)

# Appliquer le nettoyage sur toutes les feuilles
df_cnc["NATIONALITE CLEAN"] = df_cnc["NATIONALITE"].apply(extract_nationalities)  # Nettoyer les pays
df_cnc["NATIONALITE RATIO"] = df_cnc["NATIONALITE"].apply(extract_ratios)  # Extraire les ratios


###### Nettoyer les Genres ######

# Dictionnaire pour uniformisation de l'orthographe des genres
genre_mapping = {
    r"animation|anim": "Animation",
    r"documentaire|docu": "Documentaire",
    r"fiction": "Fiction"
}

# Création de la fonction de nettoyage
def normaliser_genre(mot):
    if not isinstance(mot, str):
        return mot  # Pour éviter les erreurs avec NaN ou autres types

    for motif, remplacement in genre_mapping.items():
        if re.search(motif, mot, flags=re.IGNORECASE):
            return remplacement
    return mot.strip().capitalize()

# Application sur la colonne GENRE
df_cnc["GENRE"] = df_cnc["GENRE"].apply(normaliser_genre)

###### Renomer les colonnes  ######
df_cnc  = df_cnc.rename(columns={"VISA":"cnc_visa","TITRE": "original_name","DEVIS":"budget","BONUS PARITE ":"parity_bonus","EOF": "eof","ASR":"asr","SOFICA":"sofica_funding","CREDIT D'IMPOT":	"tax_credit","AIDE REGIONALE":"regional_funding","CNC AGREMENT YEAR":"cnc_agreement_year","RANG":"cnc_rank","GENRE":"cnc_genre"})
