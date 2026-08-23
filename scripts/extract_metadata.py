#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para extraer metadatos de los archivos Markdown de la base de conocimiento de SeniorVital.

Uso:
    python extract_metadata.py [--input-dir DIR] [--output-file FILE]

Si no se especifican argumentos, se usa:
    --input-dir  E:\SeniorVital-master\data\knowledge_base
    --output-file E:\SeniorVital-master\data\processed\document_metadata.json
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# ============================================================================
# MAPEO MANUAL DE METADATOS (basado en el documento de estructura)
# ============================================================================
# Cada entrada asigna: macrodominio, agente, nivel funcional y fuente.
# Los nombres de archivo deben coincidir exactamente con los del sistema.
KNOWN_METADATA: Dict[str, Dict[str, str]] = {
    # Macrodominio A – Fundamentos fisiológicos y patologías
    "Sarcopenia y dinapenia.md": {
        "macrodominio": "A",
        "agente": "Physio-Evaluator",
        "nivel": "Todos",
        "fuente": "EWGSOP2"
    },
    "Movilidad articular en adultos mayores + ejercicios - ESHI.md": {
        "macrodominio": "A",
        "agente": "Physio-Evaluator",
        "nivel": "Frágil, Activo",
        "fuente": "ESHI"
    },
    "Cómo frenar la osteoporosis 8 claves basadas en la evidencia - ESHI.md": {
        "macrodominio": "A",
        "agente": "Physio-Evaluator",
        "nivel": "Frágil, Activo",
        "fuente": "ESHI"
    },
    "La diabetes.md": {
        "macrodominio": "A",
        "agente": "Physio-Evaluator",
        "nivel": "Todos",
        "fuente": "OMS"
    },

    # Macrodominio B – Taxonomía del ejercicio
    "Mejores ejercicios de fuerza para mayores de 60 años - Guía.md": {
        "macrodominio": "B",
        "agente": "Exercise Architect",
        "nivel": "Activo, Muy activo",
        "fuente": "Guía práctica"
    },
    "Los tres tipos de ejercicio que pueden mejorar su salud y capacidad física.md": {
        "macrodominio": "B",
        "agente": "Exercise Architect",
        "nivel": "Activo",
        "fuente": "ACSM"
    },
    "guia-ejercicio-mayores-segg.md": {
        "macrodominio": "B",
        "agente": "Exercise Architect",
        "nivel": "Todos",
        "fuente": "SEGG"
    },
    "Entrenamiento en adultos mayores - guía completa - ESHI.md": {
        "macrodominio": "B",
        "agente": "Exercise Architect",
        "nivel": "Todos",
        "fuente": "ESHI, OMS"
    },

    # Macrodominio C – Contexto y entorno (Latinoamérica)
    "Manual_ejercicio_persona_mayor_domicilio2.md": {
        "macrodominio": "C",
        "agente": "Context-Adaptor",
        "nivel": "Frágil, Activo",
        "fuente": "Manual práctico"
    },
    "Exercising Outdoors_ Safety Tips for Older Adults.md": {
        "macrodominio": "C",
        "agente": "Context-Adaptor",
        "nivel": "Todos",
        "fuente": "Guía de seguridad"
    },
    "Tips for Getting and Staying Active as You Age.md": {
        "macrodominio": "C",
        "agente": "Context-Adaptor",
        "nivel": "Todos",
        "fuente": "NIH (inferido)"
    },

    # Macrodominio D – Comorbilidades y seguridad clínica
    "Hacer ejercicio con enfermedades crónicas.md": {
        "macrodominio": "D",
        "agente": "Safety Guardian",
        "nivel": "Todos",
        "fuente": "Guía clínica"
    },

    # Macrodominio E – Nutrición y metabolismo
    "Alimentación saludable para personas mayores.md": {
        "macrodominio": "E",
        "agente": "Nutri-Buddy",
        "nivel": "Todos",
        "fuente": "USDA, HHS, DASH"
    },
    "WEB-GUIA-MAYORES-version-publicacion.md": {
        "macrodominio": "E",   # También contiene secciones cognitivas (F), pero se asigna a E
        "agente": "Nutri-Buddy",
        "nivel": "Todos",
        "fuente": "Guía integral"
    },

    # Macrodominio F – Estimulación cognitiva y bienestar emocional
    "Gimnasia para mayores guía oficial para una vida activa y feliz.md": {
        "macrodominio": "F",
        "agente": "Mind & Soul",
        "nivel": "Activo",
        "fuente": "Guía oficial"
    },

    # Documentos adicionales presentes en el directorio (no listados en la estructura principal)
    "Cómo pueden las personas mayores comenzar a hacer ejercicio.md": {
        "macrodominio": "B",
        "agente": "Exercise Architect",
        "nivel": "Todos",
        "fuente": "Desconocida"
    },
    "Diferencias en el entrenamiento entre hombres y mujeres lo que dice la ciencia - ESHI.md": {
        "macrodominio": "B",
        "agente": "Exercise Architect",
        "nivel": "Todos",
        "fuente": "ESHI"
    },
    "DOCUMENTO DE CONOCIMIENTO SENIORVITAL.md": {
        "macrodominio": "General",
        "agente": "General",
        "nivel": "Todos",
        "fuente": "Propio"
    },
    "Ejercicio_y_actividad_fisicasmaller-39-100.md": {
        "macrodominio": "B",
        "agente": "Exercise Architect",
        "nivel": "Todos",
        "fuente": "Desconocida"
    },
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def infer_metadata_from_filename(filename: str) -> Dict[str, str]:
    """
    Intenta inferir metadatos a partir del nombre del archivo cuando no está en el mapeo.
    """
    name_lower = filename.lower()
    if "sarcopenia" in name_lower or "osteoporosis" in name_lower or "movilidad" in name_lower:
        return {"macrodominio": "A", "agente": "Physio-Evaluator", "nivel": "Todos", "fuente": "Inferido"}
    if "fuerza" in name_lower or "ejercicio" in name_lower or "entrenamiento" in name_lower:
        return {"macrodominio": "B", "agente": "Exercise Architect", "nivel": "Todos", "fuente": "Inferido"}
    if "domicilio" in name_lower or "outdoors" in name_lower or "tips" in name_lower:
        return {"macrodominio": "C", "agente": "Context-Adaptor", "nivel": "Todos", "fuente": "Inferido"}
    if "enfermedad" in name_lower or "crónica" in name_lower or "seguridad" in name_lower:
        return {"macrodominio": "D", "agente": "Safety Guardian", "nivel": "Todos", "fuente": "Inferido"}
    if "alimentación" in name_lower or "nutrición" in name_lower:
        return {"macrodominio": "E", "agente": "Nutri-Buddy", "nivel": "Todos", "fuente": "Inferido"}
    if "memoria" in name_lower or "cognitivo" in name_lower or "gimnasia" in name_lower:
        return {"macrodominio": "F", "agente": "Mind & Soul", "nivel": "Todos", "fuente": "Inferido"}
    # Por defecto
    return {"macrodominio": "General", "agente": "General", "nivel": "Todos", "fuente": "Desconocida"}


def extract_metadata(input_dir: Path) -> List[Dict[str, str]]:
    """
    Recorre el directorio y extrae metadatos para cada archivo .md.
    """
    results = []
    md_files = sorted(input_dir.glob("*.md"))
    for filepath in md_files:
        filename = filepath.name
        # Buscar en el mapeo conocido
        if filename in KNOWN_METADATA:
            metadata = KNOWN_METADATA[filename].copy()
        else:
            # Intentar inferir
            metadata = infer_metadata_from_filename(filename)
        # Asegurar que todos los campos existan
        metadata.setdefault("macrodominio", "General")
        metadata.setdefault("agente", "General")
        metadata.setdefault("nivel", "Todos")
        metadata.setdefault("fuente", "Desconocida")
        # Añadir el nombre
        entry = {"filename": filename, **metadata}
        results.append(entry)
    return results


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Extrae metadatos de archivos Markdown de la base de conocimiento de SeniorVital."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(r"E:\SeniorVital-master\data\knowledge_base"),
        help="Directorio donde se encuentran los archivos .md (por defecto: E:\\SeniorVital-master\\data\\knowledge_base)"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path(r"E:\SeniorVital-master\data\processed\document_metadata.json"),
        help="Ruta del archivo JSON de salida (por defecto: E:\\SeniorVital-master\\data\\processed\\document_metadata.json)"
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    output_file = args.output_file

    if not input_dir.exists():
        print(f"❌ El directorio de entrada no existe: {input_dir}")
        return

    # Asegurar que el directorio de salida existe
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"📂 Procesando archivos en: {input_dir}")
    metadata_list = extract_metadata(input_dir)
    print(f"✅ Se encontraron {len(metadata_list)} archivos .md")

    # Guardar como JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2, ensure_ascii=False)

    print(f"💾 Metadatos guardados en: {output_file}")

    # Mostrar un resumen
    print("\n📊 Resumen por Macrodominio:")
    counts = {}
    for entry in metadata_list:
        macro = entry["macrodominio"]
        counts[macro] = counts.get(macro, 0) + 1
    for macro, count in sorted(counts.items()):
        print(f"   {macro}: {count} documento(s)")


if __name__ == "__main__":
    main()