"""Trae los llamados del portal Educacionales y genera data.json (sin datos de personas)."""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone

URL = "https://educacionales.mendoza.edu.ar/data?_=" + str(int(time.time() * 1000))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://educacionales.mendoza.edu.ar/",
}

def traer():
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def iso(s):
    m = re.match(r"(\d\d)/(\d\d)/(\d\d) (\d\d):(\d\d)", s)
    return f"20{m[3]}-{m[2]}-{m[1]}T{m[4]}:{m[5]}:00-03:00" if m else None

def fechas(r):
    txt = r.get("numero_llamado_4") or ""
    hallados = re.findall(r"(\d+\s?[a-zº°]{1,3})\s*:\s*(\d\d/\d\d/\d\d \d\d:\d\d)", txt, re.I)
    if hallados:
        return [[a.replace(" ", ""), iso(b)] for a, b in hallados]
    etiquetas = ["1er", "2do", "3er", "4to"]
    return [[etiquetas[i - 1], iso(r[f"fecha_llamado_{i}"])] for i in range(1, 5) if r.get(f"fecha_llamado_{i}")]

def limpiar(r):
    # Solo campos del llamado: escuela, cargo, horario, zona y requisitos. Nada de personas.
    t = lambda k: (r.get(k) or "").strip()
    return {
        "id": r.get("id"), "nivel": t("nivel"), "dep": t("departamento"), "loc": t("localidad"),
        "esc": t("lugar_trabajo"), "zona": t("zona"), "reg": t("regimen"), "horas": t("horas"),
        "turno": t("turno"), "mat": t("materia"), "horario": t("horario"), "tipo": t("tipo_llamado"),
        "pres": t("presentarse_en"), "prio": t("prioridad"),
        "cond": t("condiciones_adicionales")[:600], "obs": t("observaciones_adicionales")[:400],
        "f": fechas(r),
    }

def main():
    fuente = "portal"
    try:
        crudo = traer()
    except Exception as e:
        print("No se pudo leer el portal:", e)
        if os.path.exists("data_manual.json"):
            crudo, fuente = json.load(open("data_manual.json", encoding="utf-8")), "manual"
        else:
            sys.exit(1)
    filas = [limpiar(r) for r in crudo["datos"] if r.get("estado") == "Publicado"]
    filas = [f for f in filas if f["f"]]
    salida = {"actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "fuente": fuente, "total": len(filas), "llamados": filas}
    with open("data.json", "w", encoding="utf-8") as fh:
        json.dump(salida, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"OK: {len(filas)} llamados publicados (fuente: {fuente})")

if __name__ == "__main__":
    main()
