import matplotlib.pyplot as plt
import io
import os
import numpy as np

class Visualizer:
    def __init__(self, style_dir='styles'):
        self.style_dir = style_dir

    def set_style(self, style_name):
        """Sets the matplotlib style."""
        # Check if style_dir is absolute or relative
        if os.path.isabs(self.style_dir):
            style_path = os.path.join(self.style_dir, f'{style_name}.mplstyle')
        else:
            # Assuming style_dir is relative to the project root or current working dir
            style_path = os.path.abspath(os.path.join(os.getcwd(), self.style_dir, f'{style_name}.mplstyle'))

        if os.path.exists(style_path):
            plt.style.use(style_path)
        else:
            print(f"Style file not found: {style_path}. Using fallback.")
            if style_name == 'nature':
                plt.style.use('seaborn-v0_8-white' if 'seaborn-v0_8-white' in plt.style.available else 'classic')
            else:
                plt.style.use('ggplot')

    def plot_semilog_jv(self, df, ax, title="Dark IV"):
        """Plots Semi-log J-V curve."""
        # Filter positive J for log plot
        mask = df['J'] > 0
        df_pos = df[mask]
        
        ax.semilogy(df_pos['V'], df_pos['J'], 'o', alpha=0.5, label='Raw Data')
        if 'J_smooth' in df.columns:
             # Plot smooth line
             mask_smooth = df['J_smooth'] > 0
             ax.semilogy(df[mask_smooth]['V'], df[mask_smooth]['J_smooth'], '-', label='Smoothed')
             
        ax.set_xlabel('Voltage (V)')
        ax.set_ylabel('Current Density (A/cm$^2$)')
        ax.set_title(title)
        ax.legend()

    def plot_ideality_factor(self, df, ax, title="Ideality Factor"):
        """Plots n vs V."""
        if 'n_local' in df.columns:
            # Filter reasonable range
            mask = (df['n_local'] > 0) & (df['n_local'] < 10) & (df['V'] > 0)
            df_plot = df[mask]
            
            ax.plot(df_plot['V'], df_plot['n_local'], '-', linewidth=2)
            ax.axhline(1, color='gray', linestyle='--', alpha=0.5, label='n=1')
            ax.axhline(2, color='gray', linestyle='--', alpha=0.5, label='n=2')
            
            ax.set_xlabel('Voltage (V)')
            ax.set_ylabel('Ideality Factor (n)')
            ax.set_ylim(0, 5)
            ax.set_title(title)
            ax.legend()
        else:
            ax.text(0.5, 0.5, "n(V) not available", ha='center', va='center')
    
    def plot_differential_resistance(self, df, ax, title="Differential Resistance"):
        """Plots Rdiff vs V."""
        if 'R_diff' in df.columns:
            # Filter reasonable range and positive voltage
            mask = (df['V'] > 0.1) & (np.isfinite(df['R_diff']))
            df_plot = df[mask]
            
            if len(df_plot) > 0:
                ax.semilogy(df_plot['V'], df_plot['R_diff'].abs(), '-', linewidth=2)
                ax.set_xlabel('Voltage (V)')
                ax.set_ylabel('|Differential Resistance| (Ω·cm²)')
                ax.set_title(title)
                ax.grid(True, alpha=0.3)
            else:
                ax.text(0.5, 0.5, "No valid Rdiff data", ha='center', va='center')
        else:
            ax.text(0.5, 0.5, "Rdiff not calculated", ha='center', va='center')

    def get_image_stream(self, fig, format='png', dpi=300):
        """Returns the figure as a BytesIO stream."""
        img_stream = io.BytesIO()
        fig.savefig(img_stream, format=format, dpi=dpi, bbox_inches='tight')
        img_stream.seek(0)
        return img_stream
