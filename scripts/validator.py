import re
import pandas as pd
import requests
import io

class PRValidator:
    def __init__(self, sheet_url, webhook_url, phone_number):
        self.sheet_url = sheet_url
        self.webhook_url = webhook_url
        self.phone_number = phone_number

    def extract_code(self, title):
        """Busca el patrón [CODE:XXXXX] en el título."""
        match = re.search(r'\[CODE:\s*([a-zA-Z0-9]+)\s*\]', title)
        if match:
            return match.group(1)
        return None

    def get_csv_data(self):
        """Descarga el CSV de Google Sheets."""
        try:
            response = requests.get(self.sheet_url)
            response.raise_for_status()
            return pd.read_csv(io.StringIO(response.text))
        except Exception as e:
            raise RuntimeError(f"Error descargando CSV: {e}")

    def validate_code(self, code, df):
        """Verifica si el código existe."""
        if 'code' not in df.columns or 'name' not in df.columns:
            raise ValueError("El CSV debe tener columnas 'code' y 'name'")
        
        df['code'] = df['code'].astype(str).str.strip()
        row = df[df['code'] == str(code)]
        
        if not row.empty:
            return True, row.iloc[0]['name']
        return False, None

    def send_webhook(self, name):
        """Envía el POST con el formato específico de chat."""
        if not self.webhook_url:
            print("⚠ Warning: WEBHOOK_URL no configurada.")
            return

        if not self.phone_number:
            print("⚠ Warning: PHONE_NUMBER no configurado.")
            return
            
        try:
            # Construimos el payload exacto solicitado
            payload = {
                "chatId": f"{self.phone_number}@c.us", # Agregamos el sufijo @c.us
                "reply_to": None,
                "text": f"{name} Asistió",
                "linkPreview": True,
                "linkPreviewHighQuality": False,
                "session": "default"
            }

            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }

            requests.post(
                self.webhook_url + '/api/sessions/default/start', 
                headers=headers, 
                timeout=10
            )
            

            requests.post(
                self.webhook_url + '/api/sendText', 
                json=payload, 
                headers=headers, 
                timeout=10
            )
            print(f"📡 Mensaje enviado a {self.phone_number}: {name} Asistió")
        except Exception as e:
            print(f"⚠ Error enviando webhook: {e}")