import os
import re
from typing import Dict, Optional, Tuple
from pathlib import Path

class EnvManager:
    def __init__(self, env_file_path: str = ".env"):
        self.env_file_path = Path(env_file_path)
        self.ensure_env_file_exists()

    def ensure_env_file_exists(self):
        """Crée le fichier .env s'il n'existe pas"""
        if not self.env_file_path.exists():
            self.env_file_path.touch()

    def read_env_file(self) -> Dict[str, str]:
        """Lit toutes les variables du fichier .env"""
        env_vars = {}
        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except FileNotFoundError:
            pass
        return env_vars

    def write_env_file(self, env_vars: Dict[str, str]):
        """Écrit toutes les variables dans le fichier .env"""
        with open(self.env_file_path, 'w', encoding='utf-8') as file:
            for key, value in env_vars.items():
                file.write(f"{key}={value}\n")

    def get_variable(self, key: str) -> Optional[str]:
        """Récupère une variable spécifique"""
        env_vars = self.read_env_file()
        return env_vars.get(key)

    def set_variable(self, key: str, value: str) -> bool:
        """Définit une variable d'environnement"""
        try:
            env_vars = self.read_env_file()
            env_vars[key] = value
            self.write_env_file(env_vars)
            # Met aussi à jour la variable d'environnement actuelle
            os.environ[key] = value
            return True
        except Exception:
            return False

    def set_variables(self, variables: Dict[str, str]) -> Tuple[bool, str]:
        """Définit plusieurs variables d'environnement"""
        try:
            env_vars = self.read_env_file()
            env_vars.update(variables)
            self.write_env_file(env_vars)
            # Met aussi à jour les variables d'environnement actuelles
            for key, value in variables.items():
                os.environ[key] = value
            return True, f"Successfully updated {len(variables)} variables"
        except Exception as e:
            return False, f"Error updating variables: {str(e)}"

    def delete_variable(self, key: str) -> bool:
        """Supprime une variable d'environnement"""
        try:
            env_vars = self.read_env_file()
            if key in env_vars:
                del env_vars[key]
                self.write_env_file(env_vars)
                # Supprime aussi de l'environnement actuel si elle existe
                if key in os.environ:
                    del os.environ[key]
                return True
            return False
        except Exception:
            return False

    def get_all_variables(self) -> Dict[str, str]:
        """Récupère toutes les variables d'environnement"""
        return self.read_env_file()

# Instance globale
env_manager = EnvManager()
