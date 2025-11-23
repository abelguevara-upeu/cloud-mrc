<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

// Interfaces
interface Guardian {
  dni: string
  first_name: string
  last_name: string
  phone: string
  email: string
}

interface Student {
  id?: number
  dni: string
  first_name: string
  last_name: string
  birth_date: string
  address: string
  guardian_dni: string
  guardian?: Guardian
}

// State
const students = ref<Student[]>([])
const guardians = ref<Guardian[]>([])
const enrolledStudentIds = ref<Set<number>>(new Set())
const loading = ref(false)
const error = ref('')
const success = ref('')
const activeTab = ref('students')
const editingStudent = ref<Student | null>(null)
const editingGuardian = ref<Guardian | null>(null)

// Form Data
const form = ref<Student>({
  dni: '',
  first_name: '',
  last_name: '',
  birth_date: '',
  address: '',
  guardian_dni: ''
})

const guardianForm = ref<Guardian>({
  dni: '',
  first_name: '',
  last_name: '',
  phone: '',
  email: ''
})

const showNewGuardianModal = ref(false)
const isNewGuardian = ref(false)

// Computed
const uniqueGuardians = computed(() => {
  const seen = new Set()
  return guardians.value.filter(g => {
    if (seen.has(g.dni)) return false
    seen.add(g.dni)
    return true
  })
})

// Methods
const fetchStudents = async () => {
  try {
    const response = await api.get('/students/')
    students.value = response.data
    await fetchEnrolledStudents()
  } catch (e) {
    console.error(e)
  }
}

const fetchEnrolledStudents = async () => {
  try {
    const response = await api.get('/enrollments/')
    const enrollments = response.data
    // Crear un Set con los IDs de estudiantes que tienen matrícula activa
    enrolledStudentIds.value = new Set(
      enrollments
        .filter((e: any) => e.status === 'Matriculado')
        .map((e: any) => e.student_id)
    )
  } catch (e) {
    console.error(e)
  }
}

const isEnrolled = (studentId: number) => {
  return enrolledStudentIds.value.has(studentId)
}

const fetchGuardians = async () => {
  try {
    const response = await api.get('/students/guardian')
    console.log('Guardians response:', response.data)
    guardians.value = response.data
  } catch (e) {
    console.error('Error fetching guardians:', e)
  }
}

const openNewGuardianModal = () => {
  guardianForm.value = { dni: '', first_name: '', last_name: '', phone: '', email: '' }
  showNewGuardianModal.value = true
}

const registerGuardian = async () => {
  // Si está editando, usar updateGuardian
  if (editingGuardian.value) {
    await updateGuardian()
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    if (!guardianForm.value.dni || !guardianForm.value.first_name || !guardianForm.value.last_name) {
      error.value = 'Complete DNI, nombres y apellidos del apoderado'
      loading.value = false
      return
    }

    await api.post('/students/guardian', guardianForm.value)
    success.value = 'Apoderado registrado exitosamente'
    
    await fetchGuardians()
    guardianForm.value = { dni: '', first_name: '', last_name: '', phone: '', email: '' }
    showNewGuardianModal.value = false

  } catch (e: any) {
    console.error('Error registrando apoderado:', e)
    error.value = e.response?.data?.detail || 'Error al registrar apoderado'
  } finally {
    loading.value = false
  }
}

const deleteStudent = async (studentId: number) => {
  if (!confirm('¿Está seguro de eliminar este alumno?')) return
  
  try {
    await api.delete(`/students/${studentId}`)
    success.value = 'Alumno eliminado exitosamente'
    await fetchStudents()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al eliminar alumno'
  }
}

const deleteGuardian = async (dni: string) => {
  if (!confirm('¿Está seguro de eliminar este apoderado?')) return
  
  try {
    await api.delete(`/students/guardian/${dni}`)
    success.value = 'Apoderado eliminado exitosamente'
    await fetchGuardians()
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al eliminar apoderado'
  }
}

const editStudent = (student: Student) => {
  editingStudent.value = { ...student }
  form.value = { ...student, guardian_dni: student.guardian?.dni || '' }
  activeTab.value = 'register'
}

const editGuardian = (guardian: Guardian) => {
  editingGuardian.value = { ...guardian }
  guardianForm.value = { ...guardian }
  showNewGuardianModal.value = true
}

const updateStudent = async () => {
  if (!editingStudent.value?.id) return
  
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await api.put(`/students/${editingStudent.value.id}`, form.value)
    success.value = 'Alumno actualizado exitosamente'
    await fetchStudents()
    form.value = { dni: '', first_name: '', last_name: '', birth_date: '', address: '', guardian_dni: '' }
    editingStudent.value = null
    activeTab.value = 'students'
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al actualizar alumno'
  } finally {
    loading.value = false
  }
}

const updateGuardian = async () => {
  if (!editingGuardian.value?.dni) return
  
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await api.put(`/students/guardian/${editingGuardian.value.dni}`, guardianForm.value)
    success.value = 'Apoderado actualizado exitosamente'
    await fetchGuardians()
    // Refrescar también los estudiantes para que se actualice la relación
    await fetchStudents()
    guardianForm.value = { dni: '', first_name: '', last_name: '', phone: '', email: '' }
    editingGuardian.value = null
    showNewGuardianModal.value = false
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al actualizar apoderado'
  } finally {
    loading.value = false
  }
}

const cancelEdit = () => {
  editingStudent.value = null
  editingGuardian.value = null
  form.value = { dni: '', first_name: '', last_name: '', birth_date: '', address: '', guardian_dni: '' }
  guardianForm.value = { dni: '', first_name: '', last_name: '', phone: '', email: '' }
  showNewGuardianModal.value = false
  error.value = ''
  success.value = ''
}

const goToEnroll = (studentId: number) => {
  // Guardar el ID del estudiante en localStorage para pre-seleccionarlo
  localStorage.setItem('preSelectedStudentId', studentId.toString())
  // Navegar a la vista de matrículas
  window.location.href = '/#/enrollments'
}

const selectNewGuardian = () => {
  isNewGuardian.value = true
  form.value.guardian_dni = ''
}

const register = async () => {
  // Si está editando, usar updateStudent
  if (editingStudent.value) {
    await updateStudent()
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    if (!form.value.guardian_dni) {
      error.value = 'Debe seleccionar un apoderado'
      loading.value = false
      return
    }

    await api.post('/students/', form.value)
    
    success.value = 'Alumno registrado exitosamente'
    await fetchStudents()
    
    // Reset form
    form.value = { dni: '', first_name: '', last_name: '', birth_date: '', address: '', guardian_dni: '' }
    isNewGuardian.value = false

  } catch (e: any) {
    console.error('Error registrando alumno:', e)
    error.value = e.response?.data?.detail || 'Error al registrar alumno'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStudents()
  fetchGuardians()
})
</script>

<template>
  <div>
    <!-- Tabs Navigation -->
    <ul class="nav nav-tabs mb-4" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'students' }"
          @click="activeTab = 'students'"
          type="button"
        >
          <i class="bi bi-people-fill me-2"></i>Alumnos
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'register' }"
          @click="activeTab = 'register'"
          type="button"
        >
          <i class="bi bi-person-plus-fill me-2"></i>Registrar Alumno
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'guardians' }"
          @click="activeTab = 'guardians'"
          type="button"
        >
          <i class="bi bi-person-hearts me-2"></i>Apoderados
        </button>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- TAB 1: Lista de Alumnos -->
      <div v-show="activeTab === 'students'">
        <div class="card">
          <div class="card-header bg-white border-bottom-0 pt-4 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0 text-secondary">Directorio de Alumnos</h5>
            <span class="badge bg-light text-dark border">{{ students.length }} registrados</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4">Estudiante</th>
                    <th>DNI</th>
                    <th>Fecha Nac.</th>
                    <th>Apoderado</th>
                    <th>Contacto</th>
                    <th class="text-center" style="width: 180px;">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="student in students" :key="student.id">
                    <td class="ps-4">
                      <div class="fw-bold">{{ student.last_name }}, {{ student.first_name }}</div>
                      <div class="small text-muted">{{ student.address }}</div>
                    </td>
                    <td>{{ student.dni }}</td>
                    <td class="small text-muted">{{ student.birth_date }}</td>
                    <td>
                      <div v-if="student.guardian">
                        {{ student.guardian.first_name }} {{ student.guardian.last_name }}
                        <div class="small text-muted">DNI: {{ student.guardian.dni }}</div>
                      </div>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td class="small">
                      <div v-if="student.guardian?.phone">
                        <i class="bi bi-telephone me-1"></i>{{ student.guardian.phone }}
                      </div>
                      <div v-if="student.guardian?.email">
                        <i class="bi bi-envelope me-1"></i>{{ student.guardian.email }}
                      </div>
                    </td>
                    <td class="text-center">
                      <button 
                        @click="goToEnroll(student.id!)" 
                        class="btn btn-sm me-1"
                        :class="isEnrolled(student.id!) ? 'btn-secondary' : 'btn-success'"
                        :disabled="isEnrolled(student.id!)"
                        :title="isEnrolled(student.id!) ? 'Ya está matriculado' : 'Matricular alumno'"
                      >
                        <i class="bi" :class="isEnrolled(student.id!) ? 'bi-check-circle' : 'bi-clipboard-check'"></i>
                      </button>
                      <button 
                        @click="editStudent(student)" 
                        class="btn btn-sm btn-outline-primary me-1"
                        title="Editar alumno"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button 
                        @click="deleteStudent(student.id!)" 
                        class="btn btn-sm btn-outline-danger"
                        title="Eliminar alumno"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="students.length === 0">
                    <td colspan="5" class="text-center py-5 text-muted">
                      No hay alumnos registrados aún.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: Formulario de Registro -->
      <div v-show="activeTab === 'register'">
        <form @submit.prevent="register">
          <div class="row g-4">
            <!-- Paso 1: Seleccionar Apoderado -->
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-header bg-danger text-white d-flex justify-content-between align-items-center">
                  <h6 class="mb-0">
                    <i class="bi bi-person-circle me-2"></i>Paso 1: Seleccionar Apoderado
                  </h6>
                  <button 
                    type="button"
                    class="btn btn-sm btn-light"
                    @click="openNewGuardianModal"
                  >
                    <i class="bi bi-plus-circle me-1"></i>Nuevo
                  </button>
                </div>
                <div class="card-body">
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Seleccione el Apoderado</label>
                    <select 
                      v-model="form.guardian_dni" 
                      class="form-select form-select-lg"
                      required
                    >
                      <option value="">-- Seleccione un apoderado --</option>
                      <option 
                        v-for="guardian in uniqueGuardians" 
                        :key="guardian.dni" 
                        :value="guardian.dni"
                      >
                        {{ guardian.first_name }} {{ guardian.last_name }} - DNI: {{ guardian.dni }}
                      </option>
                    </select>
                  </div>

                  <div v-if="form.guardian_dni" class="alert alert-success">
                    <i class="bi bi-check-circle me-2"></i>
                    Apoderado seleccionado correctamente
                  </div>

                  <div class="alert alert-info small mt-3">
                    <i class="bi bi-info-circle me-1"></i>
                    Si el apoderado no está en la lista, haga clic en <strong>"Nuevo"</strong> para registrarlo primero.
                  </div>
                </div>
              </div>
            </div>

            <!-- Paso 2: Datos del Alumno -->
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-header bg-danger text-white">
                  <h6 class="mb-0">
                    <i class="bi bi-person-badge me-2"></i>Paso 2: Datos del Alumno
                  </h6>
                </div>
                <div class="card-body">
                  <div class="row g-2 mb-3">
                    <div class="col-5">
                      <label class="form-label fw-semibold">DNI</label>
                      <input 
                        v-model="form.dni" 
                        type="text" 
                        class="form-control" 
                        placeholder="DNI" 
                        required 
                        maxlength="8"
                      >
                    </div>
                    <div class="col-7">
                      <label class="form-label fw-semibold">Fecha de Nacimiento</label>
                      <input 
                        v-model="form.birth_date" 
                        type="date" 
                        class="form-control" 
                        required
                      >
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-semibold">Nombres</label>
                    <input 
                      v-model="form.first_name" 
                      type="text" 
                      class="form-control" 
                      placeholder="Nombres del alumno" 
                      required
                    >
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-semibold">Apellidos</label>
                    <input 
                      v-model="form.last_name" 
                      type="text" 
                      class="form-control" 
                      placeholder="Apellidos del alumno" 
                      required
                    >
                  </div>

                  <div class="mb-4">
                    <label class="form-label fw-semibold">Dirección</label>
                    <input 
                      v-model="form.address" 
                      type="text" 
                      class="form-control" 
                      placeholder="Dirección de domicilio"
                    >
                  </div>

                  <!-- Mensajes -->
                  <div v-if="error" class="alert alert-danger py-2">
                    <i class="bi bi-x-circle me-1"></i>{{ error }}
                  </div>
                  <div v-if="success" class="alert alert-success py-2">
                    <i class="bi bi-check-circle me-1"></i>{{ success }}
                  </div>

                <div class="d-flex gap-2" v-if="editingStudent">
                  <button type="button" class="btn btn-secondary flex-fill" @click="cancelEdit">
                    Cancelar
                  </button>
                  <button type="submit" class="btn btn-danger flex-fill py-2" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    <i class="bi bi-save me-2" v-if="!loading"></i>
                    Actualizar Alumno
                  </button>
                </div>
                <button v-else type="submit" class="btn btn-danger w-100 py-2" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i class="bi bi-save me-2" v-if="!loading"></i>
                  Registrar Alumno
                </button>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- TAB 3: Lista de Apoderados -->
      <div v-show="activeTab === 'guardians'">
        <div class="card">
          <div class="card-header bg-white border-bottom-0 pt-4 d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0 text-secondary">Lista de Apoderados</h5>
            <button class="btn btn-danger" @click="openNewGuardianModal">
              <i class="bi bi-plus-circle me-2"></i>Nuevo Apoderado
            </button>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover align-middle mb-0">
                <thead class="table-light">
                  <tr>
                    <th class="ps-4">Apoderado</th>
                    <th>DNI</th>
                    <th>Teléfono</th>
                    <th>Email</th>
                    <th class="text-center">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="guardian in uniqueGuardians" :key="guardian.dni">
                    <td class="ps-4">
                      <div class="fw-bold">{{ guardian.first_name }} {{ guardian.last_name }}</div>
                    </td>
                    <td>{{ guardian.dni }}</td>
                    <td>
                      <span v-if="guardian.phone">
                        <i class="bi bi-telephone me-1"></i>{{ guardian.phone }}
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td>
                      <span v-if="guardian.email">{{ guardian.email }}</span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td class="text-center">
                      <button 
                        @click="editGuardian(guardian)" 
                        class="btn btn-sm btn-outline-primary me-1"
                        title="Editar apoderado"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button 
                        @click="deleteGuardian(guardian.dni)" 
                        class="btn btn-sm btn-outline-danger"
                        title="Eliminar apoderado"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="uniqueGuardians.length === 0">
                    <td colspan="4" class="text-center py-5 text-muted">
                      No hay apoderados registrados aún.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Nuevo Apoderado -->
    <div v-if="showNewGuardianModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">
              <i :class="['bi', editingGuardian ? 'bi-pencil' : 'bi-person-plus', 'me-2']"></i>
              {{ editingGuardian ? 'Editar Apoderado' : 'Registrar Nuevo Apoderado' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="cancelEdit"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="registerGuardian">
              <div class="mb-3">
                <label class="form-label fw-semibold">DNI *</label>
                <input 
                  v-model="guardianForm.dni" 
                  type="text" 
                  class="form-control" 
                  placeholder="DNI del apoderado" 
                  required 
                  maxlength="8"
                >
              </div>
              
              <div class="row g-2 mb-3">
                <div class="col-6">
                  <label class="form-label fw-semibold">Nombres *</label>
                  <input 
                    v-model="guardianForm.first_name" 
                    type="text" 
                    class="form-control" 
                    placeholder="Nombres" 
                    required
                  >
                </div>
                <div class="col-6">
                  <label class="form-label fw-semibold">Apellidos *</label>
                  <input 
                    v-model="guardianForm.last_name" 
                    type="text" 
                    class="form-control" 
                    placeholder="Apellidos" 
                    required
                  >
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label fw-semibold">Teléfono</label>
                <input 
                  v-model="guardianForm.phone" 
                  type="tel" 
                  class="form-control" 
                  placeholder="999 888 777"
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label fw-semibold">Email</label>
                <input 
                  v-model="guardianForm.email" 
                  type="email" 
                  class="form-control" 
                  placeholder="correo@ejemplo.com"
                >
              </div>

              <div v-if="error" class="alert alert-danger py-2">
                <i class="bi bi-x-circle me-1"></i>{{ error }}
              </div>

              <div class="d-flex gap-2">
                <button type="button" class="btn btn-secondary flex-fill" @click="cancelEdit">
                  Cancelar
                </button>
                <button type="submit" class="btn btn-danger flex-fill" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  <i class="bi bi-save me-2" v-if="!loading"></i>
                  {{ editingGuardian ? 'Actualizar' : 'Registrar' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

