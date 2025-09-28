"""
Startskript for Plastic Plate Heat Exchanger Simulator
======================================================

Dette skriptet starter web-simulatoren og åpner nettleseren automatisk.
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading

def check_flask_installed():
    """Sjekk om Flask er installert."""
    try:
        import flask
        return True
    except ImportError:
        return False

def install_requirements():
    """Installer requirements hvis nødvendig."""
    print("📦 Installerer avhengigheter...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Avhengigheter installert!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Feil ved installasjon av avhengigheter")
        return False

def open_browser_delayed():
    """Åpne nettleser etter kort pause."""
    time.sleep(2)  # Vent litt for at serveren skal starte
    webbrowser.open('http://localhost:5000')

def main():
    """Hovedfunksjon for å starte simulatoren."""
    print("🔥 Plastic Plate Heat Exchanger Simulator")
    print("=" * 45)
    
    # Sjekk og installer avhengigheter
    if not check_flask_installed():
        print("⚠️  Flask ikke funnet. Installerer...")
        if not install_requirements():
            print("❌ Kunne ikke installere avhengigheter. Installér manuelt:")
            print("   pip install -r requirements.txt")
            return
    
    print("🚀 Starter web-simulator...")
    
    # Start nettleser i bakgrunnen
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("🌐 Simulator tilgjengelig på: http://localhost:5000")
    print("📊 Rapporter lagres i: generated_reports/")
    print("⏹️  Trykk Ctrl+C for å stoppe simulatoren")
    print()
    
    try:
        # Import og start Flask app
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Simulator stoppet")
    except Exception as e:
        print(f"❌ Feil ved oppstart: {e}")
        print("\nPrøv å starte manuelt med:")
        print("   python app.py")

if __name__ == '__main__':
    main()