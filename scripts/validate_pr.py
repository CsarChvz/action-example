import os
import sys
from validator import PRValidator

import uuid

def set_action_output(name, value):
    """Escribe outputs de forma segura para strings multilínea."""
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        delimiter = f"ghadelimiter_{uuid.uuid4()}"
        print(f"{name}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)

        
def main():
    # 1. Variables de entorno
    pr_title = os.getenv('PR_TITLE', '')
    sheet_url = os.getenv('GOOGLE_SHEET_URL')
    webhook_url = os.getenv('WEBHOOK_URL')
    phone_number = os.getenv('PHONE_NUMBER') # Nuevo

    if not sheet_url:
        print("❌ Error: GOOGLE_SHEET_URL faltante.")
        sys.exit(1)

    # Pasamos el teléfono al validador
    validator = PRValidator(sheet_url, webhook_url, phone_number)

    # 2. Extraer Código
    code = validator.extract_code(pr_title)
    if not code:
        msg = "❌ **Código Inválido**: No se encontró `[CODE:XXXXX]`."
        set_action_output('message', msg)
        set_action_output('success', 'false')
        sys.exit(0)

    print(f"🔍 Código extraído: {code}")

    # 3. Validar y Notificar
    try:
        df = validator.get_csv_data()
        is_valid, name = validator.validate_code(code, df)

        if is_valid:
            validator.send_webhook(name) # Ahora usará el nuevo formato
            msg = f"✅ **Código validado correctamente**\n\nIdentificado: `{name}`"
            set_action_output('message', msg)
            set_action_output('success', 'true')
        else:
            msg = f"❌ **Código Inválido**: `{code}` no existe."
            set_action_output('message', msg)
            set_action_output('success', 'false')

    except Exception as e:
        msg = f"⚠ **Error del sistema**: {str(e)}"
        set_action_output('message', msg)
        set_action_output('success', 'false')

if __name__ == "__main__":
    main()