# run with:
# streamlit run excel_02_streamlit.py
#
# https://discuss.streamlit.io/t/multiselect-items-displayed-as-in-a-box/50291/2
import streamlit as st
import pandas as pd

# Function to process column 3 values: split by commas and newlines
def process_column_string_to_list(value):
    # Check if the value is a string, otherwise return an empty list
    if isinstance(value, str):
        # Split by comma and then by newline, flatten the list
        return [item.strip() for line in value.split('\n') for item in line.split(',')]
    else:
        return []


# Path to your Excel file
file_path = '../_data/texts/animals.xlsx'

# Read the Excel file
df = pd.read_excel(file_path)

# Applying the function to a column by its name
diet = 'Diet'
preds = 'Predators/Threats'
df[diet] = df[diet].apply(process_column_string_to_list)
df[preds] = df[preds].apply(process_column_string_to_list)

# Unique values
diet_options = df[diet].explode().sort_values().unique().tolist()
preds_options = df[preds].explode().sort_values().unique().tolist()

# Filters
container1 = st.container()
all1 = st.checkbox("Select all diet")
container2 = st.container()
all2 = st.checkbox("Select all predators")

# Filter selection
if all1:
    selected_diet = container1.multiselect("Select one or more options:",
         diet_options, diet_options)
else:
    selected_diet =  container1.multiselect("Select one or more options:",
        diet_options)

if all2:
    selected_predators = container2.multiselect("Select one or more options:",
         preds_options, preds_options)
else:
    selected_predators =  container2.multiselect("Select one or more options:",
        preds_options)

# Filter data
filtered_df = df[df[diet].apply(lambda x: any(diet in x for diet in selected_diet))]
filtered_df = filtered_df[filtered_df[preds].apply(lambda x: any(predator in x for predator in selected_predators))]

# Display data
st.write("Filtered Animals", filtered_df)