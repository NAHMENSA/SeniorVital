import React from 'react'
import { Link } from 'react-router-dom'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto">
        <Link to="/" className="text-primary font-bold hover:underline mb-4 inline-block">← Volver</Link>
        <h1 className="text-2xl font-bold text-primary mb-6">Política de Privacidad</h1>
        <div className="prose prose-sm text-on-surface-variant space-y-4">
          <p>Última actualización: {new Date().toLocaleDateString('es-ES')}</p>
          <h2 className="text-lg font-bold text-primary">1. Información que recopilamos</h2>
          <p>Recopilamos información que nos proporcionas al registrarte: nombre, email, edad, peso, condición física, objetivos, restricciones médicas y equipamiento disponible.</p>
          <p>También recopilamos datos de uso: rutinas completadas, RPE reportado, hábitos diarios (agua, sueño) y progreso general.</p>
          <h2 className="text-lg font-bold text-primary">2. Cómo usamos tu información</h2>
          <p>Usamos tus datos para: generar rutinas personalizadas, mostrar tu progreso, permitir que cuidadores autorizados sigan tu evolución, y mejorar nuestros servicios.</p>
          <h2 className="text-lg font-bold text-primary">3. Almacenamiento y seguridad</h2>
          <p>Tus datos se almacenan de forma segura en PostgreSQL con cifrado. Las contraseñas se hashean con bcrypt. Los tokens JWT expiran automáticamente.</p>
          <h2 className="text-lg font-bold text-primary">4. Compartición de datos</h2>
          <p>Solo compartimos tu información con cuidadores que hayas autorizado explícitamente mediante el proceso de vinculación. No vendemos tus datos a terceros.</p>
          <h2 className="text-lg font-bold text-primary">5. Tus derechos</h2>
          <p>Puedes solicitar la eliminación de tu cuenta y datos en cualquier momento contactándonos. Tienes derecho a acceder, rectificar y eliminar tu información personal.</p>
        </div>
      </div>
    </div>
  )
}
