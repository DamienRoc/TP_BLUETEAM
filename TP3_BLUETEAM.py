#!/usr/bin/env python3

import os
import sys
import json
import stat
import base64
import subprocess
from datetime import datetime
from getpass import getpass


# ==============================
# PARTIE A : Vérification dépendances
# ==============================

def check_dependencies():
    print("Vérification des dépendances...")

    if sys.version_info < (3, 8):
        print("Python 3.8+ requis.")
        sys.exit(1)

    required = ["cryptography", "paramiko"]
    missing = []

    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"Modules manquants : {missing}")
        choice = input("Installer automatiquement ? (O/N) : ").lower()

        if choice == "o":
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *missing]
            )
        else:
            sys.exit(1)

    print("✓ Toutes les dépendances sont installées.\n")


# ==============================
# PARTIE C : Génération de clé
# ==============================

def generate_key(algo, length):

    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend

    if algo.upper() == "AES":
        return os.urandom(length // 8)

    elif algo.upper() == "PBKDF2":
        password = getpass("Mot de passe : ").encode()
        salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length // 8,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        return kdf.derive(password)

    else:
        raise ValueError("Algorithme non supporté.")


def save_key(key, algo, length):

    os.makedirs("keys", exist_ok=True)

    filename = f"key_{algo.lower()}_{length}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join("keys", filename)

    data = {
        "algorithm": algo,
        "length": length,
        "key": base64.b64encode(key).decode()
    }

    with open(path, "w") as f:
        json.dump(data, f)

    if os.name != "nt":
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)

    print(f"✓ Clé sauvegardée : {path}")
    return path


# ==============================
# PARTIE D : SFTP (VERSION SIMPLIFIÉE)
# ==============================

def send_sftp(local_path):

    import paramiko

    host = input("Host : ")
    username = input("Username : ")
    password = input("Password : ")
    remote_path = input("Remote path : ")

    try:
        transport = paramiko.Transport((host, 22))
        transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, remote_path)

        sftp.close()
        transport.close()

        print("✓ Transfert réussi.")

    except Exception as e:
        print(f"Erreur SFTP : {e}")


# ==============================
# PARTIE E : Chiffrement / Déchiffrement
# ==============================

def encrypt_file(filepath, key):

    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    try:
        with open(filepath, "rb") as f:
            data = f.read()

        iv = os.urandom(16)

        cipher = Cipher(
            algorithms.AES(key),
            modes.CFB(iv),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()
        encrypted = encryptor.update(data) + encryptor.finalize()

        with open(filepath, "wb") as f:
            f.write(iv + encrypted)

    except Exception as e:
        print(f"Erreur chiffrement {filepath} : {e}")


def decrypt_file(filepath, key):

    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    with open(filepath, "rb") as f:
        data = f.read()

    iv = data[:16]
    encrypted = data[16:]

    cipher = Cipher(
        algorithms.AES(key),
        modes.CFB(iv),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted) + decryptor.finalize()

    with open(filepath, "wb") as f:
        f.write(decrypted)


# ==============================
# PARTIE F : Sélection fichiers
# ==============================

def select_directories():

    print("[1] Fichier unique")
    print("[2] Dossier complet")
    choice = input("Choix : ")

    paths = []

    if choice == "1":
        path = input("Chemin fichier : ")
        if os.path.isfile(path):
            paths.append(path)

    elif choice == "2":
        folder = input("Chemin dossier : ")
        for root, _, files in os.walk(folder):
            for file in files:
                paths.append(os.path.join(root, file))

    return paths


def progress_bar(current, total):
    percent = int((current / total) * 100)
    bar = "█" * (percent // 10)
    print(f"\r[{bar:<10}] {percent}%", end="")


# ==============================
# MENU PRINCIPAL
# ==============================

def main():

    check_dependencies()

    while True:
        print("""
================================
Système de Chiffrement - TP3
================================
1. Générer une nouvelle clé
2. Envoyer une clé via SFTP
3. Chiffrer des fichiers/dossiers
4. Vérifier les dépendances
5. Déchiffrer des fichiers/dossiers
6. Quitter
""")

        choice = input("Choix : ")

        if choice == "1":
            algo = input("Algorithme (AES/PBKDF2) : ")
            length = int(input("Longueur (128/192/256) : "))
            key = generate_key(algo, length)
            save_key(key, algo, length)

        elif choice == "2":
            local = input("Chemin clé locale : ")

            if not os.path.isfile(local):
                print("Fichier introuvable.")
                continue

            send_sftp(local)

        elif choice == "3":
            key_file = input("Fichier clé JSON : ")

            with open(key_file) as f:
                data = json.load(f)
                key = base64.b64decode(data["key"])

            files = select_directories()
            total = len(files)

            if total == 0:
                print("Aucun fichier sélectionné.")
                continue

            for i, file in enumerate(files, 1):
                encrypt_file(file, key)
                progress_bar(i, total)

            print("\n✓ Chiffrement terminé.")

        elif choice == "5":
            key_file = input("Fichier clé JSON : ")

            with open(key_file) as f:
                data = json.load(f)
                key = base64.b64decode(data["key"])

            files = select_directories()
            total = len(files)

            if total == 0:
                print("Aucun fichier sélectionné.")
                continue

            for i, file in enumerate(files, 1):
                decrypt_file(file, key)
                progress_bar(i, total)

            print("\n✓ Déchiffrement terminé.")

        elif choice == "4":
            check_dependencies()

        elif choice == "6":
            break


if __name__ == "__main__":
    main()
