<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

// Interfaces
interface Student {
  id: number
  dni: string
  first_name: string
  last_name: string
}

interface AcademicYear {
  id: number
  year: number
  is_active: boolean
}

interface Grade {
  id: number
  name: string
  level: string
}

interface Section {
  id: number
  name: string
  capacity: number
  grade_id: number
}

interface Enrollment {
  id: number
  student_id: number
  academic_year_id: number
  grade_id: number
  section_id: number
  status: string
  created_at: string
  student?: Student
  grade?: Grade
  section?: Section
}

// State
const activeTab = ref('enroll')
const step = ref(1)
const loading = ref(false)
const error = ref('')
const success = ref('')
const enrollments = ref<Enrollment[]>([])

// Data Lists
const students = ref<Student[]>([])
const years = ref<AcademicYear[]>([])
const grades = ref<Grade[]>([])
const sections = ref<Section[]>([])

// Selection
const selectedStudent = ref<Student | null>(null)
const selectedYear = ref<number | null>(null)
const selectedGrade = ref<number | null>(null)
const selectedSection = ref<number | null>(null)

// Computed
const filteredSections = computed(() => {
  if (!selectedGrade.value) return []
  return sections.value.filter(s => s.grade_id === selectedGrade.value)
})

// Methods
const fetchEnrollments = async () => {
  try {
    const response = await api.get('/enrollments/')
    enrollments.value = response.data
    console.log('Enrollments loaded:', enrollments.value)
  } catch (e: any) {
    console.error('Error cargando matrículas', e)
    console.error('Error details:', e.response?.data)
  }
}

const fetchData = async () => {
  try {
    const [studentsRes, yearsRes, gradesRes, sectionsRes] = await Promise.all([
      api.get('/students/'),
      api.get('/academic/years'),
      api.get('/academic/grades'),
      api.get('/academic/sections')
    ])
    
    students.value = studentsRes.data
    years.value = yearsRes.data
    grades.value = gradesRes.data
    sections.value = sectionsRes.data

    // Auto-select active year if exists
    const activeYear = years.value.find(y => y.is_active)
    if (activeYear) selectedYear.value = activeYear.id
    // Fallback: select first year if none active
    else if (years.value.length > 0) selectedYear.value = years.value[0].id

  } catch (e) {
    console.error("Error cargando datos iniciales", e)
    error.value = "Error cargando datos del sistema. Asegúrese de haber configurado años y grados."
  }
}

const selectStudent = (student: Student) => {
  selectedStudent.value = student
  step.value = 2
}

const processEnrollment = async () => {
  if (!selectedStudent.value || !selectedYear.value || !selectedGrade.value || !selectedSection.value) {
    error.value = "Por favor complete todos los campos"
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    await api.post('/enrollments/', {
      student_id: selectedStudent.value.id,
      academic_year_id: selectedYear.value,
      grade_id: selectedGrade.value,
      section_id: selectedSection.value
    })
    
    success.value = `Matrícula exitosa para ${selectedStudent.value.first_name}`
    step.value = 3 // Success view
    fetchEnrollments() // Refresh enrollments list
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al procesar matrícula'
  } finally {
    loading.value = false
  }
}

const reset = () => {
  selectedStudent.value = null
  selectedGrade.value = null
  selectedSection.value = null
  step.value = 1
  success.value = ''
  error.value = ''
}

onMounted(() => {
  fetchData()
  fetchEnrollments()
})
</script>

<template>
  <div>
    <!-- Tabs Navigation -->
    <ul class="nav nav-tabs mb-4" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: activeTab === 'enroll'}" @click="activeTab = 'enroll'" type="button" role="tab">
          <i class="bi bi-plus-circle-fill me-2"></i>Nueva Matrícula
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: activeTab === 'list'}" @click="activeTab = 'list'" type="button" role="tab">
          <i class="bi bi-list-check me-2"></i>Alumnos Matriculados
        </button>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- TAB 1: Nueva Matrícula -->
      <div class="tab-pane fade" :class="{show: activeTab === 'enroll', active: activeTab === 'enroll'}" role="tabpanel">
        <div class="row justify-content-center">
          <div class="col-md-8">
      
      <!-- Progress Bar -->
      <div class="position-relative m-4">
        <div class="progress" style="height: 1px;">
          <div class="progress-bar bg-primary" role="progressbar" :style="{width: (step-1)*50 + '%'}" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
        </div>
        <button type="button" class="position-absolute top-0 start-0 translate-middle btn btn-sm rounded-pill" :class="step >= 1 ? 'btn-primary' : 'btn-secondary'" style="width: 2rem; height:2rem;">1</button>
        <button type="button" class="position-absolute top-0 start-50 translate-middle btn btn-sm rounded-pill" :class="step >= 2 ? 'btn-primary' : 'btn-secondary'" style="width: 2rem; height:2rem;">2</button>
        <button type="button" class="position-absolute top-0 start-100 translate-middle btn btn-sm rounded-pill" :class="step >= 3 ? 'btn-primary' : 'btn-secondary'" style="width: 2rem; height:2rem;">3</button>
      </div>

      <div class="card mt-5">
        <div class="card-body p-4">
          
          <!-- STEP 1: Seleccionar Alumno -->
          <div v-if="step === 1">
            <h4 class="card-title mb-4 text-center">Seleccionar Alumno</h4>
            <div class="input-group mb-3">
              <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
              <input type="text" class="form-control" placeholder="Buscar por DNI o Apellido...">
            </div>
            
            <div class="list-group list-group-flush border rounded">
              <button 
                v-for="student in students" 
                :key="student.id"
                @click="selectStudent(student)"
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center p-3"
              >
                <div>
                  <div class="fw-bold">{{ student.last_name }}, {{ student.first_name }}</div>
                  <small class="text-muted">DNI: {{ student.dni }}</small>
                </div>
                <i class="bi bi-chevron-right text-muted"></i>
              </button>
              
              <div v-if="students.length === 0" class="p-4 text-center text-muted">
                No hay alumnos registrados. <router-link to="/students">Registrar nuevo</router-link>
              </div>
            </div>
          </div>

          <!-- STEP 2: Configurar Matrícula -->
          <div v-if="step === 2">
            <div class="d-flex align-items-center mb-4">
              <button @click="step = 1" class="btn btn-link text-decoration-none p-0 me-3"><i class="bi bi-arrow-left fs-4"></i></button>
              <h4 class="card-title mb-0">Matricular a {{ selectedStudent?.first_name }}</h4>
            </div>

            <form @submit.prevent="processEnrollment">
              <div class="mb-3">
                <label class="form-label text-muted small fw-bold">AÑO ACADÉMICO</label>
                <select v-model="selectedYear" class="form-select" required>
                  <option v-for="year in years" :key="year.id" :value="year.id">
                    {{ year.year }} {{ year.is_active ? '(Activo)' : '' }}
                  </option>
                </select>
              </div>

              <div class="row mb-4">
                <div class="col-md-6">
                  <label class="form-label text-muted small fw-bold">GRADO</label>
                  <select v-model="selectedGrade" class="form-select" required>
                    <option :value="null">Seleccione...</option>
                    <option v-for="grade in grades" :key="grade.id" :value="grade.id">
                      {{ grade.name }} - {{ grade.level }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label text-muted small fw-bold">SECCIÓN</label>
                  <select v-model="selectedSection" class="form-select" :disabled="!selectedGrade" required>
                    <option :value="null">Seleccione...</option>
                    <option v-for="section in filteredSections" :key="section.id" :value="section.id">
                      Sección {{ section.name }} (Cap: {{ section.capacity }})
                    </option>
                  </select>
                </div>
              </div>

              <div v-if="error" class="alert alert-danger">{{ error }}</div>

              <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Confirmar Matrícula
              </button>
            </form>
          </div>

          <!-- STEP 3: Éxito -->
          <div v-if="step === 3" class="text-center py-4">
            <div class="mb-3">
              <i class="bi bi-check-circle-fill text-success display-1"></i>
            </div>
            <h3 class="mb-3">¡Matrícula Exitosa!</h3>
            <p class="text-muted mb-4">{{ success }}</p>
            
            <div class="d-grid gap-2 col-md-6 mx-auto">
              <button @click="reset" class="btn btn-outline-primary">Matricular otro alumno</button>
              <router-link to="/" class="btn btn-link text-muted">Volver al inicio</router-link>
            </div>
          </div>

          </div>
        </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: Lista de Matriculados -->
      <div class="tab-pane fade" :class="{show: activeTab === 'list', active: activeTab === 'list'}" role="tabpanel">
        <div class="card">
          <div class="card-header bg-white border-bottom-0 pt-4 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0 text-secondary">Alumnos Matriculados</h5>
            <span class="badge bg-light text-dark border">{{ enrollments.length }} matrículas</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4">Estudiante</th>
                    <th>Grado y Sección</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="enrollment in enrollments" :key="enrollment.id">
                    <td class="ps-4">
                      <div class="fw-bold">{{ enrollment.student?.last_name }}, {{ enrollment.student?.first_name }}</div>
                      <div class="small text-muted">ID: {{ enrollment.student_id }}</div>
                    </td>
                    <td>
                      <div>{{ enrollment.grade?.name }}</div>
                      <div class="small text-muted">Sección {{ enrollment.section?.name }}</div>
                    </td>
                    <td>
                      <span class="badge" :class="{
                        'bg-success': enrollment.status === 'Aprobado',
                        'bg-warning text-dark': enrollment.status === 'Pendiente',
                        'bg-danger': enrollment.status === 'Rechazado'
                      }">
                        {{ enrollment.status }}
                      </span>
                    </td>
                    <td>
                      <small class="text-muted">{{ new Date(enrollment.created_at).toLocaleDateString('es-PE') }}</small>
                    </td>
                  </tr>
                  <tr v-if="enrollments.length === 0">
                    <td colspan="4" class="text-center py-5 text-muted">
                      No hay matrículas registradas aún.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

