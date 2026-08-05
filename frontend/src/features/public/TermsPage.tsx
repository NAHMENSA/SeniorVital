import React from 'react'
import { Link } from 'react-router-dom'

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto">
        <Link to="/" className="text-primary font-bold hover:underline mb-4 inline-block">← Volver</Link>
        <h1 className="text-2xl font-bold text-primary mb-6">Términos y Condiciones</h1>
        <div className="prose prose-sm text-on-surface-variant space-y-4">
          <p>Última actualización: {new Date().toLocaleDateString('es-ES')}</p>
          <h2 className="text-lg font-bold text-primary">1. Aceptación de los términos</h2>
          <p>Al acceder y utilizar SeniorVital, aceptas cumplir con estos términos y condiciones. Si no estás de acuerdo, no uses el servicio.</p>
          <h2 className="text-lg font-bold text-primary">2. Descripción del servicio</h2>
          <p>SeniorVital es una plataforma de bienestar para adultos mayores que proporciona rutinas de ejercicio personalizadas, seguimiento de actividad, y herramientas de comunicación con cuidadores y profesionales de la salud.</p>
          <h2 className="text-lg font-bold text-primary">3. Privacidad de los datos</h2>
          <p>Nos tomamos muy en serio tu privacidad. Consulta nuestra <Link to="/privacy" className="text-primary font-bold hover:underline">Política de Privacidad</Link> para entender cómo manejamos tus datos.</p>
          <h2 className="text-lg font-bold text-primary">4. Responsabilidad del usuario</h2>
          <p>Eres responsable de la precisión de la información que proporcionas, incluyendo tu perfil de salud. Consulta a un médico antes de comenzar cualquier rutina de ejercicios.</p>
          <h2 className="text-lg font-bold text-primary">5. Limitación de responsabilidad</h2>
          <p>SeniorVital no se hace responsable de lesiones o problemas de salud derivados del uso de las rutinas recomendadas. Siempre consulta con un profesional de la salud.</p>
        </div>
      </div>
    </div>
  )
}
