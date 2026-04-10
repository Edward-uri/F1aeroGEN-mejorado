import matplotlib.pyplot as plt
import numpy as np
import math

class Visualizer:
    
    @staticmethod
    def plot_convergencia(historial_mejor, historial_media, historial_peor):
        plt.figure(figsize=(10, 5))
        plt.plot(historial_mejor, label='Mejor Aptitud (Elitismo)', color='#2ca02c', linewidth=2.5)
        plt.plot(historial_media, label='Media de la Población', color='#1f77b4', alpha=0.8)
        plt.plot(historial_peor, label='Peor Aptitud', color='#d62728', linestyle='--', alpha=0.6)

        plt.title('Evolución de Setups de F1 (Algoritmo Genético)', fontsize=14, pad=15)
        plt.xlabel('Generaciones', fontsize=12)
        plt.ylabel('Puntuación de Aptitud (Fitness)', fontsize=12)
        plt.legend(loc='lower right')
        plt.grid(True, linestyle=":", alpha=0.7)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_evolucion_variables(historial_vmax, historial_ecurva, historial_tlap):
        fig, axs = plt.subplots(3, 1, figsize=(10, 10))
        
        axs[0].plot(historial_vmax, color='#ff7f0e', linewidth=2)
        axs[0].set_title('Evolución de Velocidad Máxima ($V_{max}$)', fontsize=12)
        axs[0].set_ylabel('m/s')
        axs[0].grid(True, linestyle=":", alpha=0.7)
        
        axs[1].plot(historial_ecurva, color='#2ca02c', linewidth=2)
        axs[1].set_title('Evolución de Estabilidad en Curva ($E_{curva}$)', fontsize=12)
        axs[1].set_ylabel('Fuerzas G')
        axs[1].grid(True, linestyle=":", alpha=0.7)
        
        axs[2].plot(historial_tlap, color='#d62728', linewidth=2)
        axs[2].set_title('Evolución del Tiempo de Vuelta ($T_{lap}$)', fontsize=12)
        axs[2].set_xlabel('Generaciones')
        axs[2].set_ylabel('Segundos')
        axs[2].grid(True, linestyle=":", alpha=0.7)
        
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_telemetria_simulada(evaluador, genes_base, genes_campeon, nombre_pista="Circuito"):
        """
        Simula una vuelta completa segmentando la pista en tramos alternos
        de recta y curva. Grafica Velocidad vs Distancia para ambos setups.
        """
        d_rectas = evaluador.d_rectas
        d_curvas = evaluador.d_curvas

        n_segmentos = 8
        longitud_recta_seg = d_rectas / (n_segmentos // 2)
        longitud_curva_seg = d_curvas / (n_segmentos // 2)

        vmax_base = evaluador.calcular_vmax(genes_base)
        ecurva_base = evaluador.calcular_estabilidad(genes_base)
        vcurva_base = math.sqrt(ecurva_base * evaluador.GRAVEDAD * evaluador.r_curva)

        vmax_ag = evaluador.calcular_vmax(genes_campeon)
        ecurva_ag = evaluador.calcular_estabilidad(genes_campeon)
        vcurva_ag = math.sqrt(ecurva_ag * evaluador.GRAVEDAD * evaluador.r_curva)

        dist_puntos = []
        vel_base = []
        vel_ag = []
        dist_acum = 0.0

        for i in range(n_segmentos):
            if i % 2 == 0:
                long_seg = longitud_recta_seg
                puntos = np.linspace(0, long_seg, 50)
                for p in puntos:
                    dist_puntos.append(dist_acum + p)
                    factor = min(1.0, (p / long_seg) * 1.3)
                    vel_base.append((vmax_base * 0.85 + (vmax_base * 0.15) * factor) * 3.6)
                    vel_ag.append((vmax_ag * 0.85 + (vmax_ag * 0.15) * factor) * 3.6)
            else:
                long_seg = longitud_curva_seg
                puntos = np.linspace(0, long_seg, 50)
                for p in puntos:
                    dist_puntos.append(dist_acum + p)
                    ratio = p / long_seg
                    if ratio < 0.15:
                        factor = 1.0 - (0.15 - ratio) * 3
                        vel_base.append(max(vcurva_base, vmax_base * factor) * 3.6)
                        vel_ag.append(max(vcurva_ag, vmax_ag * factor) * 3.6)
                    elif ratio > 0.85:
                        factor = (ratio - 0.85) * 3
                        vel_base.append((vcurva_base + (vmax_base - vcurva_base) * factor) * 3.6)
                        vel_ag.append((vcurva_ag + (vmax_ag - vcurva_ag) * factor) * 3.6)
                    else:
                        vel_base.append(vcurva_base * 3.6)
                        vel_ag.append(vcurva_ag * 3.6)
            dist_acum += long_seg

        plt.figure(figsize=(14, 5))
        plt.plot(dist_puntos, vel_base, color='#888888', linewidth=2, label='Config. Base (Estándar)', alpha=0.8)
        plt.plot(dist_puntos, vel_ag, color='#e74c3c', linewidth=2.5, label='Mejor Individuo (AG)')
        plt.fill_between(dist_puntos, vel_base, vel_ag, alpha=0.15, color='green',
                         where=[a > b for a, b in zip(vel_ag, vel_base)], label='AG supera a Base')
        plt.fill_between(dist_puntos, vel_base, vel_ag, alpha=0.15, color='red',
                         where=[a < b for a, b in zip(vel_ag, vel_base)])

        dist_acum2 = 0.0
        for i in range(n_segmentos):
            long = longitud_recta_seg if i % 2 == 0 else longitud_curva_seg
            color_bg = '#e8f5e9' if i % 2 == 0 else '#fce4ec'
            plt.axvspan(dist_acum2, dist_acum2 + long, alpha=0.12, color=color_bg)
            etiqueta = 'R' if i % 2 == 0 else 'C'
            plt.text(dist_acum2 + long / 2, max(vel_ag) * 0.98, etiqueta,
                     ha='center', fontsize=9, color='gray', alpha=0.6)
            dist_acum2 += long

        plt.title(f'Telemetría Simulada: Velocidad vs Distancia — {nombre_pista}', fontsize=13, pad=12)
        plt.xlabel('Distancia recorrida (m)', fontsize=11)
        plt.ylabel('Velocidad (km/h)', fontsize=11)
        plt.legend(loc='lower right')
        plt.grid(True, linestyle=":", alpha=0.5)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_mapa_calor_aero(evaluador, genes_campeon):
        """
        Mapa de calor 2D que muestra la distribución de carga aerodinámica
        para diferentes combinaciones de alerón delantero y trasero.
        """
        rango = range(1, 51)
        mapa = np.zeros((50, 50))

        for fw in rango:
            _, cl_fw = evaluador._obtener_coeficientes_aero(fw)
            for rw in rango:
                _, cl_rw = evaluador._obtener_coeficientes_aero(rw)
                mapa[rw - 1, fw - 1] = cl_fw - cl_rw

        fig, ax = plt.subplots(figsize=(9, 8))

        im = ax.imshow(mapa, cmap='Spectral_r', origin='lower', extent=[1, 50, 1, 50],
                       aspect='auto', interpolation='bicubic')

        X, Y = np.meshgrid(np.linspace(1, 50, 50), np.linspace(1, 50, 50))
        contornos = ax.contour(X, Y, mapa, levels=8, colors='black', alpha=0.2, linewidths=0.6)
        ax.clabel(contornos, inline=True, fontsize=7, fmt='%.2f')

        cbar = plt.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
        cbar.set_label('Balance Aerodinámico  (+ Sobreviraje / − Subviraje)', fontsize=10)

        fw_c = genes_campeon['aleron_delantero']
        rw_c = genes_campeon['aleron_trasero']
        ax.plot(fw_c, rw_c, 'D', color='#FFD700', markersize=14, markeredgecolor='black',
                markeredgewidth=2.0, label=f'Mejor Individuo ({fw_c}°, {rw_c}°)', zorder=5)
        ax.plot(fw_c, rw_c, 'o', color='#FFD700', markersize=28, alpha=0.25, zorder=4)

        ax.plot([1, 50], [1, 50], color='white', linestyle='--', alpha=0.7,
                linewidth=1.5, label='Equilibrio Neutro (F = R)')

        ax.text(12, 42, 'SUBVIRAJE\n(Difícil girar)', fontsize=12, color='white',
                ha='center', fontweight='bold', style='italic',
                bbox=dict(facecolor='#1a237e', alpha=0.65, edgecolor='none', boxstyle='round,pad=0.4'))
        ax.text(40, 8, 'SOBREVIRAJE\n(Cola inestable)', fontsize=12, color='white',
                ha='center', fontweight='bold', style='italic',
                bbox=dict(facecolor='#b71c1c', alpha=0.65, edgecolor='none', boxstyle='round,pad=0.4'))

        ax.set_title('Mapa de Calor: Balance Aerodinámico del Monoplaza', fontsize=14, pad=14, fontweight='bold')
        ax.set_xlabel('Ángulo Alerón Delantero (°)', fontsize=11)
        ax.set_ylabel('Ángulo Alerón Trasero (°)', fontsize=11)
        ax.legend(loc='upper left', fontsize=9, framealpha=0.85)
        plt.tight_layout()
        plt.show()
