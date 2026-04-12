#!/usr/bin/env python3
"""
Genera todos los gráficos de la guía teórica del entregable parte 2.
Los guarda en _build/ayvd/parte2/img/
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sns.set_style('whitegrid')
sns.set_context('talk')

IMG_DIR = 'img'
os.makedirs(IMG_DIR, exist_ok=True)

df = pd.read_csv('data/sysarmy_survey_2026_processed.csv')
fmt_m = mticker.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M')

# Preparar grupos como en la consigna
df.loc[:, 'profile_g'] = df.profile_gender.replace({
    'Hombre Cis': 'Varón cis', 'Mujer Cis': 'Mujer cis',
    'Queer': 'Diversidades', 'Trans': 'Diversidades',
    'Lesbiana': 'Diversidades', 'Agénero': 'Diversidades'
}).fillna('Sin dato')

is_man = df.profile_g == 'Varón cis'
is_woman = df.profile_g == 'Mujer cis'
groupA = df[(15000000 > df.salary_monthly_NETO) & (df.salary_monthly_NETO > 100000) & is_man].salary_monthly_NETO
groupB = df[(df.salary_monthly_NETO > 100000) & is_woman].salary_monthly_NETO

def savefig(fig, name):
    fig.savefig(os.path.join(IMG_DIR, name), dpi=130, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  ✅ {name}')

# ============================================================
# SECCIÓN 1: Población, muestra y estimadores
# ============================================================
print("Sección 1: Población y muestra...")

# 1.1 Muestreo: múltiples muestras, múltiples medias
np.random.seed(42)
pop = np.random.lognormal(mean=14.7, sigma=0.5, size=100000)
sample_means = [np.random.choice(pop, size=200).mean() for _ in range(500)]

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
axes[0].hist(pop, bins=60, color='steelblue', alpha=0.7, edgecolor='white', density=True)
axes[0].axvline(pop.mean(), color='#e74c3c', linewidth=2, linestyle='--', label=f'μ = {pop.mean()/1e6:.2f}M')
axes[0].set_title('Población (N=100.000)')
axes[0].set_xlabel('Salario')
axes[0].legend()

axes[1].hist(sample_means, bins=40, color='#2ecc71', alpha=0.7, edgecolor='white', density=True)
axes[1].axvline(np.mean(sample_means), color='#e74c3c', linewidth=2, linestyle='--',
                label=f'Media de las medias: {np.mean(sample_means)/1e6:.2f}M')
axes[1].set_title('Distribución de medias muestrales\n(500 muestras de n=200)')
axes[1].set_xlabel('Media muestral')
axes[1].legend(fontsize=11)
fig.suptitle('Teorema Central del Límite: la distribución de medias muestrales tiende a la normal',
             fontsize=13, fontweight='bold', y=1.03)
fig.tight_layout()
savefig(fig, '01_01_tcl_muestreo.png')

# 1.2 Estimador puntual: media muestral vs parámetro
fig, ax = plt.subplots(figsize=(11, 5))
np.random.seed(0)
estimates = []
for i in range(30):
    sample = np.random.choice(pop, size=150)
    estimates.append(sample.mean())
ax.scatter(range(30), [e/1e6 for e in estimates], color='steelblue', s=60, zorder=3, label='Media muestral (estimación)')
ax.axhline(pop.mean()/1e6, color='#e74c3c', linewidth=2, linestyle='--', label=f'Parámetro real μ = {pop.mean()/1e6:.2f}M')
ax.set_xlabel('Número de muestra')
ax.set_ylabel('Media (millones ARS)')
ax.set_title('Estimaciones puntuales: cada muestra da un valor distinto')
ax.legend(fontsize=11)
savefig(fig, '01_02_estimador_puntual.png')

# ============================================================
# SECCIÓN 2: Intervalo de confianza
# ============================================================
print("Sección 2: Intervalo de confianza...")

# 2.1 Visualización de IC
fig, ax = plt.subplots(figsize=(12, 7))
np.random.seed(42)
n_ic = 25
mu_real = pop.mean()
captured = 0
for i in range(n_ic):
    sample = np.random.choice(pop, size=150)
    xbar = sample.mean()
    se = sample.std() / np.sqrt(len(sample))
    ci_low = xbar - 1.96 * se
    ci_high = xbar + 1.96 * se
    contains = ci_low <= mu_real <= ci_high
    if contains:
        captured += 1
    color = '#2ecc71' if contains else '#e74c3c'
    ax.plot([ci_low/1e6, ci_high/1e6], [i, i], color=color, linewidth=2)
    ax.plot(xbar/1e6, i, 'o', color=color, markersize=5)
ax.axvline(mu_real/1e6, color='#2c3e50', linewidth=2, linestyle='--', label=f'μ real = {mu_real/1e6:.2f}M')
ax.set_xlabel('Salario (millones ARS)')
ax.set_ylabel('Muestra #')
ax.set_title(f'25 intervalos de confianza al 95%\n{captured}/25 contienen el parámetro real (verde)')
ax.legend(fontsize=12)
savefig(fig, '02_01_intervalos_confianza.png')

# 2.2 IC para diferencia de medias (datos reales)
mean_a = groupA.mean()
mean_b = groupB.mean()
diff = mean_a - mean_b
se_diff = np.sqrt(groupA.var()/len(groupA) + groupB.var()/len(groupB))
ci_low = diff - 1.96 * se_diff
ci_high = diff + 1.96 * se_diff

fig, ax = plt.subplots(figsize=(10, 3))
ax.barh(0, diff/1e6, color='#3498db', height=0.4, alpha=0.7)
ax.plot([ci_low/1e6, ci_high/1e6], [0, 0], color='#2c3e50', linewidth=3)
ax.plot(ci_low/1e6, 0, '|', color='#2c3e50', markersize=20, markeredgewidth=3)
ax.plot(ci_high/1e6, 0, '|', color='#2c3e50', markersize=20, markeredgewidth=3)
ax.plot(diff/1e6, 0, 'D', color='#e74c3c', markersize=10, zorder=5)
ax.axvline(0, color='gray', linewidth=1, linestyle='--')
ax.set_xlabel('Diferencia de medias salariales (millones ARS)')
ax.set_title(f'IC 95% para μ_varones - μ_mujeres\nEstimación puntual: ${diff/1e6:.3f}M  |  IC: [${ci_low/1e6:.3f}M, ${ci_high/1e6:.3f}M]')
ax.set_yticks([])
savefig(fig, '02_02_ic_diferencia_medias.png')

# ============================================================
# SECCIÓN 3: Test de hipótesis
# ============================================================
print("Sección 3: Test de hipótesis...")

# 3.1 Distribución bajo H0 y región de rechazo
fig, ax = plt.subplots(figsize=(11, 5.5))
x = np.linspace(-4, 4, 1000)
y = stats.norm.pdf(x)
ax.plot(x, y, color='#2c3e50', linewidth=2.5)
ax.fill_between(x, y, where=(x < -1.96), color='#e74c3c', alpha=0.3, label='Región de rechazo (α/2 = 0.025)')
ax.fill_between(x, y, where=(x > 1.96), color='#e74c3c', alpha=0.3)
ax.fill_between(x, y, where=(-1.96 <= x) & (x <= 1.96), color='#2ecc71', alpha=0.15, label='Región de no rechazo')
ax.axvline(-1.96, color='#e74c3c', linewidth=1.5, linestyle='--')
ax.axvline(1.96, color='#e74c3c', linewidth=1.5, linestyle='--')
ax.set_xlabel('Estadístico t')
ax.set_ylabel('Densidad')
ax.set_title('Test bilateral: distribución bajo H₀ y regiones de decisión\n(α = 0.05, valores críticos ±1.96)')
ax.legend(fontsize=11)
ax.annotate('t_crit = -1.96', xy=(-1.96, 0), xytext=(-3.2, 0.15),
            fontsize=11, arrowprops=dict(arrowstyle='->', color='#e74c3c'))
ax.annotate('t_crit = +1.96', xy=(1.96, 0), xytext=(2.5, 0.15),
            fontsize=11, arrowprops=dict(arrowstyle='->', color='#e74c3c'))
savefig(fig, '03_01_region_rechazo.png')

# 3.2 P-valor visual
t_stat, p_value = stats.ttest_ind(groupA, groupB, equal_var=False)

fig, ax = plt.subplots(figsize=(11, 5.5))
x = np.linspace(-6, 6, 1000)
y = stats.norm.pdf(x)
ax.plot(x, y, color='#2c3e50', linewidth=2.5)
ax.fill_between(x, y, where=(x < -abs(t_stat)), color='#e74c3c', alpha=0.4, label=f'p-valor = {p_value:.2e}')
ax.fill_between(x, y, where=(x > abs(t_stat)), color='#e74c3c', alpha=0.4)
ax.axvline(t_stat, color='#3498db', linewidth=2.5, linestyle='-', label=f'Estadístico t = {t_stat:.2f}')
ax.axvline(-t_stat, color='#3498db', linewidth=2.5, linestyle='-', alpha=0.5)
ax.set_xlabel('Estadístico t')
ax.set_ylabel('Densidad')
ax.set_title(f'P-valor del test de Welch: diferencia salarial varones vs mujeres\np = {p_value:.2e} → {"Rechazamos H₀" if p_value < 0.05 else "No rechazamos H₀"} (α = 0.05)')
ax.legend(fontsize=12)
savefig(fig, '03_02_pvalor_visual.png')

# 3.3 Distribuciones de ambos grupos
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.hist(groupA, bins=50, alpha=0.5, color='#3498db', label=f'Varones (n={len(groupA)}, x̄=${groupA.mean()/1e6:.2f}M)', density=True, edgecolor='white')
ax.hist(groupB, bins=40, alpha=0.5, color='#e91e63', label=f'Mujeres (n={len(groupB)}, x̄=${groupB.mean()/1e6:.2f}M)', density=True, edgecolor='white')
ax.axvline(groupA.mean(), color='#3498db', linewidth=2, linestyle='--')
ax.axvline(groupB.mean(), color='#e91e63', linewidth=2, linestyle='--')
ax.set_xlabel('Salario mensual NETO (ARS)')
ax.set_ylabel('Densidad')
ax.set_title('Distribuciones salariales: Varones vs Mujeres')
ax.xaxis.set_major_formatter(fmt_m)
ax.legend(fontsize=11)
savefig(fig, '03_03_distribuciones_grupos.png')

# ============================================================
# SECCIÓN 4: Errores tipo I y II, potencia
# ============================================================
print("Sección 4: Errores y potencia...")

# 4.1 Errores tipo I y II
fig, ax = plt.subplots(figsize=(12, 5.5))
x = np.linspace(-5, 8, 1000)
y_h0 = stats.norm.pdf(x, 0, 1)
y_h1 = stats.norm.pdf(x, 3, 1)
ax.plot(x, y_h0, color='#3498db', linewidth=2.5, label='Distribución bajo H₀')
ax.plot(x, y_h1, color='#e74c3c', linewidth=2.5, label='Distribución bajo H₁ (efecto real)')
# Región de rechazo
ax.fill_between(x, y_h0, where=(x > 1.96), color='#3498db', alpha=0.3)
ax.fill_between(x, y_h1, where=(x <= 1.96), color='#e74c3c', alpha=0.2)
# Anotaciones
ax.annotate('α (Error Tipo I)\nRechazo H₀ siendo verdadera', xy=(2.5, 0.02), fontsize=10,
            bbox=dict(boxstyle='round', facecolor='#AED6F1', alpha=0.8))
ax.annotate('β (Error Tipo II)\nNo rechazo H₀ siendo falsa', xy=(-0.5, 0.08), fontsize=10,
            bbox=dict(boxstyle='round', facecolor='#FADBD8', alpha=0.8))
ax.annotate('Potencia = 1 - β', xy=(3.5, 0.25), fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#D5F5E3', alpha=0.8))
ax.axvline(1.96, color='gray', linewidth=1.5, linestyle='--', label='Valor crítico')
ax.set_xlabel('Estadístico t')
ax.set_ylabel('Densidad')
ax.set_title('Errores Tipo I (α) y Tipo II (β) en un test de hipótesis')
ax.legend(fontsize=10, loc='upper right')
savefig(fig, '04_01_errores_tipo_I_II.png')

# 4.2 Potencia vs tamaño de muestra
from statsmodels.stats.power import tt_ind_solve_power

effect_size = (groupA.mean() - groupB.mean()) / groupB.std()
ratio = len(groupB) / len(groupA)

fig, ax = plt.subplots(figsize=(10, 5.5))
powers = [0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
n_needed = []
for p in powers:
    n = tt_ind_solve_power(effect_size=effect_size, alpha=0.05, power=p, ratio=ratio)
    n_needed.append(n)

ax.bar(range(len(powers)), n_needed, color=sns.color_palette("YlOrRd", len(powers)), edgecolor='white')
ax.set_xticks(range(len(powers)))
ax.set_xticklabels([f'{p*100:.0f}%' for p in powers])
for i, (p, n) in enumerate(zip(powers, n_needed)):
    ax.text(i, n + 5, f'n={n:.0f}', ha='center', fontsize=11, fontweight='bold')
ax.set_xlabel('Potencia deseada (1 - β)')
ax.set_ylabel('Tamaño de muestra necesario (por grupo)')
ax.set_title(f'Tamaño de muestra requerido según potencia deseada\n(effect size d = {effect_size:.3f}, α = 0.05)')
savefig(fig, '04_02_potencia_vs_n.png')

# ============================================================
# SECCIÓN 5: Comunicación de resultados
# ============================================================
print("Sección 5: Comunicación...")

# 5.1 Ejemplo de visualización limpia para comunicar
fig, ax = plt.subplots(figsize=(10, 5))
data_comm = pd.DataFrame({
    'Género': ['Varones', 'Mujeres'],
    'Mediana': [groupA.median(), groupB.median()],
    'Media': [groupA.mean(), groupB.mean()]
})
x_pos = [0, 1]
bars = ax.bar(x_pos, data_comm['Mediana']/1e6, width=0.5,
              color=['#3498db', '#e91e63'], edgecolor='white', alpha=0.85)
for i, (med, mean) in enumerate(zip(data_comm['Mediana'], data_comm['Media'])):
    ax.text(i, med/1e6 + 0.05, f'${med/1e6:.2f}M', ha='center', fontsize=14, fontweight='bold')

diff_pct = (groupA.median() - groupB.median()) / groupB.median() * 100
ax.annotate(f'Brecha: {diff_pct:.0f}%', xy=(0.5, max(data_comm['Mediana'])/1e6 * 0.85),
            fontsize=16, fontweight='bold', ha='center', color='#2c3e50',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F9E79F', alpha=0.8))
ax.set_xticks(x_pos)
ax.set_xticklabels(data_comm['Género'], fontsize=14)
ax.set_ylabel('Mediana salarial (millones ARS)')
ax.set_title('Brecha salarial de género: salario neto mensual', fontsize=15, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
savefig(fig, '05_01_comunicacion_limpia.png')

# 5.2 Mal ejemplo vs buen ejemplo
fig, axes = plt.subplots(1, 2, figsize=(16, 5.5))

# Mal ejemplo
axes[0].pie([len(groupA), len(groupB), len(df) - len(groupA) - len(groupB)],
            labels=['Varones', 'Mujeres', 'Otros'], autopct='%1.1f%%',
            colors=['#3498db', '#e91e63', '#95a5a6'])
axes[0].set_title('❌ Mal ejemplo\nUsa pie chart para datos que no lo ameritan\nNo comunica la brecha salarial', fontsize=11)

# Buen ejemplo
bp = axes[1].boxplot([groupA, groupB], labels=['Varones', 'Mujeres'],
                      patch_artist=True, showfliers=False, widths=0.5)
bp['boxes'][0].set_facecolor('#3498db')
bp['boxes'][0].set_alpha(0.6)
bp['boxes'][1].set_facecolor('#e91e63')
bp['boxes'][1].set_alpha(0.6)
for median in bp['medians']:
    median.set_color('#2c3e50')
    median.set_linewidth(2)
axes[1].yaxis.set_major_formatter(fmt_m)
axes[1].set_ylabel('Salario mensual NETO')
axes[1].set_title('✅ Buen ejemplo\nBoxplot comparativo: muestra distribución,\ncentro y dispersión de ambos grupos', fontsize=11)

fig.suptitle('Comunicación: elegir la visualización adecuada', fontsize=14, fontweight='bold', y=1.03)
fig.tight_layout()
savefig(fig, '05_02_bueno_vs_malo.png')

print(f"\n✅ Todos los gráficos generados en {os.path.abspath(IMG_DIR)}/")
