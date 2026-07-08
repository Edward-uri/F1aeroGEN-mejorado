import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sliders, ClipboardList, MoveLeft, Play, Radio } from 'lucide-react'
import { evolucionar, telemetriaIniciar, telemetriaDetener, telemetriaEstado } from '../api'

const sliders = [
  { key: 'p_initial', label: 'Población Inicial', min: 5, max: 50, step: 1 },
  { key: 'p_max', label: 'Población Máxima', min: 10, max: 100, step: 5 },
  { key: 'p_cruza', label: 'Probabilidad de Cruza', min: 0.1, max: 1.0, step: 0.05 },
  { key: 'p_mut_i', label: 'Prob. Mutación (Individuo)', min: 0.05, max: 0.80, step: 0.05 },
  { key: 'p_mut_gen', label: 'Prob. Mutación (Gen)', min: 0.05, max: 0.50, step: 0.05 },
  { key: 'n_generaciones', label: 'Número de Generaciones', min: 5, max: 100, step: 5 },
  { key: 'paciencia', label: 'Paciencia (paro por convergencia, 0 = off)', min: 0, max: 30, step: 1 },
]

export default function ConfigPage({ selection, config, setConfig, onBack, onResults }) {
  const [loading, setLoading] = useState(false)
  const [capturando, setCapturando] = useState(false)
  const [telemetria, setTelemetria] = useState(null)
  const [usarTelemetria, setUsarTelemetria] = useState(false)

  useEffect(() => {
    if (!capturando) return
    const id = setInterval(() => {
      telemetriaEstado().then(setTelemetria).catch(() => {})
    }, 2000)
    return () => clearInterval(id)
  }, [capturando])

  const toggleCaptura = async () => {
    try {
      const estado = capturando ? await telemetriaDetener() : await telemetriaIniciar()
      setTelemetria(estado)
      setCapturando(!capturando)
    } catch (err) {
      console.error('Error:', err)
      alert('No se pudo hablar con el backend de telemetría.')
    }
  }

  const vueltasCompletas = telemetria?.vueltas?.filter(v => v.tiempo_s)?.length ?? 0

  const handleRun = async () => {
    setLoading(true)
    try {
      const params = {
        pista_id: selection.pista.id,
        coche_id: selection.coche.id,
        km_actual: 0,
        compuesto: selection.compuesto,
        incluir_telemetria_real: usarTelemetria,
        ...config,
      }
      const data = await evolucionar(params)
      onResults(data)
    } catch (err) {
      console.error('Error:', err)
      alert('Error al conectar con el backend. ¿Está corriendo uvicorn?')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loader-container">
        <div className="racing-loader" />
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ repeat: Infinity, duration: 1, repeatType: 'reverse' }}
          className="loader-text"
        >
          Evolucionando...
        </motion.div>
        <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem', marginTop: 16 }}>
          Procesando {config.n_generaciones} generaciones en el motor genético
        </p>
      </div>
    )
  }

  return (
    <div className="config-layout">
      <section className="glass-panel">
        <div className="panel-header">
          <Sliders size={20} className="text-accent" />
          <h3>Hiperparámetros del AG</h3>
        </div>
        
        {sliders.map((s, idx) => (
          <motion.div 
            key={s.key} 
            className="slider-item"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
          >
            <div className="slider-info">
              <span className="slider-name">{s.label}</span>
              <span className="slider-curr">{config[s.key]}</span>
            </div>
            <input
              type="range"
              min={s.min}
              max={s.max}
              step={s.step}
              value={config[s.key]}
              onChange={e => setConfig({ ...config, [s.key]: parseFloat(e.target.value) })}
            />
          </motion.div>
        ))}
      </section>

      <aside>
        <div className="glass-panel">
          <div className="panel-header">
            <ClipboardList size={20} className="text-accent-secondary" />
            <h3>Resumen del Escenario</h3>
          </div>

          <div className="summary-card">
            <h4>Circuito</h4>
            <div className="summary-row">
              <span className="sum-label">Pista</span>
              <span className="sum-val">{selection.pista?.nombre?.replace(/_/g, ' ')}</span>
            </div>
            <div className="summary-row">
              <span className="sum-label">ρ del Aire</span>
              <span className="sum-val">{selection.pista?.densidad} kg/m³</span>
            </div>
          </div>

          <div className="summary-card">
            <h4>Monoplaza</h4>
            <div className="summary-row">
              <span className="sum-label">Categoría</span>
              <span className="sum-val">{selection.coche?.categoria?.replace(/_/g, ' ')}</span>
            </div>
            <div className="summary-row">
              <span className="sum-label">Potencia</span>
              <span className="sum-val">{selection.coche?.potencia_hp} HP</span>
            </div>
          </div>

          <div className="summary-card">
            <h4>Neumático</h4>
            <div className="summary-row">
              <span className="sum-label">Compuesto</span>
              <span className="sum-val">{selection.compuesto}</span>
            </div>
          </div>

          <div className="summary-card">
            <h4><Radio size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />Telemetría F1 25 (UDP)</h4>
            <div className="summary-row">
              <span className="sum-label">Estado</span>
              <span className="sum-val">{capturando ? 'Capturando…' : 'Detenida'}</span>
            </div>
            <div className="summary-row">
              <span className="sum-label">Muestras</span>
              <span className="sum-val">{telemetria?.muestras ?? 0}</span>
            </div>
            <div className="summary-row">
              <span className="sum-label">Vueltas completas</span>
              <span className="sum-val">{vueltasCompletas}</span>
            </div>
            <button className="btn-base btn-ghost" style={{ width: '100%', marginTop: 10 }} onClick={toggleCaptura}>
              {capturando ? 'Detener captura' : 'Iniciar captura'}
            </button>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 10, fontSize: '0.85rem', color: 'var(--text-dim)', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={usarTelemetria}
                onChange={e => setUsarTelemetria(e.target.checked)}
                disabled={vueltasCompletas === 0}
              />
              Superponer la mejor vuelta real en la gráfica
            </label>
          </div>

          <div className="action-bar" style={{ flexDirection: 'column', marginTop: 32 }}>
            <button className="btn-base btn-main" style={{ width: '100%' }} onClick={handleRun}>
              <Play size={18} fill="currentColor" /> Ejecutar Evolución
            </button>
            <button className="btn-base btn-ghost" style={{ width: '100%' }} onClick={onBack}>
              <MoveLeft size={18} /> Atrás
            </button>
          </div>
        </div>
      </aside>
    </div>
  )
}

