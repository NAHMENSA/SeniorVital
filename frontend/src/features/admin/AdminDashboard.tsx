import React, { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../../store/useAuth'
import { getPatients, setRoutineOverride } from '../../services/admin'
import { AccessibleButton, TrafficLight } from '../../components/ui'
import type { AdminPatient, RoutineOverride } from '../../types/models'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [patients, setPatients] = useState<AdminPatient[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [selectedPatient, setSelectedPatient] = useState<AdminPatient | null>(null)
  const [overrideNote, setOverrideNote] = useState('')
  const modalRef = useRef<HTMLDivElement>(null)
  const pageSize = 10

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getPatients()
      setPatients(data)
    } catch { /* empty */ }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const filtered = patients.filter(p =>
    !search || p.nombre_senior?.toLowerCase().includes(search.toLowerCase()) || p.email.toLowerCase().includes(search.toLowerCase())
  )

  const paginated = filtered.slice((page - 1) * pageSize, page * pageSize)
  const totalPages = Math.ceil(filtered.length / pageSize)

  const handleOverride = async () => {
    if (!selectedPatient) return
    try {
      const override: RoutineOverride = { custom_notes: overrideNote }
      await setRoutineOverride(selectedPatient.id, override)
      setSelectedPatient(null)
      setOverrideNote('')
    } catch { /* handle error */ }
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        <h1 className="text-xl text-primary font-bold">Panel de administración</h1>

        {/* Search */}
        <input type="search" value={search} onChange={e => { setSearch(e.target.value); setPage(1) }}
          placeholder="Buscar paciente..."
          className="w-full h-12 px-4 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-base"
          aria-label="Buscar pacientes" />

        {/* Table */}
        {loading ? (
          <div className="text-center p-8" role="status" aria-label="Cargando pacientes">
            <div className="w-10 h-10 border-4 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-on-surface-variant">Cargando pacientes...</p>
          </div>
        ) : (
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b-2 border-primary bg-surface-container-high">
                    <th className="p-3 text-sm font-bold text-primary">Nombre</th>
                    <th className="p-3 text-sm font-bold text-primary">Email</th>
                    <th className="p-3 text-sm font-bold text-primary">Riesgo</th>
                    <th className="p-3 text-sm font-bold text-primary">Racha</th>
                    <th className="p-3 text-sm font-bold text-primary">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map(p => (
                    <tr key={p.id} className="border-b border-outline-variant hover:bg-surface-container-high">
                      <td className="p-3 font-semibold">{p.nombre_senior || 'Sin nombre'}</td>
                      <td className="p-3 text-sm text-on-surface-variant">{p.email}</td>
                      <td className="p-3"><TrafficLight risk={p.risk} /></td>
                      <td className="p-3 font-bold text-center">{p.streak}</td>
                      <td className="p-3">
                        <AccessibleButton variant="ghost" size="sm" onClick={() => setSelectedPatient(p)}>
                          Anular
                        </AccessibleButton>
                      </td>
                    </tr>
                  ))}
                  {paginated.length === 0 && (
                    <tr><td colSpan={5} className="p-8 text-center text-on-surface-variant">No se encontraron pacientes</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 p-4 border-t border-outline-variant">
                <AccessibleButton variant="ghost" size="sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                  ← Anterior
                </AccessibleButton>
                <span className="text-sm text-on-surface-variant">Página {page} de {totalPages}</span>
                <AccessibleButton variant="ghost" size="sm" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                  Siguiente →
                </AccessibleButton>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Override modal */}
      {selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" role="dialog" aria-modal="true" aria-label="Anular rutina"
          ref={modalRef}
          onKeyDown={(e) => {
            if (e.key === 'Escape') setSelectedPatient(null)
          }}>
          <div className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-6 max-w-md w-full">
            <h2 className="text-lg font-bold text-primary mb-4">Anular rutina de {selectedPatient.nombre_senior}</h2>
            <textarea value={overrideNote} onChange={e => setOverrideNote(e.target.value)}
              placeholder="Notas de la anulación..."
              className="w-full h-24 px-4 py-3 rounded-xl border-2 border-outline-variant bg-surface focus:border-primary focus:outline-none text-base resize-none mb-4"
              aria-label="Notas de anulación" />
            <div className="flex gap-3">
              <AccessibleButton variant="ghost" onClick={() => setSelectedPatient(null)}>Cancelar</AccessibleButton>
              <AccessibleButton variant="primary" onClick={handleOverride}>Guardar anulación</AccessibleButton>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
