
Ce dossier contient le code de machine learning pour l'analyse automatique des différentes images (frames) de bande-annonces.

# Installation


Pour installer les requirements: 
`pip3 install -r ml-image/requirements.txt`

Il se peut que le requirements.txt ne fonctionne pas entièrement avec pip, notamment avec :
* Dlib, requiert au minimum un compiler C++ (Ce tuto fonctionne bien sur Windows https://www.geeksforgeeks.org/how-to-install-dlib-library-for-python-in-windows-10/)
* Dlib va réinstaller une version antérieure de torch sans CUDA, donc préférez installer Dlib puis PyTorch
* PyTorch (torch, torchaudio, torchvision) qui doit être installé avec CUDA 11.8 (utiliser la commande adéquate donnée sur https://pytorch.org/get-started/locally/)


Dans le cas où le développement se fait sur windows, il faut également installer:
`pip3 install -r ml-image/requirements_windows.txt`

## Modeles

Différents modèles déjà entrainés sont utilisés dans la pipeline. Les poids doivent etre téléchargés avant de lancer le script.

- Détection des personnes: https://github.com/ultralytics/ultralytics
- Detection des visages: https://github.com/akanametov/yolo-face ([poids du modele](https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov11n-face.pt))
- Classification de l'âge, de l'ethnie et du sexe: https://github.com/dchen236/FairFace/tree/master ([poids du modele](https://drive.google.com/file/d/113QMzQzkBDmYMs9LwzvD-jxEZdBQ5J4X/view?usp=drive_link))


Pour les télécharger automatiquement dans un dossier `ml-image/models`:
```bash
bash ml-image/install/download_models.sh
```

# Execution


Pour analyser une bande-annonce de film:
```python main.py url_fiche_film_allocine```

La pipeline est la suivante:
1. extraction des différentes frames 2D de la bande-annonce
2. détection des visages présents sur les différentes frames
3. filtre des visages détectés selon plusieurs critères (proportion de l'image occupée, netteté etc.)
4. classification des visages selon plusieurs caractéristiques (âge, genre, ethnie)
5. aggrégation des résultats pour chacun des personnages identifiés (vote majoritaire)
