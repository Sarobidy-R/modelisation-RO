# modelisation-RO


## Utilisation 
### 1. Clonez le projet 
### 2. Créez un environnement conda et activez-le pour le projet

```bash
conda create -n nom_env
```

```bash
conda activate nom_env
```

### 3. Installez le dépendances requises contenu dans 'requirements.txt'

```bash
pip install -r requirements.txt
```

### 4. Créez un fichier `.env` contenant votre clé D'API google et le chemin vers votre resolveur `glpk`

```ini
GOOGLE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GLPK_PATH="chemin/vers/glpk"
```
#### Installation de GLPK
##### Sous Windows :
Extraire le fichier `https://drive.google.com/file/d/1b-TBUzo-NVhCfbKJLdg34QkI13SDq-p8/view?usp=sharing` 

#### Sous linux :
Pour les dérivées de Debian : 
```bash 
sudo apt update
sudo apt install glpk-utils
```

Pour les dérivées de Red Hat :
```bash
sudo dnf update
sudo dnf install glpk
```

Chemin général sous linux : "/usr/bin/glpsol"


### 5. Lancement 
```bash
streamlit run app.py
```
