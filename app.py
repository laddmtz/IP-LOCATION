from flask import Flask, request, jsonify
import ipaddress
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def ping(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(["ping", param, "1", str(ip)],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            return str(ip)
    except:
        return None

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    cidr = data.get("network")
    resultat = []

    try:
        reseau = ipaddress.ip_network(cidr, strict=False)
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(ping, ip): ip for ip in reseau.hosts()}
            for future in futures:
                ip_result = future.result()
                if ip_result:
                    resultat.append(ip_result)
        return "\n".join(resultat)
    except Exception as e:
        return f"Erreur : {e}", 400

if __name__ == '__main__':
    app.run(debug=True)
