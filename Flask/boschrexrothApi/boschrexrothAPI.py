from dataclasses import dataclass
import requests
from requests.exceptions import RequestException
from urllib.parse import quote
from datetime import datetime, timedelta
import urllib3

@dataclass
class BoschrexrothAPIConfig:
    """Configuration pour l'API Boschrexroth"""
    base_url: str = "https://localhost"
    username: str = "boschrexroth"
    password: str = "boschrexroth"
    verify_ssl: bool = False

class BoschrexrothAPI:
    def __init__(self, config: BoschrexrothAPIConfig = None):
        self.config = config or BoschrexrothAPIConfig()
        self.session = requests.Session()
        self.session.verify = self.config.verify_ssl
        self.token = None
        self.token_expiry = None
        self.token_lifetime = timedelta(hours=1)

    def is_token_valid(self):
        """Vérifie si le token actuel est valide"""
        return (
            self.token is not None and 
            self.token_expiry is not None and 
            datetime.now() < self.token_expiry
        )

    def ensure_valid_token(self):
        """S'assure qu'un token valide est disponible"""
        if not self.is_token_valid():
            self.get_auth_token()

    def _get_auth_headers(self):
        """
        Obtient les en-têtes d'authentification avec un token valide.
        
        Returns:
            dict: Les en-têtes d'authentification
        """
        self.ensure_valid_token()
        return {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def get_auth_token(self, username=None, password=None):
        """
        Obtient un token d'authentification auprès du serveur.
        
        Args:
            username (str, optional): Nom d'utilisateur pour l'authentification
            password (str, optional): Mot de passe pour l'authentification
            
        Returns:
            dict: Données de réponse du serveur
            
        Raises:
            Exception: Si la requête échoue
        """
        try:
            username = username or self.config.username
            password = password or self.config.password
            
            endpoint = f"{self.config.base_url}/identity-manager/api/v2/auth/token"
            
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'name': username,
                'password': password
            }
            
            response = self.session.post(
                url=endpoint,
                headers=headers,
                json=payload,
                params={'dryrun': 'false'}
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            if 'access_token' in response_data:
                self.token = response_data['access_token']
                self.token_expiry = datetime.now() + self.token_lifetime
            
            return response_data
            
        except RequestException as e:
            raise Exception(f"Erreur lors de la requête d'authentification: {str(e)}")

    def get_drive_name(self):
        """
        Récupère les noms des drives disponibles.
        
        Returns:
            list: Liste des drives disponibles
            
        Raises:
            Exception: Si la requête échoue
        """
        self.ensure_valid_token()
        try:
            path = quote("fieldbuses/ethercat/master/instances/ethercatmaster/realtime_data/input/data")
            endpoint = f"{self.config.base_url}/automation/api/v2/nodes/{path}"
            
            headers = self._get_auth_headers()
            
            response = self.session.get(
                url=endpoint,
                headers=headers,
                params={'type': 'browse'}
            )
            
            response.raise_for_status()
            return response.json()['value']
            
        except RequestException as e:
            raise Exception(f"Erreur lors de la récupération des données EtherCAT: {str(e)}")

    def set_drive_value(self, value):
        """
        Définit la valeur d'un drive.
        
        Args:
            value (str): Valeur à définir
            
        Returns:
            dict: Réponse du serveur
            
        Raises:
            Exception: Si la requête échoue
        """
        self.ensure_valid_token()
        try:
            path = quote("sdk/cpp/datalayer/provider/simple/string-Drive")
            endpoint = f"{self.config.base_url}/automation/api/v2/nodes/{path}"
            
            headers = self._get_auth_headers()
            headers['Content-Type'] = 'application/json'
            
            payload = {
                "type": "string",
                "value": value
            }
            
            response = self.session.put(
                url=endpoint,
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            return response.json() if response.text else {"status": "success"}
                
        except RequestException as e:
            raise Exception(f"Erreur lors de la définition de la valeur du drive: {str(e)}")

    def get_data_mouvement(self, data_type=None):
        """
        Récupère les données de mouvement.
        
        Args:
            data_type (str, optional): Type de données à récupérer (couple, position, vitesse, temps)
            
        Returns:
            dict: Données de mouvement
            
        Raises:
            Exception: Si la requête échoue
        """
        self.ensure_valid_token()
        paths = {
            'couple': "sdk/cpp/datalayer/provider/simple/array-of-float32-Couple",
            'position': "sdk/cpp/datalayer/provider/simple/array-of-float32-Postion", 
            'vitesse': "sdk/cpp/datalayer/provider/simple/array-of-float32-Vitesse",
            'temps': "sdk/cpp/datalayer/provider/simple/array-of-int32-Time"
        }

        if data_type and data_type.lower() in paths:
            paths = {data_type.lower(): paths[data_type.lower()]}

        try:
            headers = self._get_auth_headers()

            results = {}
            for data_name, path in paths.items():
                endpoint = f"{self.config.base_url}/automation/api/v2/nodes/{quote(path)}"
                response = self.session.get(
                    url=endpoint,
                    headers=headers
                )
                response.raise_for_status()
                results[data_name] = response.json()['value']

            return results[data_type.lower()] if data_type else results
                
        except RequestException as e:
            raise Exception(f"Erreur lors de la récupération des données: {str(e)}")

    def read_datalayer(self, node_path, query_params=None):
        self.ensure_valid_token()
        try:
            url = f"{self.config.base_url}/automation/api/v2/nodes/{node_path}"
            headers = self._get_auth_headers()
            print(f"En-têtes de la requête: {headers}")
            
            response = self.session.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise Exception(f"Erreur lors de la lecture du nœud {node_path}: {str(e)}")
            
    def write_datalayer(self, node_path, data=None):
        """
        Écrire des données dans le datalayer.
        
        Args:
            node_path (str): Chemin du nœud où écrire
            data (dict, optional): Données à écrire. Peut être None pour les endpoints qui n'exigent pas de corps.
        
        Returns:
            dict: Réponse de l'opération d'écriture
            
        Raises:
            Exception: Si la requête échoue
        """
        self.ensure_valid_token()
        try:
            url = f"{self.config.base_url}/automation/api/v2/nodes/{node_path}"
            headers = self._get_auth_headers()
            
            if data is not None:
                headers['Content-Type'] = 'application/json'
                response = self.session.put(url, headers=headers, json=data)
            else:
                # Requête sans corps
                response = self.session.put(url, headers=headers)
                
            response.raise_for_status()
            return response.json() if response.content else {"status": "success"}
        except RequestException as e:
            raise Exception(f"Erreur lors de l'écriture dans le nœud {node_path}: {str(e)}")