import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64


def _fig_to_base64():
    """Convierte la figura actual de matplotlib a una cadena base64 PNG."""
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e', edgecolor='none')
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return f"data:image/png;base64,{img_b64}"


class Visualizer:

    @staticmethod
    def plot_convergencia(historial_mejor, historial_media, historial_peor):
        plt.figure(figsize=(10, 5), facecolor='#1a1a2e')
        ax = plt.gca()
        ax.set_facecolor('#1a1a2e')
        plt.plot(historial_mejor, label='Mejor Aptitud (Elitismo)', color='#2ca02c', linewidth=2.5)
        plt.plot(historial_media, label='Media de la Población', color='#1f77b4', alpha=0.8)
        plt.plot(historial_peor, label='Peor Aptitud', color='#d62728', linestyle='--', alpha=0.6)
        plt.title('Evolución de Setups de F1 (Algoritmo Genético)', fontsize=14, pad=15, color='white')
        plt.xlabel('Generaciones', fontsize=12, color='#a0a0a0')
        plt.ylabel('Puntuación de Aptitud (Fitness)', fontsize=12, color='#a0a0a0')
        plt.legend(loc='lower right', facecolor='#2a2a3e', edgecolor='#444', labelcolor='white')
        plt.grid(True, linestyle=":", alpha=0.3, color='#555')
        ax.tick_params(colors='#a0a0a0')
        plt.tight_layout()
        return _fig_to_base64()

    @staticmethod
    def plot_evolucion_variables(historial_vmax, historial_ecurva, historial_tlap):
        fig, axs = plt.subplots(3, 1, figsize=(10, 10), facecolor='#1a1a2e')
        for ax in axs:
            ax.set_facecolor('#1a1a2e')
            ax.tick_params(colors='#a0a0a0')

        axs[0].plot(historial_vmax, color='#ff7f0e', linewidth=2)
        axs[0].set_title('Evolución de Velocidad Máxima ($V_{max}$)', fontsize=12, color='white')
        axs[0].set_ylabel('m/s', color='#a0a0a0')
        axs[0].grid(True, linestyle=":", alpha=0.3, color='#555')

        axs[1].plot(historial_ecurva, color='#2ca02c', linewidth=2)
        axs[1].set_title('Evolución de Estabilidad en Curva ($E_{curva}$)', fontsize=12, color='white')
        axs[1].set_ylabel('Fuerzas G', color='#a0a0a0')
        axs[1].grid(True, linestyle=":", alpha=0.3, color='#555')

        axs[2].plot(historial_tlap, color='#d62728', linewidth=2)
        axs[2].set_title('Evolución del Tiempo de Vuelta ($T_{lap}$)', fontsize=12, color='white')
        axs[2].set_xlabel('Generaciones', color='#a0a0a0')
        axs[2].set_ylabel('Segundos', color='#a0a0a0')
        axs[2].grid(True, linestyle=":", alpha=0.3, color='#555')

        plt.tight_layout()
        return _fig_to_base64()

    @staticmethod
    def plot_telemetria_simulada(evaluador, genes_base, genes_campeon, nombre_pista="Circuito",
                                 trazo_real=None, tiempo_real=None):
        # Trazos reales del simulador de vuelta (aceleración + frenado por segmento)
        t_base, trazo_base = evaluador.simular_vuelta(genes_base)
        t_ag, trazo_ag = evaluador.simular_vuelta(genes_campeon)

        dist_puntos = [p[0] for p in trazo_base]
        vel_base = [p[1] * 3.6 for p in trazo_base]
        # el trazo del AG se interpola sobre la malla del base para poder sombrear
        vel_ag = np.interp(dist_puntos, [p[0] for p in trazo_ag],
                           [p[1] * 3.6 for p in trazo_ag])

        plt.figure(figsize=(14, 5), facecolor='#1a1a2e')
        ax = plt.gca()
        ax.set_facecolor('#1a1a2e')
        plt.plot(dist_puntos, vel_base, color='#888888', linewidth=2, label=f'Config. Base ({t_base:.1f}s)', alpha=0.8)
        plt.plot(dist_puntos, vel_ag, color='#e10600', linewidth=2.5, label=f'Mejor Individuo AG ({t_ag:.1f}s)')
        plt.fill_between(dist_puntos, vel_base, vel_ag, alpha=0.15, color='#2ca02c',
                         where=[a > b for a, b in zip(vel_ag, vel_base)], label='AG supera')
        plt.fill_between(dist_puntos, vel_base, vel_ag, alpha=0.1, color='red',
                         where=[a < b for a, b in zip(vel_ag, vel_base)])

        # Vuelta real capturada del juego por UDP (velocidades ya en km/h)
        if trazo_real:
            etiqueta = f'Telemetría Real F1 ({tiempo_real:.1f}s)' if tiempo_real else 'Telemetría Real F1'
            plt.plot([p[0] for p in trazo_real], [p[1] for p in trazo_real],
                     color='#00d2ff', linewidth=1.3, alpha=0.9, label=etiqueta)

        dist_acum2 = 0.0
        for i in range(evaluador.n_pares * 2):
            long = evaluador.long_recta_seg if i % 2 == 0 else evaluador.long_curva_seg
            color_bg = '#1e3a1e' if i % 2 == 0 else '#3a1e1e'
            plt.axvspan(dist_acum2, dist_acum2 + long, alpha=0.15, color=color_bg)
            if evaluador.n_pares <= 8:
                etiqueta = 'R' if i % 2 == 0 else 'C'
                plt.text(dist_acum2 + long / 2, max(vel_ag) * 0.98, etiqueta,
                         ha='center', fontsize=9, color='#666', alpha=0.7)
            dist_acum2 += long

        plt.title(f'Telemetría Simulada — {nombre_pista}', fontsize=13, pad=12, color='white')
        plt.xlabel('Distancia (m)', fontsize=11, color='#a0a0a0')
        plt.ylabel('Velocidad (km/h)', fontsize=11, color='#a0a0a0')
        plt.legend(loc='lower right', facecolor='#2a2a3e', edgecolor='#444', labelcolor='white')
        plt.grid(True, linestyle=":", alpha=0.2, color='#555')
        ax.tick_params(colors='#a0a0a0')
        plt.tight_layout()
        return _fig_to_base64()

    @staticmethod
    def plot_mapa_calor_aero(evaluador, genes_campeon):
        rango = range(1, 51)
        mapa = np.zeros((50, 50))
        for fw in rango:
            _, cl_fw = evaluador._obtener_coeficientes_aero(fw)
            for rw in rango:
                _, cl_rw = evaluador._obtener_coeficientes_aero(rw)
                mapa[rw - 1, fw - 1] = cl_fw - cl_rw

        fig, ax = plt.subplots(figsize=(9, 8), facecolor='#1a1a2e')
        ax.set_facecolor('#1a1a2e')
        im = ax.imshow(mapa, cmap='Spectral_r', origin='lower', extent=[1, 50, 1, 50],
                       aspect='auto', interpolation='bicubic')
        X, Y = np.meshgrid(np.linspace(1, 50, 50), np.linspace(1, 50, 50))
        contornos = ax.contour(X, Y, mapa, levels=8, colors='white', alpha=0.15, linewidths=0.5)
        cbar = plt.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
        cbar.set_label('Balance Aero (+ Sobreviraje / − Subviraje)', fontsize=10, color='#a0a0a0')
        cbar.ax.tick_params(colors='#a0a0a0')

        fw_c = genes_campeon['aleron_delantero']
        rw_c = genes_campeon['aleron_trasero']
        ax.plot(fw_c, rw_c, 'D', color='#FFD700', markersize=14, markeredgecolor='black',
                markeredgewidth=2.0, label=f'Campeón ({fw_c}°, {rw_c}°)', zorder=5)
        ax.plot(fw_c, rw_c, 'o', color='#FFD700', markersize=28, alpha=0.25, zorder=4)
        ax.plot([1, 50], [1, 50], color='white', linestyle='--', alpha=0.5, linewidth=1.5, label='Equilibrio Neutro')
        ax.text(12, 42, 'SUBVIRAJE', fontsize=11, color='white', ha='center', fontweight='bold',
                bbox=dict(facecolor='#1a237e', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.3'))
        ax.text(40, 8, 'SOBREVIRAJE', fontsize=11, color='white', ha='center', fontweight='bold',
                bbox=dict(facecolor='#b71c1c', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.3'))
        ax.set_title('Mapa de Calor Aerodinámico', fontsize=14, pad=14, fontweight='bold', color='white')
        ax.set_xlabel('Alerón Delantero (°)', fontsize=11, color='#a0a0a0')
        ax.set_ylabel('Alerón Trasero (°)', fontsize=11, color='#a0a0a0')
        ax.tick_params(colors='#a0a0a0')
        ax.legend(loc='upper left', fontsize=9, facecolor='#2a2a3e', edgecolor='#444', labelcolor='white')
        plt.tight_layout()
        return _fig_to_base64()
