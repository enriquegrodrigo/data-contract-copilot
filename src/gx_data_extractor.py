# Configuración de rutas usando variables de entorno con fallbacks
import os

from pathlib import Path

import pandas as pd

DATA_DIR = Path(os.getenv('DATA_DIR', './data'))
CSV_FILE = Path(os.getenv('CSV_FILE', DATA_DIR / "orders.csv"))
DOC_FILE = Path(os.getenv('DOC_FILE', DATA_DIR / "orders.md"))

print(f"📁 Directorio de datos: {DATA_DIR}")
print(f"📊 Archivo CSV: {CSV_FILE}")
print(f"📋 Archivo de documentación: {DOC_FILE}")


class DataExtractor:
    def __init__(self, csv_file: Path, doc_file: Path):
        self.csv_file = csv_file
        self.doc_file = doc_file
        self.df = None
        self.documentation = None

    def load_csv(self):
        """Carga el archivo CSV y extrae información básica"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✅ CSV cargado: {len(self.df)} filas, {len(self.df.columns)} columnas")
            print(f"Columnas: {list(self.df.columns)}")
            return self.df
        except Exception as e:
            print(f"❌ Error cargando CSV: {e}")
            return None

    def load_documentation(self):
        """Carga la documentación markdown"""
        try:
            self.documentation = self.doc_file.read().decode('utf-8')
            print(f"✅ Documentación cargada: {len(self.documentation)} caracteres")
            return self.documentation
        except Exception as e:
            print(f"❌ Error cargando documentación: {e}")
            return None

    def get_data_profile(self, max_unique_values_to_show=10):
        """
        Genera un perfil básico de los datos

        Args:
            max_unique_values_to_show (int): Número máximo de valores únicos para mostrar todos los valores posibles
        """
        if self.df is None:
            return None

        profile = {
            "shape": self.df.shape,
            "columns": {}
        }

        for col in self.df.columns:
            unique_count = int(self.df[col].nunique())
            null_count = int(self.df[col].isnull().sum())

            # Información básica de la columna
            col_info = {
                "dtype": str(self.df[col].dtype),
                "null_count": null_count,
                "unique_count": unique_count,
                "sample_values": [str(val) for val in self.df[col].dropna().head(5).tolist()]
            }

            # Si tiene pocos valores únicos, mostrar todos los valores posibles
            if unique_count <= max_unique_values_to_show and unique_count > 0:
                unique_values = self.df[col].dropna().unique()
                col_info["unique_values"] = [str(val) for val in sorted(unique_values)]
                col_info["is_categorical"] = True

                # Contar frecuencias de cada valor
                value_counts = self.df[col].value_counts()
                col_info["value_frequencies"] = {
                    str(val): int(count) for val, count in value_counts.items()
                }
            else:
                col_info["is_categorical"] = False

            profile["columns"][col] = col_info

        return profile


# Inicializar extractor
# extractor = DataExtractor(CSV_FILE, DOC_FILE)
# df = extractor.load_csv()
# documentation = extractor.load_documentation()
# data_profile = extractor.get_data_profile()

# Mostrar vista previa
# print("\n📊 Vista previa de los datos:")
# if df is not None:
#     print(df.head())
#     print(f"\n🔍 Perfil de datos:")
#     if data_profile:
#         try:
#             print(json.dumps(data_profile, indent=2, ensure_ascii=False))
#         except Exception as e:
#             print(f"Error mostrando perfil completo: {e}")
#             print(f"Forma del dataset: {data_profile['shape']}")
#             print(f"Columnas: {list(data_profile['columns'].keys())}")
#
#             # Mostrar información categórica específica
#             print(f"\n📋 Columnas categóricas detectadas (≤10 valores únicos):")
#             for col, info in data_profile['columns'].items():
#                 if info.get('is_categorical', False):
#                     print(f"   • {col}: {info['unique_values']} (total: {info['unique_count']} valores)")
#                     print(f"     Frecuencias: {info['value_frequencies']}")
