import React from 'react'
import { Link } from 'react-router-dom'
import { AccessibleButton } from '../../components/ui'

/**
 * LandingPage — Public landing page.
 * Optimizado para adultos mayores con tamaños aumentados.
 *
 * Responsive:
 * - Hero section: full-width, fluid padding with clamp()
 * - Features grid: 1 col mobile, 2 col tablet, 3 col desktop
 * - Footer: stacks vertically on mobile, horizontal on tablet+
 *
 * WCAG 2.1 AA + Senior-friendly:
 * - Semantic heading hierarchy (h1 > h2 > h3)
 * - Decorative icons: aria-hidden="true"
 * - Focus-visible links
 * - Touch targets >= 56px
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero — fluid padding, responsive text */}
      <section className="bg-gradient-to-b from-secondary to-secondary-dark text-on-secondary px-[clamp(1.5rem,5vw,4rem)] py-[clamp(4rem,10vw,8rem)] text-center">
        <div className="max-w-[min(90%,44rem)] mx-auto">
          <span className="text-[clamp(4rem,10vw,7rem)] block mb-6" aria-hidden="true">👴</span>
          <h1 className="sv-text-heading mb-6">SeniorVital</h1>
          <p className="sv-text-subheading mb-10 opacity-90">
            Tu bienestar, nuestra prioridad. Plataforma integral para el cuidado de adultos mayores.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register?role=senior">
              <AccessibleButton variant="primary" size="lg">Soy Adulto Mayor</AccessibleButton>
            </Link>
            <Link to="/register?role=caregiver">
              <AccessibleButton variant="secondary" size="lg">Soy Cuidador</AccessibleButton>
            </Link>
          </div>
          <p className="mt-6 sv-text-body opacity-90 text-black">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="font-bold underline text-black focus:outline-none focus:ring-2 focus:ring-on-secondary rounded">
              Inicia sesión
            </Link>
          </p>
        </div>
      </section>

      {/* Features — responsive grid */}
      <section className="sv-container py-[clamp(3rem,8vw,6rem)]">
        <h2 className="sv-text-heading text-primary text-center mb-[clamp(2rem,5vw,4rem)]">
          ¿Qué ofrecemos?
        </h2>
        <div className="sv-grid-auto">
          {[
            { icon: '🏋️', title: 'Rutinas personalizadas', desc: 'Ejercicios adaptados a tu condición física y restricciones médicas, generados por IA.' },
            { icon: '📊', title: 'Seguimiento de progreso', desc: 'Monitorea tu evolución con gráficos, rachas y métricas clave de tu actividad diaria.' },
            { icon: '👨‍👩‍👧‍👦', title: 'Cuidadores informados', desc: 'Los familiares pueden seguir tu progreso y recibir alertas sobre tu bienestar.' },
          ].map(f => (
            <div key={f.title} className="bg-surface-container-lowest rounded-2xl border-2 border-primary p-[clamp(1.5rem,4vw,2.5rem)] text-center">
              <span className="text-[clamp(3rem,6vw,4.5rem)] block mb-4" aria-hidden="true">{f.icon}</span>
              <h3 className="sv-text-subheading text-primary mb-3">{f.title}</h3>
              <p className="sv-text-body text-on-surface-variant">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer — responsive, stacks on mobile */}
      <footer className="bg-surface-container-high py-[clamp(2rem,5vw,4rem)] px-5 text-center sv-text-body text-on-surface-variant" role="contentinfo">
        <div className="max-w-[min(90%,44rem)] mx-auto flex flex-col sm:flex-row gap-5 justify-center mb-5">
          <Link to="/terms" className="hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded min-h-[3.5rem] flex items-center">Términos y condiciones</Link>
          <Link to="/privacy" className="hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded min-h-[3.5rem] flex items-center">Política de privacidad</Link>
          <Link to="/help" className="hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded min-h-[3.5rem] flex items-center">Centro de ayuda</Link>
        </div>
        <p>&copy; {new Date().getFullYear()} SeniorVital. Todos los derechos reservados.</p>
      </footer>
    </div>
  )
}
