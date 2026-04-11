import io
import matplotlib
import matplotlib.pyplot as plt
import numpy
import pandas as pd
import seaborn
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

seaborn.set_context('talk')

df = pd.read_csv('data/sysarmy_survey_2026_processed.csv', keep_default_na=False)

print(df[:10])