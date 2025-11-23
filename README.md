# Sistema de Matrícula - I.E. Mariscal Ramón Castilla

Este proyecto implementa un sistema de matrícula escolar bajo el modelo CaaS (Code as a Service), utilizando contenedores Docker para su fácil despliegue y escalabilidad.

## 1. Arquitectura del Sistema

El sistema está diseñado como una arquitectura de microservicios simplificada, orquestada mediante Docker Compose.

```mermaid
graph TD
    User((Usuario))

    subgraph "Cliente (Navegador)"
        UI[Frontend - Vue 3]
    end

    subgraph "Servidor (Docker Host)"
        ReverseProxy["Nginx / Traefik (Opcional)"]
        API[Backend - FastAPI]
        DB[(Base de Datos - PostgreSQL)]
    end

    User -->|HTTPS| UI
    UI -->|REST API / JSON| API
    API -->|SQL| DB

    style UI fill:#42b883,stroke:#333,stroke-width:2px,color:white
    style API fill:#009688,stroke:#333,stroke-width:2px,color:white
    style DB fill:#336791,stroke:#333,stroke-width:2px,color:white
```

## 2. Diagrama de Entidad-Relación (Modelo de Datos)

A continuación se detalla la estructura preliminar de la base de datos para soportar el proceso de matrícula.

```mermaid
erDiagram
    USERS ||--o{ ROLES : has
    USERS {
        int id PK
        string username
        string password_hash
        string email
        boolean is_active
    }

    ROLES {
        int id PK
        string name "Admin, Secretaria, Docente"
    }

    STUDENTS ||--o{ ENROLLMENTS : "se matricula en"
    STUDENTS }|--|| GUARDIANS : "representado por"
    STUDENTS {
        int id PK
        string dni UK
        string first_name
        string last_name
        date birth_date
        string address
        int guardian_id FK
    }

    GUARDIANS {
        int id PK
        string dni UK
        string first_name
        string last_name
        string phone
        string email
    }

    ACADEMIC_YEARS ||--o{ ENROLLMENTS : "contiene"
    ACADEMIC_YEARS {
        int id PK
        int year
        boolean is_active
        date start_date
        date end_date
    }

    ENROLLMENTS }|--|| GRADES : "pertenece a"
    ENROLLMENTS }|--|| SECTIONS : "asignado a"
    ENROLLMENTS {
        int id PK
        int student_id FK
        int academic_year_id FK
        int grade_id FK
        int section_id FK
        string status "Pendiente, Aprobado, Rechazado"
        date created_at
    }

    ENROLLMENTS ||--o{ DOCUMENTS : "tiene requisitos"
    DOCUMENTS {
        int id PK
        int enrollment_id FK
        string type "DNI, Certificado, Vacunacion"
        string file_url
        string status "Pendiente, Validado, Observado"
        date uploaded_at
    }

    GRADES ||--o{ SECTIONS : "tiene"
    GRADES {
        int id PK
        string name "1ro, 2do, 3ro..."
        string level "Primaria, Secundaria"
    }

    SECTIONS {
        int id PK
        string name "A, B, C..."
        int grade_id FK
        int capacity
    }
```

## 3. Flujo de Matrícula (Happy Path)

```mermaid
sequenceDiagram
    actor Padre as Apoderado/Secretaria
    participant FE as Frontend (Vue)
    participant BE as Backend (FastAPI)
    participant DB as PostgreSQL

    Padre->>FE: Inicia solicitud de matrícula
    FE->>BE: GET /students/validate/{dni}
    BE->>DB: Consulta existencia
    DB-->>BE: Retorna resultado
    BE-->>FE: Status (Nuevo o Existente)

    alt Estudiante Nuevo
        Padre->>FE: Ingresa datos Alumno + Apoderado
        FE->>BE: POST /students
        BE->>DB: Insertar Alumno y Apoderado
        DB-->>BE: OK
    end

    Padre->>FE: Selecciona Grado y Sección
    FE->>BE: POST /enrollments
    BE->>DB: Verificar vacantes en Sección

    alt Hay vacantes
        BE->>DB: Crear registro Enrollment (Pendiente)
        DB-->>BE: ID Matrícula
        BE-->>FE: Confirmación de registro
    else No hay vacantes
        BE-->>FE: Error: Sección llena
    end
```
