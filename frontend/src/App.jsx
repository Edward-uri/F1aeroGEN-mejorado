import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Flag, Settings, BarChart3, ChevronRight, Check } from 'lucide-react'
import SelectionPage from './pages/SelectionPage'
import ConfigPage from './pages/ConfigPage'
import ResultsPage from './pages/ResultsPage'

function App() {
  const [step, setStep] = useState(1)
  const [selection, setSelection] = useState({ pista: null, coche: null, compuesto: 'Blando' })
  const [config, setConfig] = useState({
    p_initial: 10,
    p_max: 30,
    p_cruza: 0.75,
    p_mut_i: 0.30,
    p_mut_gen: 0.20,
    n_generaciones: 25,
  })
  const [results, setResults] = useState(null)

  const steps = [
    { num: 1, label: 'ESCENARIO', icon: Flag },
    { num: 2, label: 'CONFIGURACIÓN', icon: Settings },
    { num: 3, label: 'RESULTADOS', icon: BarChart3 },
  ]

  const pageVariants = {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 }
  }

  return (
    <div className="app-container">
      <header className="header">
        <motion.h1 
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6 }}
        >
          F1 AEROGEN
        </motion.h1>
        <motion.p
          initial={{ y: -10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          Sistema de Optimización Aerodinámica por Algoritmo Genético
        </motion.p>
      </header>

      <nav className="stepper">
        {steps.map((s, idx) => (
          <div key={s.num} style={{ display: 'flex', alignItems: 'center' }}>
            <div
              className={`step ${step === s.num ? 'active' : ''} ${step > s.num ? 'done' : ''}`}
              onClick={() => step > s.num && setStep(s.num)}
            >
              <div className="step-number">
                {step > s.num ? <Check size={14} /> : <s.icon size={14} />}
              </div>
              {s.label}
            </div>
            {idx < steps.length - 1 && (
              <ChevronRight size={16} className="text-dim" style={{ opacity: 0.3, margin: '0 4px' }} />
            )}
          </div>
        ))}
      </nav>

      <main>
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.4 }}
            >
              <SelectionPage
                selection={selection}
                setSelection={setSelection}
                onNext={() => setStep(2)}
              />
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.4 }}
            >
              <ConfigPage
                selection={selection}
                config={config}
                setConfig={setConfig}
                onBack={() => setStep(1)}
                onResults={(data) => { setResults(data); setStep(3); }}
              />
            </motion.div>
          )}

          {step === 3 && (
            <motion.div
              key="step3"
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ duration: 0.4 }}
            >
              <ResultsPage
                results={results}
                onReset={() => { setStep(1); setResults(null); }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App

