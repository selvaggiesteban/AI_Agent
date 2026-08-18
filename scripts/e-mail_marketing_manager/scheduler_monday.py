import schedule
import time
import subprocess
import sys
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEND_SCRIPT = os.path.join(SCRIPT_DIR, "test_send_scheduled.py")

TARGET_DAY = 0  # 0=Lunes
TARGET_START_HOUR = 7
TARGET_END_HOUR = 13

def run_campaign():
    """Ejecuta la campaña de envíos."""
    print(f"\n{'='*60}")
    print(f"INICIANDO CAMPAÑA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        subprocess.run([sys.executable, SEND_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando campaña: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def check_schedule():
    """Verifica si es el día y hora correctos para ejecutar."""
    now = datetime.now()
    
    if now.weekday() == TARGET_DAY:
        if TARGET_START_HOUR <= now.hour < TARGET_END_HOUR:
            print(f"[{now.strftime('%H:%M:%S')}] Lunes detectado, iniciando campaña...")
            run_campaign()
        else:
            print(f"[{now.strftime('%H:%M:%S')}] Fuera de horario ({TARGET_START_HOUR}:00-{TARGET_END_HOUR}:00)")
    else:
        print(f"[{now.strftime('%H:%M:%S')}] No es lunes (día actual: {now.weekday()})")

def main():
    """Configura el scheduler para ejecutar la campaña."""
    print("=" * 60)
    print("SCHEDULER DE CAMPAÑAS GMAIL")
    print(f"Fecha objetivo: Lunes {TARGET_DAY}")
    print(f"Horario: {TARGET_START_HOUR}:00 - {TARGET_END_HOUR}:00")
    print(f"Script de envío: {SEND_SCRIPT}")
    print("=" * 60)
    print("\nEsperando momento de ejecución...")
    print("Presiona Ctrl+C para detener\n")
    
    # Programar verificación cada minuto
    schedule.every(1).minutes.do(check_schedule)
    
    # Verificar inmediatamente al iniciar
    check_schedule()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\nScheduler detenido por el usuario")

if __name__ == "__main__":
    main()
