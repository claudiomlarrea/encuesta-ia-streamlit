# ALIAA — Academia Latinoamericana de Inteligencia Artificial Aplicada

Plataforma educativa profesional para cursos asincrónicos de IA, con gestión de usuarios, certificados verificables, foros y pagos integrados.

## Tecnologías

- **Next.js 16** (App Router) + TypeScript
- **TailwindCSS 4** — diseño responsive con modo claro/oscuro
- **Supabase** — autenticación, base de datos PostgreSQL y Row Level Security
- **Mercado Pago** y **PayPal** — procesamiento de pagos
- **Vercel** — despliegue optimizado para Latinoamérica (región `gru1`)

## Características

- Sistema de usuarios con roles: Administrador, Docente y Alumno
- Gestión completa de cursos asincrónicos (videos, PDF, actividades, evaluaciones)
- Certificados automáticos con código QR verificable
- Dashboard de seguimiento de progreso
- Foros de discusión por curso
- Panel de administración completo
- Interfaz 100% en español
- Branding institucional para América Latina

## Inicio rápido

### 1. Instalar dependencias

```bash
cd aliaa
npm install
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env.local
```

Completá las credenciales de Supabase, Mercado Pago y PayPal.

### 3. Configurar Supabase

1. Creá un proyecto en [supabase.com](https://supabase.com)
2. Ejecutá la migración en el SQL Editor:

```bash
# Contenido de supabase/migrations/001_initial_schema.sql
```

3. (Opcional) Ejecutá `supabase/seed.sql` para datos de ejemplo

### 4. Ejecutar en desarrollo

```bash
npm run dev
```

Abrí [http://localhost:3000](http://localhost:3000)

## Estructura del proyecto

```
aliaa/
├── src/
│   ├── app/
│   │   ├── (public)/          # Páginas públicas (landing, cursos, nosotros)
│   │   ├── (auth)/            # Login y registro
│   │   ├── (dashboard)/       # Panel del alumno/docente
│   │   ├── (admin)/           # Panel de administración
│   │   └── api/               # API routes (pagos, certificados, auth)
│   ├── components/            # Componentes UI reutilizables
│   ├── lib/                   # Utilidades, Supabase, constantes
│   └── types/                 # Tipos TypeScript
├── supabase/
│   ├── migrations/            # Esquema de base de datos
│   └── seed.sql               # Datos de ejemplo
└── vercel.json                # Configuración de despliegue
```

## Despliegue en Vercel

1. Conectá el repositorio a Vercel
2. Configurá las variables de entorno desde `.env.example`
3. El directorio raíz del proyecto debe ser `aliaa`
4. Vercel detectará Next.js automáticamente

```bash
# Despliegue manual
npx vercel --prod
```

## Roles de usuario

| Rol | Permisos |
|-----|----------|
| **Alumno** | Inscribirse, ver cursos, foros, certificados |
| **Docente** | Gestionar sus cursos, ver estudiantes |
| **Admin** | Acceso completo: usuarios, cursos, pagos, configuración |

Para asignar rol admin, actualizá el perfil en Supabase:

```sql
UPDATE profiles SET rol = 'admin' WHERE email = 'tu@email.com';
```

## Licencia

Proyecto privado — ALIAA © 2025
