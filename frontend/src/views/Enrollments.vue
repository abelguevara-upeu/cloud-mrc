<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

// Interfaces
interface Student {
  id?: number
  dni: string
  first_name: string
  last_name: string
  birth_date: string
  address: string
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
const loading = ref(false)
const error = ref('')
const success = ref('')
const enrollments = ref<Enrollment[]>([])
const students = ref<Student[]>([])

// Data Lists
const years = ref<AcademicYear[]>([])
const grades = ref<Grade[]>([])
const sections = ref<Section[]>([])

// Selection
const selectedStudent = ref<number | null>(null)
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
  } catch (e: any) {
    console.error('Error cargando matrículas', e)
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/students/')
    students.value = response.data
  } catch (e: any) {
    console.error('Error cargando alumnos', e)
  }
}

const fetchData = async () => {
  try {
    const [yearsRes, gradesRes, sectionsRes] = await Promise.all([
      api.get('/academic/years'),
      api.get('/academic/grades'),
      api.get('/academic/sections')
    ])
    
    years.value = yearsRes.data
    grades.value = gradesRes.data
    sections.value = sectionsRes.data

    // Auto-select active year if exists
    const activeYear = years.value.find(y => y.is_active)
    if (activeYear) selectedYear.value = activeYear.id
    else if (years.value.length > 0) selectedYear.value = years.value[0].id

  } catch (e) {
    console.error("Error cargando datos iniciales", e)
    error.value = "Error cargando datos del sistema."
  }
}

const processEnrollment = async () => {
  if (!selectedStudent.value || !selectedYear.value || !selectedGrade.value || !selectedSection.value) {
    error.value = "Por favor complete todos los campos"
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    await api.post('/enrollments/', {
      student_id: selectedStudent.value,
      academic_year_id: selectedYear.value,
      grade_id: selectedGrade.value,
      section_id: selectedSection.value
    })
    
    success.value = `¡Matrícula registrada exitosamente!`
    await fetchEnrollments()
    reset()
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
  success.value = ''
  error.value = ''
}

const deleteEnrollment = async (enrollmentId: number) => {
  if (!confirm('¿Está seguro de eliminar esta matrícula?')) return
  
  try {
    await api.delete(`/enrollments/${enrollmentId}`)
    success.value = 'Matrícula eliminada exitosamente'
    await fetchEnrollments()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al eliminar matrícula'
  }
}

const changeEnrollmentStatus = async (enrollmentId: number, newStatus: string) => {
  try {
    await api.patch(`/enrollments/${enrollmentId}/status`, null, {
      params: { status: newStatus }
    })
    success.value = `Estado cambiado a ${newStatus}`
    await fetchEnrollments()
    setTimeout(() => { success.value = '' }, 3000)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al cambiar estado'
  }
}

onMounted(() => {
  fetchData()
  fetchStudents()
  fetchEnrollments()
  
  // Pre-seleccionar estudiante si viene desde la tabla de alumnos
  const preSelectedId = localStorage.getItem('preSelectedStudentId')
  if (preSelectedId) {
    selectedStudent.value = parseInt(preSelectedId)
    localStorage.removeItem('preSelectedStudentId')
    activeTab.value = 'enroll'
  }
})
</script>

<template>
  <div>
    <!-- Tabs Navigation -->
    <ul class="nav nav-tabs mb-4" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link" :class="{active: activeTab === 'enroll'}" @click="activeTab = 'enroll'; reset()" type="button" role="tab">
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
          <div class="col-md-10">

      <div class="card">
        <div class="card-header bg-danger text-white">
          <h5 class="mb-0"><i class="bi bi-plus-circle-fill me-2"></i>Nueva Matrícula</h5>
        </div>
        <div class="card-body p-4">
          
          <form @submit.prevent="processEnrollment">
            <div class="alert alert-info mb-4">
              <i class="bi bi-info-circle me-2"></i>
              Los alumnos y apoderados se registran en el módulo <strong>"Alumnos"</strong>. Aquí solo se asignan a grados y secciones.
            </div>

            <div class="mb-4">
              <label class="form-label fw-semibold">Seleccionar Alumno</label>
              <select v-model="selectedStudent" class="form-select form-select-lg" required>
                <option :value="null">-- Seleccione un alumno --</option>
                <option v-for="student in students" :key="student.id" :value="student.id">
                  {{ student.last_name }}, {{ student.first_name }} - DNI: {{ student.dni }}
                </option>
              </select>
              <div class="form-text">
                <i class="bi bi-lightbulb me-1"></i>
                Si el alumno no aparece, regístrelo primero en el módulo <strong>"Alumnos"</strong>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-semibold">Año Académico</label>
              <select v-model="selectedYear" class="form-select" required>
                <option v-for="year in years" :key="year.id" :value="year.id">
                  {{ year.year }} {{ year.is_active ? '(Activo)' : '' }}
                </option>
              </select>
            </div>

            <div class="row mb-4">
              <div class="col-md-6">
                <label class="form-label fw-semibold">Grado</label>
                <select v-model="selectedGrade" class="form-select" required>
                  <option :value="null">-- Seleccione --</option>
                  <option v-for="grade in grades" :key="grade.id" :value="grade.id">
                    {{ grade.name }} - {{ grade.level }}
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Sección</label>
                <select v-model="selectedSection" class="form-select" :disabled="!selectedGrade" required>
                  <option :value="null">-- Seleccione --</option>
                  <option v-for="section in filteredSections" :key="section.id" :value="section.id">
                    Sección {{ section.name }} (Capacidad: {{ section.capacity }})
                  </option>
                </select>
              </div>
            </div>

            <!-- Mensajes -->
            <div v-if="error" class="alert alert-danger py-2">
              <i class="bi bi-x-circle me-1"></i>{{ error }}
            </div>
            <div v-if="success" class="alert alert-success py-2">
              <i class="bi bi-check-circle me-1"></i>{{ success }}
            </div>

            <button type="submit" class="btn btn-danger w-100 py-2" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              <i class="bi bi-check-circle me-2" v-if="!loading"></i>
              Registrar Matrícula
            </button>
          </form>

        </div>
      </div>
      </div>
        </div>
      </div>

      <!-- TAB 2: Alumnos Matriculados -->
      <div class="tab-pane fade" :class="{show: activeTab === 'list', active: activeTab === 'list'}" role="tabpanel">
        <div class="card">
          <div class="card-header bg-white border-bottom-0 pt-4 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0 text-secondary">Matrículas Registradas</h5>
            <span class="badge bg-light text-dark border">{{ enrollments.length }} total</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive" style="overflow: visible;">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4">Alumno</th>
                    <th>Grado</th>
                    <th>Sección</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                    <th class="text-center">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="enrollment in enrollments" :key="enrollment.id">
                    <td class="ps-4">
                      <div class="fw-bold" v-if="enrollment.student">
                        {{ enrollment.student.last_name }}, {{ enrollment.student.first_name }}
                      </div>
                      <small class="text-muted" v-if="enrollment.student">DNI: {{ enrollment.student.dni }}</small>
                    </td>
                    <td>
                      <div v-if="enrollment.grade" class="fw-semibold text-dark">
                        {{ enrollment.grade.name }}
                      </div>
                    </td>
                    <td>
                      <span v-if="enrollment.section" class="badge bg-primary px-2 py-1">
                        Sección {{ enrollment.section.name }}
                      </span>
                    </td>
                    <td>
                      <span class="badge fs-6 px-3 py-2" :class="{
                        'bg-success': enrollment.status === 'Matriculado',
                        'bg-warning text-dark': enrollment.status === 'Pendiente',
                        'bg-danger': enrollment.status === 'Retirado' || enrollment.status === 'Rechazado'
                      }">
                        <i class="bi me-1" :class="{
                          'bi-check-circle': enrollment.status === 'Matriculado',
                          'bi-clock': enrollment.status === 'Pendiente',
                          'bi-x-circle': enrollment.status === 'Retirado' || enrollment.status === 'Rechazado'
                        }"></i>
                        {{ enrollment.status }}
                      </span>
                    </td>
                    <td>
                      <small class="text-muted">{{ new Date(enrollment.created_at).toLocaleDateString() }}</small>
                    </td>
                    <td class="text-center position-relative">
                      <div class="btn-group" role="group">
                        <button 
                          class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                          type="button" 
                          :id="'statusDropdown' + enrollment.id"
                          data-bs-toggle="dropdown" 
                          aria-expanded="false"
                          title="Cambiar estado"
                        >
                          <i class="bi bi-gear"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end shadow" :aria-labelledby="'statusDropdown' + enrollment.id" style="z-index: 1050;">
                          <li>
                            <a 
                              class="dropdown-item" 
                              href="#"
                              @click.prevent="changeEnrollmentStatus(enrollment.id, 'Matriculado')"
                            >
                              <i class="bi bi-check-circle text-success me-2"></i>Matriculado
                            </a>
                          </li>
                          <li>
                            <a 
                              class="dropdown-item" 
                              href="#"
                              @click.prevent="changeEnrollmentStatus(enrollment.id, 'Pendiente')"
                            >
                              <i class="bi bi-clock text-warning me-2"></i>Pendiente
                            </a>
                          </li>
                          <li><hr class="dropdown-divider"></li>
                          <li>
                            <a 
                              class="dropdown-item" 
                              href="#"
                              @click.prevent="changeEnrollmentStatus(enrollment.id, 'Retirado')"
                            >
                              <i class="bi bi-box-arrow-right text-danger me-2"></i>Retirado
                            </a>
                          </li>
                          <li>
                            <a 
                              class="dropdown-item" 
                              href="#"
                              @click.prevent="changeEnrollmentStatus(enrollment.id, 'Rechazado')"
                            >
                              <i class="bi bi-x-circle text-danger me-2"></i>Rechazado
                            </a>
                          </li>
                        </ul>
                      </div>
                      <button 
                        @click="deleteEnrollment(enrollment.id)" 
                        class="btn btn-sm btn-outline-danger ms-1"
                        title="Eliminar matrícula"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                      <router-link
                        :to="`/documents?enrollment=${enrollment.id}`"
                        class="btn btn-sm btn-outline-info ms-1"
                        title="Ver documentos"
                      >
                        <i class="bi bi-file-earmark-text"></i>
                      </router-link>
                    </td>
                  </tr>
                  <tr v-if="enrollments.length === 0">
                    <td colspan="6" class="text-center py-5 text-muted">
                      <i class="bi bi-inbox fs-1 d-block mb-2"></i>
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
