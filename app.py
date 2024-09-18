import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar datos
file_path = "C:/Users/Usuario/Desktop/Estadisticas DP/estadisticas DP.xlsx"
data = pd.read_excel(file_path)

# Limpiar la columna 'Actividad física'
try:
    data['Actividad física'] = data['Actividad física'].str.strip()  # Eliminar espacios en blanco
    data['Actividad física'] = data['Actividad física'].replace({'No me doy cuenta': 'No realiza', 'Si te das cuenta': 'Sí'})  # Reemplazar valores incorrectos
except KeyError:
    st.write("La columna 'Actividad física' no se encontró en los datos.")

# Eliminar columnas que comienzan con "Observaciones"
data = data.loc[:, ~data.columns.str.startswith('Observaciones')]

# Convertir la columna 'Edad' a numérica, forzando errores a NaN
data['Edad'] = pd.to_numeric(data['Edad'], errors='coerce')

# Eliminar filas donde 'Edad' es NaN
data = data.dropna(subset=['Edad'])

st.title('Análisis de Pacientes')

# Selección de rango de edad
edad_min = st.number_input('Edad mínima', min_value=0, max_value=120, value=0, step=1)
edad_max = st.number_input('Edad máxima', min_value=0, max_value=120, value=100, step=1)

# Selección de variables y resultados para cruzar
selected_variables = st.multiselect('Selecciona las variables a cruzar', data.columns.tolist())
selected_values = {}

for variable in selected_variables:
    unique_values = data[variable].unique()
    selected_values[variable] = st.multiselect(f'Selecciona valores de {variable}', unique_values)

# Selección de tipo de gráfico
grafico_type = st.selectbox('Selecciona el tipo de gráfico', ['Barras', 'Pastel', 'No hacer gráfico'])

if st.button('Cruzar variables'):
    # Filtrar datos según el rango de edad
    filtered_data = data[(data['Edad'] >= edad_min) & (data['Edad'] <= edad_max)]
    
    # Total inicial (cantidad de pacientes en el rango de edad)
    total_inicial = len(filtered_data)
    
    # Crear una lista para almacenar los resultados
    resultados = [("Total Inicial (Rango de Edad)", total_inicial, 100.0)]
    
    # Aplicar los filtros seleccionados
    for variable, values in selected_values.items():
        filtered_data = filtered_data[filtered_data[variable].isin(values)]
        subtotal = len(filtered_data)
        subtotal_porcentaje = (subtotal / total_inicial) * 100
        resultados.append((f"{variable}: {', '.join(values)}", subtotal, subtotal_porcentaje))
    
    # Crear un DataFrame para los resultados
    resultados_df = pd.DataFrame(resultados, columns=['Descripción', 'Total', '% del Total'])
    
    # Mostrar tabla de resultados
    st.write('Resultados:')
    st.write(resultados_df)
    
    # Generar gráfico si se selecciona una opción válida
    if grafico_type != 'No hacer gráfico':
        fig, ax = plt.subplots(figsize=(10, 6))  # Crear figura y ejes
        if grafico_type == 'Barras':
            sns.barplot(x='Descripción', y='Total', data=resultados_df, ax=ax)
            ax.set_title('Resultados por Variable')
            ax.set_ylabel('Total')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
        elif grafico_type == 'Pastel':
            ax.pie(resultados_df['Total'], labels=resultados_df['Descripción'], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        st.pyplot(fig)  # Mostrar el gráfico
    
    # Botón para descargar los datos de pacientes filtrados en CSV
    csv_pacientes = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar datos de pacientes en CSV",
        data=csv_pacientes,
        file_name='datos_pacientes_filtrados.csv',
        mime='text/csv',
        key='download-csv-pacientes'
    )
    
    # Botón para descargar los resultados de los cruces en CSV
    csv_resultados = resultados_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar resultados en CSV",
        data=csv_resultados,
        file_name='resultados_cruce.csv',
        mime='text/csv',
        key='download-csv-resultados'
    )