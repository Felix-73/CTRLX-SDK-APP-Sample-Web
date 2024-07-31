### SAMPLE-FLASK

Voici un exemple d'application web minimaliste installable sur le ctrlX Core. L'objectif de cette application est de servir de base pour développer une interface utilisateur.

## Instalation 
- Setup l'app build environement du SDK CtrlX
- Modifier le fichier snapcraft si necessaire :  
`base: core20` pour un os 1.X  
`base: core22` pour un os 2.X

- Pour build l'application utiliser les fichiers executables :        
`./build-snap-arm64.sh` pour un CtrlX 3   
`./build-snap-amd64.sh` pour un CtrlX virtuel

