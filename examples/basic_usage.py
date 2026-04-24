from gsheet_functions import GoogleSheetsFunctions
import pandas as pd

# Inicializar
gs = GoogleSheetsFunctions("tu_credencial.json", "Nombre de tu hoja")
worksheet = gs.get_worksheet(0)  # primera pestaña

# Leer datos existentes (opcional)
data = worksheet.get_all_values()
df_existente = pd.DataFrame(data[1:], columns=data[0])

# Crear nuevo DataFrame
df_nuevo = pd.DataFrame({"A": [1,2], "B": ["x","y"]})

# Actualizar hoja (sobrescribe datos desde A2)
gs.update_worksheet(worksheet, df_nuevo, clear_existing=True)