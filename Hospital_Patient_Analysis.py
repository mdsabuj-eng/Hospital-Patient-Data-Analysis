# ========== 1. Environment Setup 
import sqlite3  
import urllib.request 
import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
import seaborn as sns  

#set styles 
sns.set(style="whitegrid")
plt.style.use('seaborn-v0_8-darkgrid')

# ========== 2. SQLite DB Connection ==========
db_path = r'C:\Users\HP\OneDrive\Desktop\final python\projectlist\project1\Hospital_Patient_Analysis.db'  # Change as per project
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
print("Connected to SQLite database!")

# ========== 3. Read All Tables as Pandas DataFrame ==========

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = [table[0] for table in cursor.fetchall()] 
print("Tables in DB:", table_names)

#  Connect to SQLite database
conn = sqlite3.connect(db_path)

for table_name in table_names:
    # Load each table into DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    print(f"\nOriginal Data from Table: {table_name}")
    print(df)

    #  1. Handling Missing Values
    df_clean = df.copy()  

    for col in df_clean.columns:
        if df_clean[col].dtype in ['float64', 'int64']:  
            median_val = df_clean[col].median()
            df_clean.loc[:, col] = df_clean[col].fillna(median_val)
        else:  # Categorical/String Columns
            mode_val = df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Unknown'
            df_clean.loc[:, col] = df_clean[col].fillna(mode_val)

    print("\nAfter Missing Value Handling:")
    print(df_clean)

    #  2. Removing Duplicates
    df_clean = df_clean.drop_duplicates()
    print("\nAfter Removing Duplicates:")
    print(df_clean)

    #  3. Handling Invalid Values (Example: Negative or Zero Ages)
    if 'Age' in df_clean.columns:
        df_clean.loc[df_clean['Age'] <= 0, 'Age'] = df_clean['Age'].median()

    print("\nAfter Invalid Value Fixing (e.g., Age):")
    print(df_clean)

    #  4. Ensuring Correct Data Types (with NaN-safe ID handling)
    for col in df_clean.columns:
        if 'ID' in col or col.lower() == 'id':
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int)  # Safe conversion
        elif df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str)
        elif df_clean[col].dtype in ['float64', 'int64']:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    print("\nAfter Data Type Fixing:")
    print(df_clean)

    #  5. Handling Inconsistent Categorical Data
    if 'Name' in df_clean.columns:
        df_clean['Name'] = df_clean['Name'].str.strip().str.title()

    if 'Gender' in df_clean.columns:
        df_clean['Gender'] = df_clean['Gender'].str.strip().str.title()
        df_clean['Gender'] = df_clean['Gender'].replace({'M': 'Male', 'F': 'Female'})

    if 'Country' in df_clean.columns:
        df_clean['Country'] = df_clean['Country'].str.strip().str.title()

    print("\nAfter Cleaning Categorical Columns (e.g., Name, Gender, Country):")
    print(df_clean)

    #  Summary Statistics 
    print("\nSummary Statistics:")
    print(df_clean.describe(include='all'))

    #  Save each cleaned table as CSV
    df_clean.to_csv(f"cleaned_{table_name}.csv", index=False)

    # Final Cleaned Data for this table
    print(f"\nFinal Cleaned Data for Table: {table_name}")
    print(df_clean)


# Fetch all table names dynamically
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_names = [table[0] for table in cursor.fetchall()]
print("Tables in DB:", table_names)

def clean_dataframe(df):
    df_clean = df.copy()

    for col in df_clean.columns:
        # ============ Missing Value Handling ============
        if df_clean[col].dtype in ['float64', 'int64']:
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)
        else:
            mode_val = df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Unknown'
            df_clean[col] = df_clean[col].fillna(mode_val)

    # ============ Remove Duplicates ============
    df_clean = df_clean.drop_duplicates()

    for col in df_clean.columns:
        col_lower = col.lower()

        # ============ ID Columns Auto Detect ============
        if any(x in col_lower for x in ['id', 'number', 'code']):
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype(int)
            continue  # Skip further processing for ID

        # ============ Numeric Columns ============
        if df_clean[col].dtype in ['float64', 'int64']:
            unique_vals = df_clean[col].nunique()

            # Binary / Indicator detection (no fixing for 0 here)
            if unique_vals <= 2:
                continue  # Probably binary flag (0/1), don't fix zeros

            # Otherwise fix invalid zero/negative values (e.g., Age, Price)
            median_val = df_clean[col][df_clean[col] > 0].median()
            df_clean.loc[df_clean[col] <= 0, col] = median_val

        # ============ String / Object Columns ============
        elif df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].astype(str).str.strip().str.title()

            # Gender Auto Detect
            if any(x in col_lower for x in ['gender', 'sex']) or \
               any(val in ['M', 'F', 'Male', 'Female'] for val in df_clean[col].unique()):
                df_clean[col] = df_clean[col].replace({'M': 'Male', 'F': 'Female', 'm': 'Male', 'f': 'Female'})

    return df_clean

# Process each table and save cleaned version
for table_name in table_names:
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    print(f"\nCleaning Table: {table_name}")
    df_clean = clean_dataframe(df)
    cleaned_table_name = table_name + '_Cleaned'
    df_clean.to_sql(cleaned_table_name, conn, if_exists='replace', index=False)
    print(f"Cleaned table '{cleaned_table_name}' saved in DB.")

print("\nAll tables cleaned and saved successfully!")



#--------------------------------------------------------------------------------------------------------------------------------------------------------
##Query 1.
#1.Avg Stay Duration per Outcome

query= '''select Outcome,round(avg(julianday(DischargeDate) - julianday(AdmissionDate)),2) as Average_Stay_Days from Patient_Info_Cleaned group by 1'''
df=pd.read_sql_query(query,conn)
print(df)




##Query 2.
### Avg Treatment Duration per Department

query='''select pa.PatientID , round(avg(julianday(tr.TreatmentEndDate)-julianday(pa.AdmissionDate)),2)as Avg_Treatment_Duration
from Treatment_Record_Cleaned as tr join Patient_Info_Cleaned as pa on tr.PatientID=pa.PatientID
group by 1'''

df=pd.read_sql_query(query,conn)
print(df)

#"This analysis was excluded due to the absence of Department linkage in patient-related tables."



#-------------------------------------------------------------------------------------------------------------------------------------------------------



#1: Bar Chart (Outcome Wise Patient Count)

query='''select count(distinct PatientID) as PatientId,Outcome from Patient_Info_Cleaned group by 2'''
df=pd.read_sql_query(query,conn)
print(df)

plt.figure(figsize=(8, 5)) 
sns.barplot(data=df, x='PatientId', y='Outcome', hue='PatientId', palette='viridis', legend=False)

plt.title('Outcome Wise Patient Count')  
plt.xlabel('Patient')    
plt.ylabel('Outcome')    
plt.xticks(rotation=45)       
plt.tight_layout()

plt.savefig('images/bar_outcome.png', bbox_inches='tight')
plt.show()
plt.close()

##2:Pie Chart: % of Treatment Type

query='''select  TreatmentType  from Treatment_Record_Cleaned'''
df=pd.read_sql_query(query,conn)
print(df)

plt.figure(figsize=(6, 6)) 
df['TreatmentType'].value_counts().plot.pie(autopct='%1.1f%%', colors=sns.color_palette('viridis'))

plt.title('% of Treatment Type') 
plt.ylabel('')  
plt.tight_layout()


plt.savefig('images/pie_treatment_type.png', bbox_inches='tight')
plt.show()
plt.close()

##3.Line Chart: Admissions per Month

query='''select strftime('%Y-%m',AdmissionDate)as month ,count(distinct PatientID) as total_patient  from Patient_Info_Cleaned group by 1'''
df=pd.read_sql_query(query,conn)
print(df)

plt.figure(figsize=(10,5))
sns.lineplot(data=df, x='month', y='total_patient', marker='o', color='teal')
plt.title('Admissions per Month')
plt.xlabel('Month')
plt.ylabel('Patient')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('images/line_admission.png', bbox_inches='tight')
plt.show()
plt.close()

conn.close()
