# Installation

Il se peut que le requirements.txt ne fonctionne pas entièrement avec pip, notamment avec :
* Dlib, requiert au minimum un compiler C++ (Ce tuto fonctionne bien sur Windows https://www.geeksforgeeks.org/how-to-install-dlib-library-for-python-in-windows-10/)
* Dlib va réinstaller une version antérieure de torch sans CUDA, donc préférez installer Dlib puis PyTorch
* PyTorch (torch, torchaudio, torchvision) qui doit être installé avec CUDA 11.8 (utiliser la commande adéquate donnée sur https://pytorch.org/get-started/locally/)

# Execution

```python main.py url_fiche_film_allocine```
