"""
IPM (Information Processing & Management) journal-style SHAP figures.
Key adjustments from v1:
  - No title embedded in figure (title goes in caption below the figure)
  - Times New Roman font throughout
  - Color-blind friendly palette (cividis for continuous, muted blue/red for diverging)
  - Minimalist grid, thin axis lines
  - Consistent figure sizing
  - Publication-ready: 300 dpi, tight layout
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.ensemble import GradientBoostingRegressor
import warnings
warnings.filterwarnings('ignore')

# ============ IPM journal style ============
mpl.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'axes.linewidth': 0.8,
    'axes.edgecolor': '#333333',
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'legend.fontsize': 9,
    'legend.frameon': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.unicode_minus': False,
})

# ============ Load data ============
df = pd.read_pickle('data_ready.pkl')

features = ['Focal_GenAI_Index', 'Focal_RnD_Ratio', 'Power_Pressure',
            'Focal_Size', 'Focal_Lev', 'Focal_Age', 'Focal_CashFlow',
            'Focal_SoE', 'Focal_HHI',
            'Partner_Size', 'Partner_Lev', 'Partner_ROA']
target = 'Focal_ROA'

for c in features + [target]:
    q_low = df[c].quantile(0.01)
    q_hi  = df[c].quantile(0.99)
    df[c] = df[c].clip(q_low, q_hi)

sub = df[features + [target]].dropna().copy()
X = sub[features].values
y = sub[target].values

# ============ Train model ============
model = GradientBoostingRegressor(
    n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42
)
model.fit(X, y)

# ============ Compute tree SHAP ============
def fast_tree_shap(model, X):
    n, p = X.shape
    contribs = np.zeros((n, p))
    lr = model.learning_rate
    for est_idx in range(model.n_estimators_):
        tree = model.estimators_[est_idx, 0].tree_
        for i in range(n):
            node = 0
            while tree.children_left[node] != -1:
                feat = tree.feature[node]
                thresh = tree.threshold[node]
                parent_value = tree.value[node, 0, 0]
                if X[i, feat] <= thresh:
                    child = tree.children_left[node]
                else:
                    child = tree.children_right[node]
                child_value = tree.value[child, 0, 0]
                contribs[i, feat] += (child_value - parent_value) * lr
                node = child
    return contribs

print("Computing SHAP values...")
shap_values = fast_tree_shap(model, X)
baseline = model.predict(X).mean() - shap_values.sum(axis=1).mean()
print(f"Baseline: {baseline:.4f}")

# Colorblind-friendly diverging palette for SHAP (journal safe)
DIVERGING = mpl.colors.LinearSegmentedColormap.from_list(
    'ipm_diverging',
    ['#1f4e79', '#6c8ebf', '#c5c5c5', '#d67373', '#a62c2c'],
    N=256
)
# Monochrome bar color (classic academic style)
BAR_COLOR = '#4a6fa5'
POS_COLOR = '#a62c2c'
NEG_COLOR = '#1f4e79'
GRID_COLOR = '#dddddd'

display_names = features  # keep variable names for academic clarity

# ==================== Figure 10: Bar plot ====================
mean_abs = np.abs(shap_values).mean(axis=0)
order = np.argsort(mean_abs)[::-1]

fig, ax = plt.subplots(figsize=(6.5, 4))
ax.barh([display_names[i] for i in order[::-1]],
        mean_abs[order[::-1]],
        color=BAR_COLOR, edgecolor='black', linewidth=0.4, height=0.65)
ax.set_xlabel('Mean |SHAP value|', fontsize=10)
ax.grid(axis='x', linestyle=':', color=GRID_COLOR, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# Annotate values
for i, v in enumerate(mean_abs[order[::-1]]):
    ax.text(v + max(mean_abs)*0.01, i, f'{v:.4f}', va='center', fontsize=8, color='#333333')
ax.set_xlim(0, max(mean_abs) * 1.15)
plt.savefig('figure10_feature_importance_ipm.png')
plt.close()
print("figure10 (IPM style) saved")

# ==================== Figure 11: Beeswarm ====================
order = np.argsort(mean_abs)[::-1]
fig, ax = plt.subplots(figsize=(7, 5))
for i, feat_idx in enumerate(order):
    y_pos = len(order) - i - 1
    sv = shap_values[:, feat_idx]
    fv = X[:, feat_idx]
    fv_norm = (fv - fv.min()) / (fv.max() - fv.min() + 1e-9)
    jitter = np.random.RandomState(42 + i).uniform(-0.22, 0.22, len(sv))
    sc = ax.scatter(sv, [y_pos + j for j in jitter],
                    c=fv_norm, cmap=DIVERGING, s=7, alpha=0.7,
                    edgecolors='none')
ax.axvline(0, color='black', linewidth=0.6)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([display_names[i] for i in order[::-1]], fontsize=9)
ax.set_xlabel('SHAP value', fontsize=10)
ax.grid(axis='x', linestyle=':', color=GRID_COLOR, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
cbar = plt.colorbar(sc, ax=ax, shrink=0.7, pad=0.02, aspect=30)
cbar.set_label('Feature value', fontsize=9)
cbar.ax.tick_params(labelsize=8)
cbar.outline.set_linewidth(0.5)
cbar.set_ticks([0, 0.5, 1])
cbar.set_ticklabels(['Low', 'Mid', 'High'])
plt.savefig('figure11_beeswarm_ipm.png')
plt.close()
print("figure11 (IPM style) saved")

# ==================== Figure 12: Dependence plot for GenAI ====================
genai_idx = features.index('Focal_GenAI_Index')
rd_idx = features.index('Focal_RnD_Ratio')

fig, ax = plt.subplots(figsize=(6, 4))
sc = ax.scatter(X[:, genai_idx], shap_values[:, genai_idx],
                c=X[:, rd_idx], cmap=DIVERGING, s=18, alpha=0.7,
                edgecolors='black', linewidth=0.2)
ax.axhline(0, color='black', linewidth=0.6, linestyle='--', dashes=(5, 3))
ax.set_xlabel('Focal_GenAI_Index', fontsize=10)
ax.set_ylabel('SHAP value for Focal_GenAI_Index', fontsize=10)
ax.grid(linestyle=':', color=GRID_COLOR, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
cbar = plt.colorbar(sc, ax=ax, shrink=0.85, pad=0.02)
cbar.set_label('Focal_RnD_Ratio', fontsize=9)
cbar.ax.tick_params(labelsize=8)
cbar.outline.set_linewidth(0.5)
plt.savefig('figure12_genai_dependence_ipm.png')
plt.close()
print("figure12 (IPM style) saved")

# ==================== Figure 13: GenAI × R&D interaction ====================
fig, ax = plt.subplots(figsize=(6, 4))
sc = ax.scatter(X[:, genai_idx], shap_values[:, genai_idx],
                c=X[:, rd_idx], cmap=DIVERGING, s=18, alpha=0.75,
                edgecolors='black', linewidth=0.2)
ax.axhline(0, color='black', linewidth=0.6, linestyle='--', dashes=(5, 3))
ax.set_xlabel('Focal_GenAI_Index', fontsize=10)
ax.set_ylabel('SHAP value for Focal_GenAI_Index', fontsize=10)
ax.grid(linestyle=':', color=GRID_COLOR, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
cbar = plt.colorbar(sc, ax=ax, shrink=0.85, pad=0.02)
cbar.set_label('Focal_RnD_Ratio', fontsize=9)
cbar.ax.tick_params(labelsize=8)
cbar.outline.set_linewidth(0.5)
plt.savefig('figure13_genai_rd_interaction_ipm.png')
plt.close()
print("figure13 (IPM style) saved")

# ==================== Figure 14: GenAI × Power_Pressure ====================
pp_idx = features.index('Power_Pressure')
fig, ax = plt.subplots(figsize=(6, 4))
sc = ax.scatter(X[:, genai_idx], shap_values[:, genai_idx],
                c=X[:, pp_idx], cmap=DIVERGING, s=18, alpha=0.75,
                edgecolors='black', linewidth=0.2)
ax.axhline(0, color='black', linewidth=0.6, linestyle='--', dashes=(5, 3))
ax.set_xlabel('Focal_GenAI_Index', fontsize=10)
ax.set_ylabel('SHAP value for Focal_GenAI_Index', fontsize=10)
ax.grid(linestyle=':', color=GRID_COLOR, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
cbar = plt.colorbar(sc, ax=ax, shrink=0.85, pad=0.02)
cbar.set_label('Power_Pressure', fontsize=9)
cbar.ax.tick_params(labelsize=8)
cbar.outline.set_linewidth(0.5)
plt.savefig('figure14_genai_power_interaction_ipm.png')
plt.close()
print("figure14 (IPM style) saved")

# ==================== Figure 15: Force plot (waterfall-style) ====================
idx = np.argmax(X[:, genai_idx])
sv = shap_values[idx]
fv = X[idx]
pred = model.predict(X[idx:idx+1])[0]

order = np.argsort(np.abs(sv))[::-1]
contrib_names = [f"{display_names[i]} = {fv[i]:.3f}" for i in order]
contrib_vals = sv[order]

fig, ax = plt.subplots(figsize=(7.5, 4.5))
colors = [POS_COLOR if v > 0 else NEG_COLOR for v in contrib_vals]
bars = ax.barh(range(len(contrib_vals))[::-1], contrib_vals,
               color=colors, edgecolor='black', linewidth=0.4, height=0.7)
ax.set_yticks(range(len(contrib_vals))[::-1])
ax.set_yticklabels(contrib_names, fontsize=8)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_xlabel('SHAP contribution to predicted ROA', fontsize=10)
ax.grid(axis='x', linestyle=':', color=GRID_COLOR, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Expand x-limits to avoid label overlap
xmax = max(abs(contrib_vals))
ax.set_xlim(-xmax * 1.35, xmax * 1.35)

# Value annotations - always outside the bar
for i, (bar, val) in enumerate(zip(bars, contrib_vals)):
    offset = xmax * 0.02
    x_pos = val + (offset if val > 0 else -offset)
    ha = 'left' if val > 0 else 'right'
    ax.text(x_pos, bar.get_y() + bar.get_height()/2, f'{val:+.4f}',
            va='center', ha=ha, fontsize=8, color='#222222')

# Footnote-style annotation
ax.text(0.99, 0.02,
        f'Baseline E[f(X)] = {baseline:.4f}   |   f(x) = {pred:.4f}',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=8,
        style='italic', color='#555555')

plt.savefig('figure15_force_plot_ipm.png')
plt.close()
print("figure15 (IPM style) saved")

print("\nAll IPM-style figures saved successfully.")
