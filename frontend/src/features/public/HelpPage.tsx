import React from 'react'
import { Link } from 'react-router-dom'

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto">
        <Link to="/" className="text-primary font-bold hover:underline mb-4 inline-block">← Volver</Link>
        <h1 className="text-2xl font-bold text-primary mb-6">Centro de ayuda</h1>

        <div className="space-y-4">
          {[
            { q: '¿Cómo me registro?', a: 'Selecciona "Soy Adulto Mayor" o "Soy Cuidador" en la página de inicio, completa el formulario con tus datos y crea una contraseña.' },
            { q: '¿Cómo se genera mi rutina?', a: 'Después de completar tu perfil de salud, nuestra IA genera rutinas personalizadas basadas en tu condición física, objetivos y restricciones médicas.' },
            { q: '¿Puede un cuidador ver mi progreso?', a: 'Sí. Desde tu perfil de senior puedes vincular cuidadores por email. Ellos recibirán acceso de solo lectura a tu progreso.' },
            { q: '¿Cómo registro mis hábitos diarios?', a: 'Ve a la sección "Hábitos" desde el menú inferior. Puedes registrar tu consumo de agua y horas de sueño con botones + y -.' },
            { q: '¿Qué es el RPE?', a: 'El RPE (Rate of Perceived Exertion) es una escala del 1 al 10 que mide el esfuerzo percibido durante el ejercicio. Te ayuda a seguimiento de intensidad.' },
            { q: '¿Cómo contacto con soporte?', a: 'Para ayuda adicional, contacta a tu cuidador o profesional de la salud asignado.' },
          ].map((item, i) => (
            <details key={i} className="bg-surface-container-lowest rounded-xl border-2 border-primary p-4">
              <summary className="font-bold text-primary cursor-pointer min-h-[48px] flex items-center focus:outline-none focus:ring-2 focus:ring-primary rounded-lg">
                {item.q}
              </summary>
              <p className="mt-3 text-on-surface-variant pl-4 border-l-2 border-secondary">{item.a}</p>
            </details>
          ))}
        </div>
      </div>
    </div>
  )
}
