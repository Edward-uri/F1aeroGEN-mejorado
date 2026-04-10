import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Trophy, Dna, LineChart, RotateCcw, TrendingUp, TrendingDown, Gauge, Timer, Activity, ShieldCheck, Maximize2, X } from 'lucide-react'

const geneLabels = {
  aleron_delantero: 'Alerón Delantero (°)',
  aleron_trasero: 'Alerón Trasero (°)',
  barra_estabilizadora: 'Barra Estabilizadora',
  camber_frontal: 'Camber Frontal (°)',
  toe_frontal: 'Toe Frontal',
  altura_chasis: 'Altura Chasis',
}

export default function ResultsPage({ results, onReset }) {
  const [expandedGraph, setExpandedGraph] = useState(null)

  if (!results) return null

  const { mejor_individuo, fitness, tiempo_vuelta, vmax_kmh, estabilidad, config_base, graficas, nombre_pista } = results

  const diffFitness = fitness - config_base.fitness
  const diffTiempo = tiempo_vuelta - config_base.tiempo_vuelta
  const diffVmax = vmax_kmh - config_base.vmax_kmh
  const diffEstab = estabilidad - config_base.estabilidad

  const formatDiff = (val, invert = false) => {
    const positive = invert ? val < 0 : val > 0
    return (
      <div className={`diff-badge ${positive ? 'diff-up' : 'diff-down'}`}>
        {positive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
        {val > 0 ? '+' : ''}{val.toFixed(2)}
      </div>
    )
  }

  const statItems = [
    { label: 'Fitness Score', value: fitness, base: config_base.fitness, diff: diffFitness, icon: Activity },
    { label: 'Tiempo Vuelta', value: `${tiempo_vuelta}s`, base: `${config_base.tiempo_vuelta}s`, diff: diffTiempo, icon: Timer, invert: true },
    { label: 'V. Máxima', value: `${vmax_kmh} km/h`, base: `${config_base.vmax_kmh} km/h`, diff: diffVmax, icon: Gauge },
    { label: 'Estabilidad', value: `${estabilidad} Gs`, base: `${config_base.estabilidad} Gs`, diff: diffEstab, icon: ShieldCheck },
  ]

  const graphList = [
    { id: 'variables', title: 'Evolución de Variables', src: graficas.variables },
    { id: 'aptitud', title: 'Convergencia de Aptitud', src: graficas.aptitud },
    { id: 'telemetria', title: 'Telemetría Simulada', src: graficas.telemetria },
    { id: 'mapa_calor', title: 'Mapa de Calor Aerodinámico', src: graficas.mapa_calor },
  ]

  return (
    <div>
      <header style={{ textAlign: 'center', marginBottom: 48 }}>
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="section-title" 
          style={{ justifyContent: 'center', border: 'none', padding: 0 }}
        >
          <Trophy size={28} className="text-accent-secondary" /> 
          Resultados: {nombre_pista?.replace(/_/g, ' ')}
        </motion.div>
        <p style={{ color: 'var(--text-dim)', fontSize: '0.95rem' }}>
          Configuración Base vs. Optimización por Algoritmo Genético
        </p>
      </header>

      <div className="stats-grid">
        {statItems.map((s, idx) => (
          <motion.div 
            key={s.label}
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <div className="stat-card-label">
              <s.icon size={16} style={{ verticalAlign: 'middle', marginRight: 8, opacity: 0.6 }} />
              {s.label}
            </div>
            <div className="stat-card-value">{s.value}</div>
            <div className="stat-card-base">Base: {s.base}</div>
            {formatDiff(s.diff, s.invert)}
          </motion.div>
        ))}
      </div>

      <div className="config-layout" style={{ marginBottom: 48 }}>
        <section className="table-container" style={{ marginBottom: 0 }}>
          <div className="panel-header" style={{ padding: '24px 24px 0' }}>
            <Dna size={20} className="text-accent" />
            <h3>Genotipo del Campeón</h3>
          </div>
          <table className="modern-table">
            <thead>
              <tr>
                <th>Variable (Gen)</th>
                <th>Config. Base</th>
                <th>Mejor AG</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(mejor_individuo).map(([key, val]) => (
                <tr key={key}>
                  <td className="stat-label">{geneLabels[key] || key}</td>
                  <td className="gene-val-base">
                    {key === 'aleron_delantero' || key === 'aleron_trasero' ? '25°' :
                      key === 'barra_estabilizadora' ? '10' :
                      key === 'camber_frontal' ? '-3.00°' :
                      key === 'toe_frontal' ? '0.25' :
                      key === 'altura_chasis' ? '25' : '-'}
                  </td>
                  <td className="gene-val-ag">
                    {typeof val === 'number' ? (Number.isInteger(val) ? val : val.toFixed(2)) : val}
                    { (key.includes('aleron') || key.includes('camber')) ? '°' : '' }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <aside className="glass-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
          <Trophy size={60} className="text-accent" style={{ marginBottom: 20, opacity: 0.2 }} />
          <h3 style={{ marginBottom: 12 }}>¡Optimización Completada!</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 32 }}>
            El algoritmo ha convergido en una configuración superior tras {results.n_generaciones || 25} generaciones.
          </p>
          <button className="btn-base btn-main" onClick={onReset} style={{ width: '100%' }}>
            <RotateCcw size={18} /> Nuevo Escenario
          </button>
        </aside>
      </div>

      <div className="panel-header">
        <LineChart size={22} className="text-accent" />
        <h3>Análisis y Telemetría</h3>
      </div>
      
      <div className="graphs-grid">
        {graphList.map((g, idx) => (
          <motion.div 
            key={g.id}
            className="graph-card" 
            whileHover={{ y: -5 }}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.1 }}
          >
            <button className="graph-expand-btn" onClick={() => setExpandedGraph(g)}>
              <Maximize2 size={16} />
            </button>
            <h4>{g.title}</h4>
            <img 
              src={g.src} 
              alt={g.title} 
              className="graph-img" 
              onClick={() => setExpandedGraph(g)}
              style={{ cursor: 'zoom-in' }}
            />
          </motion.div>
        ))}
      </div>

      {/* Expanded Modal */}
      <AnimatePresence>
        {expandedGraph && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setExpandedGraph(null)}
          >
            <motion.div 
              className="modal-content"
              initial={{ scale: 0.8, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 20 }}
              onClick={e => e.stopPropagation()}
            >
              <button className="modal-close" onClick={() => setExpandedGraph(null)}>
                <X size={20} />
              </button>
              <div className="modal-header">
                <div className="modal-title">{expandedGraph.title}</div>
              </div>
              <img src={expandedGraph.src} alt={expandedGraph.title} className="modal-img" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
