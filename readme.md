
    Damien ROCABOIS
    TD-03 – Cybersécurité

## TD-03 – Système de Chiffrement

### Description du projet

Il s’agit d’un programme Python simulant un ransomware  permettant :

    - La vérification des dépendances

    - La génération de clés de chiffrement (AES ou PBKDF2)

    - La sauvegarde sécurisée des clés

    - Le transfert d’une clé via SFTP

    - Le chiffrement de fichiers ou dossiers

    - Le déchiffrement complet


Prérequis

    Python 3.8 ou supérieur

    Modules Python :

        cryptography

        paramiko

Le programme vérifie automatiquement les dépendances au démarrage et peut les installer si nécessaire.

### Lancement du programme

Sous Linux / Mac :

    python3 main.py

Sous Windows :

    python main.py

### Menu principal

Au lancement, le menu suivant apparaît :

Système de Chiffrement - TP3

    1 - Générer une nouvelle clé

    2 - Envoyer une clé via SFTP

    3 - Chiffrer des fichiers/dossiers

    4 - Vérifier les dépendances

    5 - Déchiffrer des fichiers/dossiers

    6 - Quitter

Génération de clé

Deux types de clés sont disponibles :

    AES

Clé générée aléatoirement avec os.urandom

Longueur possible : 128, 192 ou 256 bits

Cryptographiquement sécurisée

    PBKDF2

Clé dérivée d’un mot de passe

Algorithme SHA-256

Salt aléatoire

### Stockage des clés

Les clés sont enregistrées dans le dossier :

    keys/

Format :

    Algorithm

    Length

    Key (encodée en Base64)

Sous Linux, les permissions sont restreintes au propriétaire uniquement.

Transfert SFTP

Permet d’envoyer une clé vers une machine distante via SSH (port 22).

Informations demandées :

    Host (adresse IP de la machine distante)

    Username (utilisateur SSH)

    Password (mot de passe SSH)

    Remote path (chemin distant)

Exemple :

    Host : 192.168.188.147
    Username : user
    Password : ********
    Remote path : /home/user/key.json

Le transfert est sécurisé via le protocole SSH.

Chiffrement

    Algorithme : AES

    Chiffrement direct (le fichier original est remplacé)


Compatible avec :

    Fichiers texte

    Images

    Documents

Fichiers binaires

Déchiffrement

    Utilise la même clé que pour le chiffrement

    Restaure les données originales

    Si la mauvaise clé est utilisée, le fichier restera corrompu.

### Sélection des fichiers

Deux options :

Fichier unique

Dossier complet (parcours récursif)

Le programme utilise os.walk() pour parcourir tous les sous-dossiers.

Barre de progression

Pendant le chiffrement et le déchiffrement, une barre de progression s’affiche :

[█████ ] 50%

Elle indique le pourcentage d’avancement.

### Tests réalisés
Test 1 – Vérification dépendances

Lancement du programme

Vérification automatique réussie


Test 2 – Génération clé AES 256

Création d’une clé

Sauvegarde correcte dans le dossier keys


Test 3 – Transfert SFTP

Connexion vers Kali Linux

Transfert réussi dans /home/kali/


Test 4 – Chiffrement d’un dossier

Sélection dossier

Tous les fichiers deviennent illisibles


Test 5 – Déchiffrement

Utilisation de la clé correcte

Fichiers restaurés correctement




Conclusion

Ce projet démontre :

    La mise en œuvre d’AES

    L’utilisation de PBKDF2

    La gestion sécurisée des clés

    Le transfert sécurisé via SFTP

    Le chiffrement automatisé
