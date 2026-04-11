import io
import matplotlib
import matplotlib.pyplot as plt
import numpy
import pandas as pd
import seaborn
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

seaborn.set_context('talk')

df = pd.read_csv('data/sysarmy_survey_2026_processed.csv')

#print(df[:10])
print(df['salary_monthly_NETO'].quantile(0.75) - df['salary_monthly_NETO'].quantile(0.25))
plt.hist(df['salary_monthly_NETO'], bins=40, density=True, alpha=0.7)
plt.savefig('grafico.png')                                
print("✅ Guardado en grafico.png")        