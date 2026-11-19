#!/usr/bin/env python3
"""
preparar_fuentes.py
-------------------
Genera y particiona una muestra representativa de datos para el proyecto Saber 11,
simulando la distribución en las 3 fuentes heterogéneas:
1. RDS MariaDB:
   - data/rds/dim_municipios.csv
   - data/rds/dim_colegios.csv
   - data/rds/resultados_2019_2020.csv
2. EC2 Archivos CSV:
   - data/ec2/saber11_2021.csv
   - data/ec2/saber11_2022.csv
3. URL / API (JSON):
   - data/api/saber11_2023.json
   - data/api/divipola_municipios.json
"""

import os
import csv
import json
import random
import argparse
from datetime import datetime, timedelta

# Municipios y Departamentos base (DIVIPOLA muestra representativa)
MUNICIPIOS_BASE = [
    {"cod_depto": "11", "nom_depto": "BOGOTA", "cod_municipio": "11001", "nom_municipio": "BOGOTA D.C.", "lat": 4.6097, "lon": -74.0817},
    {"cod_depto": "05", "nom_depto": "ANTIOQUIA", "cod_municipio": "05001", "nom_municipio": "MEDELLIN", "lat": 6.2442, "lon": -75.5812},
    {"cod_depto": "05", "nom_depto": "ANTIOQUIA", "cod_municipio": "05088", "nom_municipio": "BELLO", "lat": 6.3370, "lon": -75.5579},
    {"cod_depto": "76", "nom_depto": "VALLE", "cod_municipio": "76001", "nom_municipio": "CALI", "lat": 3.4516, "lon": -76.5320},
    {"cod_depto": "76", "nom_depto": "VALLE", "cod_municipio": "76111", "nom_municipio": "BUGA", "lat": 3.9009, "lon": -76.2978},
    {"cod_depto": "08", "nom_depto": "ATLANTICO", "cod_municipio": "08001", "nom_municipio": "BARRANQUILLA", "lat": 10.9685, "lon": -74.7813},
    {"cod_depto": "68", "nom_depto": "SANTANDER", "cod_municipio": "68001", "nom_municipio": "BUCARAMANGA", "lat": 7.1254, "lon": -73.1198},
    {"cod_depto": "68", "nom_depto": "SANTANDER", "cod_municipio": "68276", "nom_municipio": "FLORIDABLANCA", "lat": 7.0622, "lon": -73.0864},
    {"cod_depto": "13", "nom_depto": "BOLIVAR", "cod_municipio": "13001", "nom_municipio": "CARTAGENA", "lat": 10.3910, "lon": -75.4794},
    {"cod_depto": "25", "nom_depto": "CUNDINAMARCA", "cod_municipio": "25754", "nom_municipio": "SOACHA", "lat": 4.5804, "lon": -74.2179},
    {"cod_depto": "25", "nom_depto": "CUNDINAMARCA", "cod_municipio": "25175", "nom_municipio": "CHIA", "lat": 4.8608, "lon": -74.0573},
    {"cod_depto": "52", "nom_depto": "PASTO", "cod_municipio": "52001", "nom_municipio": "PASTO", "lat": 1.2136, "lon": -77.2811},
    {"cod_depto": "17", "nom_depto": "CALDAS", "cod_municipio": "17001", "nom_municipio": "MANIZALES", "lat": 5.0689, "lon": -75.5174},
    {"cod_depto": "66", "nom_depto": "RISARALDA", "cod_municipio": "66001", "nom_municipio": "PEREIRA", "lat": 4.8133, "lon": -75.6961},
    {"cod_depto": "27", "nom_depto": "CHOCO", "cod_municipio": "27001", "nom_municipio": "QUIBDO", "lat": 5.6947, "lon": -76.6611},
    {"cod_depto": "44", "nom_depto": "LA GUAJIRA", "cod_municipio": "44001", "nom_municipio": "RIOHACHA", "lat": 11.5444, "lon": -72.9072}
]

ESTRATOS = ["Estrato 1", "Estrato 2", "Estrato 3", "Estrato 4", "Estrato 5", "Estrato 6", "Sin Estrato"]
ESTRATOS_PESOS = [0.28, 0.35, 0.22, 0.08, 0.04, 0.02, 0.01]

NIVELES_PADRES = [
    "Primaria incompleta", "Primaria completa",
    "Secundaria (Bachillerato) incompleta", "Secundaria (Bachillerato) completa",
    "Técnica o tecnológica completa", "Educación profesional completa", "Postgrado"
]

def generar_colegios(n_colegios=200):
    colegios = []
    tipos = ["INSTITUTO TECNICO", "COLEGIO", "LICEO", "INSTITUCION EDUCATIVA", "GIMNASIO"]
    nombres_prop = ["SAN CARLOS", "SAN JOSE", "BOLIVAR", "NACIONAL", "NUESTRA SEÑORA", "COLOMBIANO", "DEL SUR", "DEL NORTE", "MODERNO", "DEPARTAMENTAL"]
    
    for i in range(1, n_colegios + 1):
        muni = random.choice(MUNICIPIOS_BASE)
        naturaleza = "OFICIAL" if random.random() < 0.70 else "NO OFICIAL"
        bilingue = "S" if (naturaleza == "NO OFICIAL" and random.random() < 0.15) else "N"
        area = "URBANO" if random.random() < 0.85 else "RURAL"
        calendario = "A" if random.random() < 0.92 else "B"
        jornada = random.choice(["MAÑANA", "TARDE", "COMPLETA", "UNICA", "SABATINA"])
        genero = "MIXTO" if random.random() < 0.95 else ("FEMENINO" if random.random() < 0.5 else "MASCULINO")
        caracter = random.choice(["ACADEMICO", "TECNICO", "TECNICO/ACADEMICO"])
        
        nombre = f"{random.choice(tipos)} {random.choice(nombres_prop)} #{i}"
        dane = 111000000000 + i * 137
        icfes = 100000 + i
        
        colegios.append({
            "cole_cod_dane_establecimiento": dane,
            "cole_codigo_icfes": icfes,
            "cole_nombre_establecimiento": nombre,
            "cole_genero": genero,
            "cole_naturaleza": naturaleza,
            "cole_calendario": calendario,
            "cole_bilingue": bilingue,
            "cole_caracter": caracter,
            "cole_area_ubicacion": area,
            "cole_jornada": jornada,
            "cole_cod_mcpio_ubicacion": muni["cod_municipio"],
            "cole_mcpio_ubicacion": muni["nom_municipio"],
            "cole_cod_depto_ubicacion": muni["cod_depto"],
            "cole_depto_ubicacion": muni["nom_depto"]
        })
    return colegios

def calcular_desempeno_ingles(puntaje):
    if puntaje < 48:
        return "A-"
    elif puntaje < 58:
        return "A1"
    elif puntaje < 68:
        return "A2"
    elif puntaje < 80:
        return "B1"
    else:
        return "B+"

def simular_estudiante(consecutivo_num, periodo, colegios):
    cole = random.choice(colegios)
    muni_reside = random.choice(MUNICIPIOS_BASE)
    
    genero = "F" if random.random() < 0.52 else "M"
    tipo_doc = "TI" if random.random() < 0.85 else "CC"
    
    # Simular fecha nacimiento (16-19 años)
    anio_periodo = int(str(periodo)[:4])
    edad = random.randint(16, 19)
    anio_nac = anio_periodo - edad
    mes_nac = random.randint(1, 12)
    dia_nac = random.randint(1, 28)
    fecha_nac = f"{dia_nac:02d}/{mes_nac:02d}/{anio_nac}"
    
    estrato = random.choices(ESTRATOS, weights=ESTRATOS_PESOS)[0]
    estrato_num = 1 if "1" in estrato else (2 if "2" in estrato else (3 if "3" in estrato else (4 if "4" in estrato else (5 if "5" in estrato else 6))))
    
    educ_padre = random.choice(NIVELES_PADRES)
    educ_madre = random.choice(NIVELES_PADRES)
    
    # Probabilidad de internet / computador correlacionada con estrato
    prob_tic = min(0.95, 0.40 + estrato_num * 0.10)
    tiene_internet = "Si" if random.random() < prob_tic else "No"
    tiene_compu = "Si" if random.random() < (prob_tic - 0.05) else "No"
    
    # Modelo generativo de puntajes con efecto de colegio y estrato
    base_mu = 48.0
    if cole["cole_naturaleza"] == "NO OFICIAL":
        base_mu += 7.0
    if cole["cole_bilingue"] == "S":
        base_mu += 10.0
    if tiene_internet == "Si" and tiene_compu == "Si":
        base_mu += 4.0
    base_mu += (estrato_num - 1) * 1.5
    
    # Puntajes 0 - 100 con distribución acotada
    p_lc = max(0, min(100, int(random.gauss(base_mu + 2, 10))))
    p_mat = max(0, min(100, int(random.gauss(base_mu, 11))))
    p_cn = max(0, min(100, int(random.gauss(base_mu - 1, 10))))
    p_sc = max(0, min(100, int(random.gauss(base_mu - 1, 11))))
    
    mu_ing = base_mu + (15 if cole["cole_bilingue"] == "S" else 0)
    p_ing = max(0, min(100, int(random.gauss(mu_ing, 12))))
    des_ing = calcular_desempeno_ingles(p_ing)
    
    # Puntaje global (0 a 500): Ponderado ICFES: 3*LC + 3*Mat + 3*CN + 3*SC + 1*Ing factor scale
    # Aproximación oficial ICFES ponderada
    punt_global = int(((p_lc * 3 + p_mat * 3 + p_cn * 3 + p_sc * 3 + p_ing * 1) / 13) * 5)
    percentil = max(1, min(100, int(punt_global / 5)))
    
    return {
        "periodo": periodo,
        "estu_consecutivo": f"SB11{periodo}{consecutivo_num:06d}",
        "estu_tipodocumento": tipo_doc,
        "estu_estudiante": "ESTUDIANTE",
        "estu_genero": genero,
        "estu_fechanacimiento": fecha_nac,
        "estu_pais_reside": "COLOMBIA",
        "estu_depto_reside": muni_reside["nom_depto"],
        "estu_cod_reside_depto": muni_reside["cod_depto"],
        "estu_mcpio_reside": muni_reside["nom_municipio"],
        "estu_cod_reside_mcpio": muni_reside["cod_municipio"],
        "fami_estratovivienda": estrato,
        "fami_educacionpadre": educ_padre,
        "fami_educacionmadre": educ_madre,
        "fami_tieneinternet": tiene_internet,
        "fami_tienecomputador": tiene_compu,
        "cole_codigo_icfes": cole["cole_codigo_icfes"],
        "cole_cod_dane_establecimiento": cole["cole_cod_dane_establecimiento"],
        "cole_nombre_establecimiento": cole["cole_nombre_establecimiento"],
        "cole_genero": cole["cole_genero"],
        "cole_naturaleza": cole["cole_naturaleza"],
        "cole_calendario": cole["cole_calendario"],
        "cole_bilingue": cole["cole_bilingue"],
        "cole_caracter": cole["cole_caracter"],
        "cole_area_ubicacion": cole["cole_area_ubicacion"],
        "cole_jornada": cole["cole_jornada"],
        "cole_cod_mcpio_ubicacion": cole["cole_cod_mcpio_ubicacion"],
        "cole_mcpio_ubicacion": cole["cole_mcpio_ubicacion"],
        "cole_cod_depto_ubicacion": cole["cole_cod_depto_ubicacion"],
        "cole_depto_ubicacion": cole["cole_depto_ubicacion"],
        "punt_lectura_critica": p_lc,
        "punt_matematicas": p_mat,
        "punt_c_naturales": p_cn,
        "punt_sociales_ciudadanas": p_sc,
        "punt_ingles": p_ing,
        "desemp_ingles": des_ing,
        "punt_global": punt_global,
        "percentil_global": percentil
    }

def main():
    parser = argparse.ArgumentParser(description="Prepara y genera datos federados de Saber 11")
    parser.add_argument("--total-records", type=int, default=100000, help="Total de registros de estudiantes")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    rds_dir = os.path.join(data_dir, "rds")
    ec2_dir = os.path.join(data_dir, "ec2")
    api_dir = os.path.join(data_dir, "api")

    for d in [rds_dir, ec2_dir, api_dir]:
        os.makedirs(d, exist_ok=True)

    print("Generando dimensiones maestras...")
    colegios = generar_colegios(n_colegios=250)

    # 1. RDS Maestras
    with open(os.path.join(rds_dir, "dim_municipios.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cod_municipio", "nom_municipio", "cod_depto", "nom_depto"])
        writer.writeheader()
        for m in MUNICIPIOS_BASE:
            writer.writerow({k: m[k] for k in ["cod_municipio", "nom_municipio", "cod_depto", "nom_depto"]})

    with open(os.path.join(rds_dir, "dim_colegios.csv"), "w", newline="", encoding="utf-8") as f:
        fields = [
            "cole_cod_dane_establecimiento", "cole_codigo_icfes", "cole_nombre_establecimiento",
            "cole_genero", "cole_naturaleza", "cole_calendario", "cole_bilingue", "cole_caracter",
            "cole_area_ubicacion", "cole_jornada", "cole_cod_mcpio_ubicacion"
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in colegios:
            writer.writerow({k: c[k] for k in fields})

    # 2. Complementario DIVIPOLA (JSON para API)
    with open(os.path.join(api_dir, "divipola_municipios.json"), "w", encoding="utf-8") as f:
        json.dump(MUNICIPIOS_BASE, f, ensure_ascii=False, indent=2)

    # 3. Distribución de registros por periodo:
    # 20194, 20204 -> RDS (40%)
    # 20214, 20224 -> EC2 (40%)
    # 20234        -> API (20%)
    n_total = args.total_records
    n_rds = int(n_total * 0.40)
    n_ec2 = int(n_total * 0.40)
    n_api = n_total - n_rds - n_ec2

    print(f"Simulando {n_total} registros: RDS={n_rds}, EC2={n_ec2}, API={n_api}")

    # RDS 2019-2020
    records_rds = []
    for i in range(1, n_rds + 1):
        p = 20194 if i <= (n_rds // 2) else 20204
        records_rds.append(simular_estudiante(i, p, colegios))

    with open(os.path.join(rds_dir, "resultados_2019_2020.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records_rds[0].keys()))
        writer.writeheader()
        writer.writerows(records_rds)

    # EC2 2021-2022
    records_2021 = []
    records_2022 = []
    for i in range(1, n_ec2 + 1):
        if i <= (n_ec2 // 2):
            records_2021.append(simular_estudiante(n_rds + i, 20214, colegios))
        else:
            records_2022.append(simular_estudiante(n_rds + i, 20224, colegios))

    with open(os.path.join(ec2_dir, "saber11_2021.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records_2021[0].keys()))
        writer.writeheader()
        writer.writerows(records_2021)

    with open(os.path.join(ec2_dir, "saber11_2022.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records_2022[0].keys()))
        writer.writeheader()
        writer.writerows(records_2022)

    # API 2023
    records_2023 = []
    for i in range(1, n_api + 1):
        records_2023.append(simular_estudiante(n_rds + n_ec2 + i, 20234, colegios))

    with open(os.path.join(api_dir, "saber11_2023.json"), "w", encoding="utf-8") as f:
        json.dump(records_2023, f, ensure_ascii=False)

    print("Datos federados generados exitosamente en 02-fuentes-datos/data/:")
    print(f" - RDS: {len(records_rds)} filas en resultados_2019_2020.csv + dimensiones")
    print(f" - EC2: {len(records_2021)} filas en saber11_2021.csv y {len(records_2022)} en saber11_2022.csv")
    print(f" - API: {len(records_2023)} registros en saber11_2023.json + divipola_municipios.json")

if __name__ == "__main__":
    main()
