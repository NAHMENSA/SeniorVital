import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function RoleSelectPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-5">
      <div className="w-full max-w-lg text-center flex flex-col gap-8">
        <h1 className="text-5xl text-primary font-bold mb-4">SeniorVital</h1>
        <p className="text-2xl text-on-surface-variant mb-6">¿Quién eres?</p>

        <button
          onClick={() => navigate('/register?role=senior')}
          className="w-full min-h-[5rem] bg-secondary text-on-secondary rounded-2xl border-2 border-secondary font-bold text-xl p-8 flex items-center justify-center gap-5 hover:brightness-110 active:scale-95 transition-all focus:outline-none focus:ring-4 focus:ring-secondary focus:ring-offset-4"
          aria-label="Registrarme como adulto mayor"
        >
          <span className="text-5xl" aria-hidden="true">👴</span>
          Soy Adulto Mayor
        </button>

        <button
          onClick={() => navigate('/register?role=caregiver')}
          className="w-full min-h-[5rem] bg-surface-container-high text-primary rounded-2xl border-2 border-primary font-bold text-xl p-8 flex items-center justify-center gap-5 hover:brightness-110 active:scale-95 transition-all focus:outline-none focus:ring-4 focus:ring-primary focus:ring-offset-4"
          aria-label="Registrarme como familiar o cuidador"
        >
          <span className="text-5xl" aria-hidden="true">👨‍👩‍👧‍👦</span>
          Soy Familiar / Cuidador
        </button>

        <p className="text-lg text-black mt-6">
          ¿Ya tienes cuenta?{' '}
          <a href="/login" className="text-black font-bold hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded">
            Inicia sesión
          </a>
        </p>
      </div>
    </div>
  )
}
