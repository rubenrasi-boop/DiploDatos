#!/usr/bin/env python3
"""
Genera todos los gráficos de la guía teórica del entregable parte 1.
Los guarda en _build/ayvd/parte1/img/
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sns.set_style('whitegrid')
sns.set_context('talk')

IMG_DIR = 'img'
os.makedirs(IMG_DIR, exist_ok=True)

df = pd.read_csv('data/sysarmy_survey_2026_processed.csv')

# Limpieza base para los gráficos
df_clean = df.dropna(subset=['salary_monthly_NETO']).copy()
Q1 = df_clean['salary_monthly_NETO'].quantile(0.05)
Q3 = df_clean['salary_monthly_NETO'].quantile(0.95)
IQR = Q3 - Q1
df_clean = df_clean[
    (df_clean['salary_monthly_NETO'] >= max(300000, Q1 - 1.5 * IQR)) &
    (df_clean['salary_monthly_NETO'] <= Q3 + 1.5 * IQR) &
    (df_clean['work_dedication'] == 'Full-Time') &
    (df_clean['profile_age'] < 100)
].copy()

sal = df_clean['salary_monthly_NETO']
fmt_m = mticker.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M')

def savefig(fig, name):
    fig.savefig(os.path.join(IMG_DIR, name), dpi=130, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  ✅ {name}')

# ============================================================
# SECCIÓN 2: Estadística descriptiva univariada
# ============================================================
print("Sección 2: Descriptiva univariada...")

# 2.1 Media vs Mediana en distribución asimétrica
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(sal, bins=50, color='steelblue', alpha=0.7, edgecolor='white', density=True)
media = sal.mean()
mediana = sal.median()
ax.axvline(media, color='#e74c3c', linewidth=2.5, linestyle='--', label=f'Media: ${media/1e6:.2f}M')
ax.axvline(mediana, color='#2ecc71', linewidth=2.5, linestyle='-', label=f'Mediana: ${mediana/1e6:.2f}M')
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_ylabel('Densidad')
ax.set_title('Media vs Mediana en una distribución asimétrica (salarios)')
ax.xaxis.set_major_formatter(fmt_m)
ax.legend(fontsize=13)
savefig(fig, '02_01_media_vs_mediana.png')

# 2.2 Cuantiles y percentiles
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(sal, bins=50, color='steelblue', alpha=0.5, edgecolor='white', density=True)
q1_val = sal.quantile(0.25)
q2_val = sal.quantile(0.50)
q3_val = sal.quantile(0.75)
p10_val = sal.quantile(0.10)
p90_val = sal.quantile(0.90)
for val, label, color, ls in [
    (p10_val, f'P10: ${p10_val/1e6:.2f}M', '#9b59b6', ':'),
    (q1_val, f'Q1 (P25): ${q1_val/1e6:.2f}M', '#e67e22', '--'),
    (q2_val, f'Q2 (P50): ${q2_val/1e6:.2f}M', '#2ecc71', '-'),
    (q3_val, f'Q3 (P75): ${q3_val/1e6:.2f}M', '#e74c3c', '--'),
    (p90_val, f'P90: ${p90_val/1e6:.2f}M', '#3498db', ':'),
]:
    ax.axvline(val, color=color, linewidth=2, linestyle=ls, label=label)
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_ylabel('Densidad')
ax.set_title('Cuantiles y percentiles de la distribución salarial')
ax.xaxis.set_major_formatter(fmt_m)
ax.legend(fontsize=11, loc='upper right')
savefig(fig, '02_02_cuantiles_percentiles.png')

# 2.3 Asimetría visual
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
# Simétrica
np.random.seed(42)
sym_data = np.random.normal(3, 1, 5000)
axes[0].hist(sym_data, bins=40, color='#3498db', alpha=0.7, edgecolor='white', density=True)
axes[0].set_title(f'Simétrica\nskew ≈ {stats.skew(sym_data):.2f}')
axes[0].set_ylabel('Densidad')
# Asimetría positiva (salarios reales)
axes[1].hist(sal, bins=40, color='#e74c3c', alpha=0.7, edgecolor='white', density=True)
axes[1].set_title(f'Asimetría positiva (salarios)\nskew ≈ {sal.skew():.2f}')
axes[1].xaxis.set_major_formatter(fmt_m)
# Asimetría negativa (simulada)
neg_data = -np.random.exponential(2, 5000) + 15
axes[2].hist(neg_data, bins=40, color='#2ecc71', alpha=0.7, edgecolor='white', density=True)
axes[2].set_title(f'Asimetría negativa\nskew ≈ {stats.skew(neg_data):.2f}')
fig.suptitle('Tipos de asimetría (skewness)', fontsize=16, fontweight='bold', y=1.03)
fig.tight_layout()
savefig(fig, '02_03_asimetria.png')

# ============================================================
# SECCIÓN 3: Visualización de una variable
# ============================================================
print("Sección 3: Visualización univariada...")

# 3.1 Histograma con diferentes bins
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
for ax, nbins, title in [(axes[0], 10, '10 bins (poco detalle)'),
                          (axes[1], 40, '40 bins (equilibrado)'),
                          (axes[2], 150, '150 bins (demasiado ruido)')]:
    ax.hist(sal, bins=nbins, color='steelblue', alpha=0.7, edgecolor='white')
    ax.set_title(title)
    ax.xaxis.set_major_formatter(fmt_m)
    ax.set_xlabel('Salario NETO')
axes[0].set_ylabel('Frecuencia')
fig.suptitle('Efecto del número de bins en un histograma', fontsize=15, fontweight='bold', y=1.03)
fig.tight_layout()
savefig(fig, '03_01_histograma_bins.png')

# 3.2 Boxplot anatomía
fig, ax = plt.subplots(figsize=(10, 3))
bp = ax.boxplot(sal, vert=False, widths=0.6, patch_artist=True,
                boxprops=dict(facecolor='#AED6F1', edgecolor='#2c3e50', linewidth=1.5),
                medianprops=dict(color='#e74c3c', linewidth=2.5),
                whiskerprops=dict(color='#2c3e50', linewidth=1.5),
                capprops=dict(color='#2c3e50', linewidth=1.5),
                flierprops=dict(marker='o', markerfacecolor='#95a5a6', markersize=4, alpha=0.5))
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_title('Anatomía de un boxplot')
ax.xaxis.set_major_formatter(fmt_m)
# Anotaciones
q1_v = sal.quantile(0.25)
q3_v = sal.quantile(0.75)
med_v = sal.median()
ax.annotate(f'Q1\n${q1_v/1e6:.1f}M', xy=(q1_v, 1), xytext=(q1_v, 1.35),
            fontsize=10, ha='center', arrowprops=dict(arrowstyle='->', color='#2c3e50'))
ax.annotate(f'Mediana\n${med_v/1e6:.1f}M', xy=(med_v, 1), xytext=(med_v, 1.35),
            fontsize=10, ha='center', color='#e74c3c', arrowprops=dict(arrowstyle='->', color='#e74c3c'))
ax.annotate(f'Q3\n${q3_v/1e6:.1f}M', xy=(q3_v, 1), xytext=(q3_v, 1.35),
            fontsize=10, ha='center', arrowprops=dict(arrowstyle='->', color='#2c3e50'))
ax.set_yticks([])
savefig(fig, '03_02_boxplot_anatomia.png')

# 3.3 Violin plot vs boxplot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].set_title('Boxplot')
sns.boxplot(x=sal, ax=axes[0], color='#AED6F1', showfliers=False)
axes[0].xaxis.set_major_formatter(fmt_m)
axes[0].set_xlabel('Salario NETO')
axes[1].set_title('Violin plot')
sns.violinplot(x=sal, ax=axes[1], color='#AED6F1', inner='quartile', cut=0)
axes[1].xaxis.set_major_formatter(fmt_m)
axes[1].set_xlabel('Salario NETO')
fig.suptitle('Boxplot vs Violin plot: mismos datos, distinta información', fontsize=14, fontweight='bold', y=1.02)
fig.tight_layout()
savefig(fig, '03_03_boxplot_vs_violin.png')

# 3.4 Gráfico de barras (categórica)
fig, ax = plt.subplots(figsize=(9, 5))
sen_counts = df_clean['work_seniority'].value_counts()
colors = ['#2ecc71', '#f39c12', '#e74c3c']
ax.bar(sen_counts.index, sen_counts.values, color=colors, edgecolor='white', width=0.6)
for i, (idx, val) in enumerate(zip(sen_counts.index, sen_counts.values)):
    ax.text(i, val + 30, str(val), ha='center', fontsize=13, fontweight='bold')
ax.set_ylabel('Frecuencia')
ax.set_title('Distribución de seniority (variable categórica)')
savefig(fig, '03_04_barras_categorica.png')

# 3.5 KDE
fig, ax = plt.subplots(figsize=(10, 5))
for sen, color in [('Junior', '#e74c3c'), ('Semi-Senior', '#f39c12'), ('Senior', '#2ecc71')]:
    subset = df_clean[df_clean['work_seniority'] == sen]['salary_monthly_NETO']
    sns.kdeplot(subset, ax=ax, color=color, label=f'{sen} (n={len(subset)})', linewidth=2, fill=True, alpha=0.15)
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_ylabel('Densidad')
ax.set_title('KDE: densidad estimada de salarios por seniority')
ax.xaxis.set_major_formatter(fmt_m)
ax.legend()
savefig(fig, '03_05_kde.png')

# ============================================================
# SECCIÓN 4: Limpieza de datos
# ============================================================
print("Sección 4: Limpieza de datos...")

# 4.1 Outliers - antes y después
sal_raw = df.dropna(subset=['salary_monthly_NETO'])['salary_monthly_NETO']
fig, axes = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'height_ratios': [1, 1]})
axes[0].boxplot(sal_raw, vert=False, widths=0.6, patch_artist=True,
                boxprops=dict(facecolor='#FADBD8'), flierprops=dict(marker='.', markersize=3, alpha=0.3))
axes[0].set_title(f'ANTES de limpiar outliers (n={len(sal_raw)}, max=${sal_raw.max()/1e6:.0f}M)')
axes[0].xaxis.set_major_formatter(fmt_m)
axes[0].set_yticks([])
axes[1].boxplot(sal, vert=False, widths=0.6, patch_artist=True,
                boxprops=dict(facecolor='#D5F5E3'), flierprops=dict(marker='.', markersize=3, alpha=0.3))
axes[1].set_title(f'DESPUÉS de limpiar outliers (n={len(sal)}, max=${sal.max()/1e6:.1f}M)')
axes[1].xaxis.set_major_formatter(fmt_m)
axes[1].set_yticks([])
fig.suptitle('Efecto de la eliminación de outliers', fontsize=14, fontweight='bold', y=1.02)
fig.tight_layout()
savefig(fig, '04_01_outliers_antes_despues.png')

# 4.2 Método IQR visual
fig, ax = plt.subplots(figsize=(12, 4))
ax.hist(sal, bins=50, color='steelblue', alpha=0.5, edgecolor='white', density=True)
iqr_q1 = sal.quantile(0.25)
iqr_q3 = sal.quantile(0.75)
iqr_val = iqr_q3 - iqr_q1
lower_fence = iqr_q1 - 1.5 * iqr_val
upper_fence = iqr_q3 + 1.5 * iqr_val
ax.axvspan(iqr_q1, iqr_q3, alpha=0.2, color='#2ecc71', label=f'IQR = ${iqr_val/1e6:.2f}M')
ax.axvline(lower_fence, color='#e74c3c', linewidth=2, linestyle='--', label=f'Límite inf: ${lower_fence/1e6:.2f}M')
ax.axvline(upper_fence, color='#e74c3c', linewidth=2, linestyle='--', label=f'Límite sup: ${upper_fence/1e6:.2f}M')
ax.axvline(iqr_q1, color='#2ecc71', linewidth=1.5, linestyle='-')
ax.axvline(iqr_q3, color='#2ecc71', linewidth=1.5, linestyle='-')
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_ylabel('Densidad')
ax.set_title('Método IQR para detección de outliers')
ax.xaxis.set_major_formatter(fmt_m)
ax.legend(fontsize=11)
savefig(fig, '04_02_metodo_iqr.png')

# ============================================================
# SECCIÓN 5: Ejercicio 1 - Comparativo por lenguaje
# ============================================================
print("Sección 5: Comparativo por lenguaje...")

# Preparar datos de lenguajes
def split_languages(s):
    if not isinstance(s, str):
        return []
    return [l.strip().lower() for l in s.split(',') if l.strip() and l.strip().lower() != 'ninguno de los anteriores']

df_clean.loc[:, 'parsed_langs'] = df_clean['tools_programming_languages'].apply(split_languages)
df_lang = df_clean.explode('parsed_langs').rename(columns={'parsed_langs': 'language'})
df_lang = df_lang[df_lang['language'].str.len() > 0]
top_langs = df_lang['language'].value_counts().head(8).index.tolist()
df_top = df_lang[df_lang['language'].isin(top_langs)]
medians_order = df_top.groupby('language')['salary_monthly_NETO'].median().sort_values(ascending=False).index.tolist()

# 5.1 Boxplot comparativo por lenguaje
fig, ax = plt.subplots(figsize=(13, 7))
palette = sns.color_palette("Set2", n_colors=len(medians_order))
sns.boxplot(data=df_top, x='salary_monthly_NETO', y='language',
            order=medians_order, palette=palette, ax=ax, showfliers=False, width=0.6)
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_ylabel('')
ax.set_yticklabels([l.title() for l in medians_order])
ax.set_title('Comparación de distribuciones salariales por lenguaje\n(boxplots ordenados por mediana)')
ax.xaxis.set_major_formatter(fmt_m)
savefig(fig, '05_01_boxplot_lenguajes.png')

# 5.2 Violin plot comparativo
fig, ax = plt.subplots(figsize=(13, 7))
sns.violinplot(data=df_top, x='salary_monthly_NETO', y='language',
               order=medians_order, palette=palette, ax=ax, inner='quartile', cut=0, scale='width')
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_ylabel('')
ax.set_yticklabels([l.title() for l in medians_order])
ax.set_title('Densidad salarial por lenguaje (violin plot)\nLa anchura muestra la concentración de datos')
ax.xaxis.set_major_formatter(fmt_m)
savefig(fig, '05_02_violin_lenguajes.png')

# 5.3 Probabilidad condicional
p75_global = sal.quantile(0.75)
prob_data = []
for lang in medians_order:
    subset = df_top[df_top['language'] == lang]['salary_monthly_NETO']
    prob = (subset > p75_global).sum() / len(subset) * 100
    prob_data.append({'language': lang.title(), 'prob': prob, 'n': len(subset)})
prob_df = pd.DataFrame(prob_data).sort_values('prob', ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
colors_prob = sns.color_palette("RdYlGn", n_colors=len(prob_df))
bars = ax.barh(range(len(prob_df)), prob_df['prob'].values, color=colors_prob)
ax.set_yticks(range(len(prob_df)))
ax.set_yticklabels(prob_df['language'].values)
ax.invert_yaxis()
ax.set_xlabel(f'P(salario > ${p75_global/1e6:.1f}M)')
ax.set_title(f'Probabilidad condicional: P(salario > P75 global | sabe lenguaje X)\nP75 global = ${p75_global/1e6:.2f}M')
for i, (v, n) in enumerate(zip(prob_df['prob'].values, prob_df['n'].values)):
    ax.text(v + 0.3, i, f'{v:.1f}% (n={n})', va='center', fontsize=10)
savefig(fig, '05_03_probabilidad_condicional.png')

# ============================================================
# SECCIÓN 6: Estadística bivariada
# ============================================================
print("Sección 6: Bivariada...")

# 6.1 Scatterplot Bruto vs Neto con correlación
df_corr = df_clean.dropna(subset=['salary_monthly_BRUTO', 'salary_monthly_NETO'])
r_pearson = df_corr['salary_monthly_BRUTO'].corr(df_corr['salary_monthly_NETO'])
r_spearman = df_corr['salary_monthly_BRUTO'].corr(df_corr['salary_monthly_NETO'], method='spearman')

fig, ax = plt.subplots(figsize=(9, 8))
ax.scatter(df_corr['salary_monthly_BRUTO'], df_corr['salary_monthly_NETO'],
           alpha=0.2, s=10, color='steelblue')
max_val = max(df_corr['salary_monthly_BRUTO'].max(), df_corr['salary_monthly_NETO'].max())
ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, linewidth=1.5, label='y = x')
ax.set_xlabel('Salario BRUTO (ARS)')
ax.set_ylabel('Salario NETO (ARS)')
ax.set_title(f'Correlación Bruto vs Neto\nPearson r = {r_pearson:.3f}  |  Spearman ρ = {r_spearman:.3f}')
ax.xaxis.set_major_formatter(fmt_m)
ax.yaxis.set_major_formatter(fmt_m)
ax.legend()
savefig(fig, '06_01_scatter_bruto_neto.png')

# 6.2 Heatmap de correlación
num_cols = ['salary_monthly_BRUTO', 'salary_monthly_NETO', 'profile_years_experience',
            'profile_age', 'work_years_in_company', 'salary_satisfaction']
labels_c = ['Bruto', 'Neto', 'Años exp.', 'Edad', 'Años empresa', 'Satisfacción']
corr_matrix = df_clean[num_cols].corr()

fig, ax = plt.subplots(figsize=(9, 8))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            xticklabels=labels_c, yticklabels=labels_c, ax=ax,
            square=True, linewidths=0.5, vmin=-1, vmax=1)
ax.set_title('Matriz de correlación de Pearson\n(variables numéricas del dataset)')
savefig(fig, '06_02_heatmap_correlacion.png')

# 6.3 Tipos de correlación (didáctico)
np.random.seed(42)
fig, axes = plt.subplots(1, 4, figsize=(18, 4))
# Positiva fuerte
x = np.random.normal(0, 1, 200)
axes[0].scatter(x, x * 0.9 + np.random.normal(0, 0.3, 200), alpha=0.5, s=20, color='#2ecc71')
axes[0].set_title('Positiva fuerte\nr ≈ 0.95')
# Negativa moderada
axes[1].scatter(x, -x * 0.6 + np.random.normal(0, 0.8, 200), alpha=0.5, s=20, color='#e74c3c')
axes[1].set_title('Negativa moderada\nr ≈ -0.60')
# Sin correlación lineal
axes[2].scatter(x, np.random.normal(0, 1, 200), alpha=0.5, s=20, color='#95a5a6')
axes[2].set_title('Sin correlación lineal\nr ≈ 0.00')
# No lineal (Pearson ≈ 0 pero hay relación)
x2 = np.linspace(-3, 3, 200)
axes[3].scatter(x2, x2**2 + np.random.normal(0, 0.8, 200), alpha=0.5, s=20, color='#9b59b6')
axes[3].set_title('Relación NO lineal\nr ≈ 0.00 (¡pero hay patrón!)')
for ax in axes:
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
fig.suptitle('Tipos de correlación', fontsize=15, fontweight='bold', y=1.03)
fig.tight_layout()
savefig(fig, '06_03_tipos_correlacion.png')

# ============================================================
# SECCIÓN 7: Densidad de probabilidad
# ============================================================
print("Sección 7: Densidades...")

# 7.1 Densidad condicional: salario | nivel de estudio
df_edu = df_clean.dropna(subset=['profile_studies_level'])
top2_edu = df_edu['profile_studies_level'].value_counts().head(2).index.tolist()
df_edu_f = df_edu[df_edu['profile_studies_level'].isin(top2_edu)]

fig, axes = plt.subplots(1, 2, figsize=(16, 5.5))
# Histogramas superpuestos
for edu, color in zip(top2_edu, ['#3498db', '#e67e22']):
    subset = df_edu_f[df_edu_f['profile_studies_level'] == edu]['salary_monthly_NETO']
    axes[0].hist(subset.dropna(), bins=35, alpha=0.5, color=color,
                 label=f'{edu} (n={len(subset)})', density=True, edgecolor='white')
axes[0].set_xlabel('Salario mensual NETO')
axes[0].set_ylabel('Densidad')
axes[0].set_title('Densidad condicional: f(salario | nivel de estudio)')
axes[0].xaxis.set_major_formatter(fmt_m)
axes[0].legend(fontsize=11)

# Boxplot
sns.boxplot(data=df_edu_f, x='profile_studies_level', y='salary_monthly_NETO',
            order=top2_edu, palette=['#3498db', '#e67e22'], ax=axes[1], showfliers=False)
axes[1].set_xlabel('Nivel de estudio')
axes[1].set_ylabel('Salario mensual NETO')
axes[1].set_title('¿Son independientes salario y nivel de estudio?')
axes[1].yaxis.set_major_formatter(fmt_m)
fig.tight_layout()
savefig(fig, '07_01_densidad_condicional_estudio.png')

# 7.2 Independencia visual
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
# Caso "independientes" (simulado)
np.random.seed(42)
cat_a = np.random.normal(3, 1, 500)
cat_b = np.random.normal(3, 1, 500)
axes[0].hist(cat_a, bins=30, alpha=0.5, color='#3498db', label='Grupo A', density=True, edgecolor='white')
axes[0].hist(cat_b, bins=30, alpha=0.5, color='#e67e22', label='Grupo B', density=True, edgecolor='white')
axes[0].set_title('Variables INDEPENDIENTES\n(distribuciones iguales)')
axes[0].legend()
# Caso "dependientes" (simulado)
dep_a = np.random.normal(3, 1, 500)
dep_b = np.random.normal(5, 1.2, 500)
axes[1].hist(dep_a, bins=30, alpha=0.5, color='#3498db', label='Grupo A', density=True, edgecolor='white')
axes[1].hist(dep_b, bins=30, alpha=0.5, color='#e67e22', label='Grupo B', density=True, edgecolor='white')
axes[1].set_title('Variables DEPENDIENTES\n(distribuciones distintas)')
axes[1].legend()
fig.suptitle('Independencia: f(Y|X=a) = f(Y|X=b) → independientes', fontsize=13, fontweight='bold', y=1.03)
fig.tight_layout()
savefig(fig, '07_02_independencia_visual.png')

# ============================================================
# SECCIÓN 8: Visualización multivariada
# ============================================================
print("Sección 8: Multivariada...")

# 8.1 Scatterplot con hue (seniority)
df_plot = df_clean[df_clean['profile_gender'].isin(['Hombre Cis', 'Mujer Cis'])]
fig, ax = plt.subplots(figsize=(12, 7))
sen_colors = {'Junior': '#e74c3c', 'Semi-Senior': '#f39c12', 'Senior': '#2ecc71'}
for sen in ['Junior', 'Semi-Senior', 'Senior']:
    mask = df_plot['work_seniority'] == sen
    ax.scatter(df_plot.loc[mask, 'profile_years_experience'],
               df_plot.loc[mask, 'salary_monthly_NETO'],
               alpha=0.3, label=sen, s=15, color=sen_colors[sen])
ax.set_xlabel('Años de experiencia')
ax.set_ylabel('Salario mensual NETO')
ax.set_title('Scatterplot con hue: Salario vs Experiencia\ncoloreado por seniority')
ax.yaxis.set_major_formatter(fmt_m)
ax.legend(title='Seniority', markerscale=3)
savefig(fig, '08_01_scatter_hue_seniority.png')

# 8.2 Pairplot simplificado
from matplotlib.gridspec import GridSpec
fig = plt.figure(figsize=(14, 11))
gs = GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.5)
num_vars = ['salary_monthly_NETO', 'profile_years_experience', 'profile_age']
labels = ['Salario NETO', 'Años experiencia', 'Edad']

for i in range(3):
    for j in range(3):
        ax = fig.add_subplot(gs[i, j])
        if i == j:
            ax.hist(df_clean[num_vars[i]].dropna(), bins=35, color='steelblue', alpha=0.7, edgecolor='white')
        else:
            ax.scatter(df_clean[num_vars[j]], df_clean[num_vars[i]], alpha=0.1, s=3, color='steelblue')
        if j == 0:
            ax.set_ylabel(labels[i], fontsize=10)
        if i == 2:
            ax.set_xlabel(labels[j], fontsize=10)
        if i == 0 and j != 0:
            ax.yaxis.set_major_formatter(fmt_m)
        if j == 0 and i == 0:
            ax.xaxis.set_major_formatter(fmt_m)

fig.suptitle('Pairplot: relaciones entre Salario, Experiencia y Edad', fontsize=15, fontweight='bold', y=1.01)
savefig(fig, '08_02_pairplot.png')

# 8.3 Boxplot facetado (seniority × género)
fig, ax = plt.subplots(figsize=(11, 6))
sns.boxplot(data=df_plot, x='work_seniority', y='salary_monthly_NETO',
            hue='profile_gender', order=['Junior', 'Semi-Senior', 'Senior'],
            palette={'Hombre Cis': '#3498db', 'Mujer Cis': '#e91e63'}, ax=ax, showfliers=False)
ax.set_xlabel('Seniority')
ax.set_ylabel('Salario mensual NETO')
ax.set_title('Boxplot facetado: Salario por seniority y género\n(hue = variable categórica)')
ax.yaxis.set_major_formatter(fmt_m)
ax.legend(title='Género')
savefig(fig, '08_03_boxplot_facetado.png')

# 8.4 Scatter con hue género
fig, ax = plt.subplots(figsize=(12, 7))
for gen, color in [('Hombre Cis', '#3498db'), ('Mujer Cis', '#e91e63')]:
    mask = df_plot['profile_gender'] == gen
    ax.scatter(df_plot.loc[mask, 'profile_years_experience'],
               df_plot.loc[mask, 'salary_monthly_NETO'],
               alpha=0.2, label=gen, s=15, color=color)
ax.set_xlabel('Años de experiencia')
ax.set_ylabel('Salario mensual NETO')
ax.set_title('Scatterplot con hue: Salario vs Experiencia\ncoloreado por género')
ax.yaxis.set_major_formatter(fmt_m)
ax.legend(title='Género', markerscale=3)
savefig(fig, '08_04_scatter_hue_genero.png')

print(f"\n✅ Todos los gráficos generados en {os.path.abspath(IMG_DIR)}/")
