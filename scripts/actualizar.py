"""Trae los llamados del portal Educacionales y genera data.json (sin datos de personas)."""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone

URL = "https://educacionales.mendoza.edu.ar/data?_=" + str(int(time.time() * 1000))
BASE = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "es-AR,es;q=0.9",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://educacionales.mendoza.edu.ar/",
}
# Primero nos identificamos con transparencia; si el portal no responde, probamos con los encabezados que usa un navegador.
PERFILES = [
    ("transparente", {**BASE, "User-Agent": "Mozilla/5.0 (compatible; LlamadoATiempo/1.0; +https://julieta548.github.io/llamados-a-tiempo/)"}),
    ("navegador", {**BASE, "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8",
                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
                   "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin"}),
]

def traer():
    for nombre, headers in PERFILES:
        try:
            r = urllib.request.urlopen(urllib.request.Request(URL, headers=headers), timeout=60)
            cuerpo = r.read().decode("utf-8", "replace")
            datos = json.loads(cuerpo)
            print(f"Perfil {nombre}: OK")
            return datos
        except ValueError:
            print(f"Perfil {nombre}: no es JSON. URL final: {r.geturl()} | Inicio: {cuerpo[:120]!r}")
        except Exception as e:
            print(f"Perfil {nombre}: error {e}")
    raise RuntimeError("El portal no entregó datos en JSON")

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
