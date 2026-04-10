import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { MapPin, Zap, Weight, Maximize2, MoveRight, Layers, CircleDot } from 'lucide-react'
import { getPistas, getCoches } from '../api'

const trackImages = {
  'Monza_Italia': '/images/tracks/monza.avif',
  'Monaco_GP': '/images/tracks/monaco.avif',
  'Silverstone_UK': '/images/tracks/silverstone.avif',
  'Spa_Belgica': '/images/tracks/spa.avif',
  'CDMX_Mexico': '/images/tracks/cdmx.avif',
}

const carImages = {
  'F1_Generico': '/images/cars/f1_generico.jpeg',
  'F2_Generico': '/images/cars/f2_generico.jpg',
}

const compuestos = [
  { id: 'Blando', label: 'Blando', desc: 'Máximo agarre / Menor duración', color: '#ff1e1e' },
  { id: 'Medio', label: 'Medio', desc: 'Equilibrio perfecto', color: '#f1c40f' },
  { id: 'Duro', label: 'Duro', desc: 'Máxima duración / Menor agarre', color: '#ecf0f1' },
]

export default function SelectionPage({ selection, setSelection, onNext }) {
  const [pistas, setPistas] = useState([])
  const [coches, setCoches] = useState([])

  useEffect(() => {
    getPistas().then(setPistas).catch(console.error)
    getCoches().then(setCoches).catch(console.error)
  }, [])

  const canContinue = selection.pista && selection.coche

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  }

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <h2 className="section-title"><MapPin size={22} className="text-accent" /> Selecciona el Circuito</h2>
      <div className="cards-grid">
        {pistas.map((p) => (
          <motion.div
            key={p.id}
            variants={itemVariants}
            className={`card ${selection.pista?.id === p.id ? 'selected' : ''}`}
            onClick={() => setSelection({ ...selection, pista: p })}
          >
            <div className="card-img-container">
              <img
                className="card-img"
                src={trackImages[p.nombre] || '/images/tracks/default.jpg'}
                alt={p.nombre}
                onError={e => { e.target.style.background = '#111'; }}
              />
              <div className="card-overlay" />
            </div>
            <div className="card-body">
              <div className="card-title">{p.nombre.replace(/_/g, ' ')}</div>
              <div className="card-stats">
                <div className="card-stat">
                  <span className="stat-label">Rectas</span>
                  <span className="stat-val">{p.rectas}m</span>
                </div>
                <div className="card-stat">
                  <span className="stat-label">Curvas</span>
                  <span className="stat-val">{p.curvas}m</span>
                </div>
                <div className="card-stat">
                  <span className="stat-label">Altitud</span>
                  <span className="stat-val">{p.altitud}m</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <h2 className="section-title"><Maximize2 size={22} className="text-accent" /> Selecciona el Monoplaza</h2>
      <div className="cards-grid">
        {coches.map((c) => (
          <motion.div
            key={c.id}
            variants={itemVariants}
            className={`card ${selection.coche?.id === c.id ? 'selected' : ''}`}
            onClick={() => setSelection({ ...selection, coche: c })}
          >
            <div className="card-img-container">
              <img
                className="card-img"
                src={carImages[c.categoria] || '/images/cars/default.jpg'}
                alt={c.categoria}
                onError={e => { e.target.style.background = '#111'; }}
              />
              <div className="card-overlay" />
            </div>
            <div className="card-body">
              <div className="card-title">{c.categoria.replace(/_/g, ' ')}</div>
              <div className="card-stats">
                <div className="card-stat">
                  <span className="stat-label"><Zap size={12} style={{ display: 'inline', marginRight: 4 }} /> Potencia</span>
                  <span className="stat-val">{c.potencia_hp} HP</span>
                </div>
                <div className="card-stat">
                  <span className="stat-label"><Weight size={12} style={{ display: 'inline', marginRight: 4 }} /> Peso</span>
                  <span className="stat-val">{c.peso_kg} kg</span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <h2 className="section-title"><Layers size={22} className="text-accent" /> Compuesto de Neumático</h2>
      <div className="cards-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
        {compuestos.map((comp) => (
          <motion.div
            key={comp.id}
            variants={itemVariants}
            className={`card ${selection.compuesto === comp.id ? 'selected' : ''}`}
            onClick={() => setSelection({ ...selection, compuesto: comp.id })}
            style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '16px' }}
          >
            <CircleDot size={32} style={{ color: comp.color }} />
            <div>
              <div className="card-title" style={{ marginBottom: '4px' }}>{comp.label}</div>
              <div className="stat-label" style={{ fontSize: '0.8rem' }}>{comp.desc}</div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="action-bar">
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="btn-base btn-main" 
          disabled={!canContinue} 
          onClick={onNext}
        >
          Configurar Algoritmo <MoveRight size={18} />
        </motion.button>
      </div>
    </motion.div>
  )
}


