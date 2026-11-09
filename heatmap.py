import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ============================
# Load lattice CSV
# ============================
df = pd.read_csv("fare_lattice_results.csv")

# Helper function to pivot metric into heatmap format
def make_pivot(metric):
    return df.pivot(index="time_level", columns="loc_level", values=metric)


# ============================
# Create 3 subplots (MAE, RMSE, R²)
# ============================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

metrics = [
    ("mae", "Mean Absolute Error (MAE)"),
    ("rmse", "Root Mean Squared Error (RMSE)"),
    ("r2", "R² Score"),
]

for ax, (metric, title) in zip(axes, metrics):
    heatmap_data = make_pivot(metric)
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".3f",
        cmap="viridis",
        linewidths=0.5,
        cbar_kws={"label": title},
        ax=ax
    )
    ax.set_title(title)
    ax.set_xlabel("Location Generalization Level")
    ax.set_ylabel("Time Generalization Level")

plt.tight_layout()
plt.savefig("fare_lattice_heatmaps_all.png", dpi=300)
plt.show()
