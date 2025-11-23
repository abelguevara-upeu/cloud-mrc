<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'

// Interfaces
interface AcademicYear {
  id?: number
  year: number
  start_date: string
  end_date: string
  is_active: boolean
}

interface Grade {
  id?: number
  name: string
  level: string
}

interface Section {
  id?: number
  name: string
  capacity: number
  grade_id: number
}

// State
const activeTab = ref('years')
const loading = ref(false)
const error = ref('')
const success = ref('')

// Data
const years = ref<AcademicYear[]>([])
const grades = ref<Grade[]>([])
const sections = ref<Section[]>([])

// Forms
const yearForm = ref<AcademicYear>({
  year: new Date().getFullYear(),
  start_date: '',
  end_date: '',
  is_active: false
})

const gradeForm = ref<Grade>({
  name: '',
  level: 'Primaria'
})

const sectionForm = ref<Section>({
  name: '',
  capacity: 30,
  grade_id: 0
})

// Methods
const fetchYears = async () => {
  try {
    const response = await api.get('/academic/years')
    years.value = response.data
  } catch (e) {
    console.error(e)
  }
}

const fetchGrades = async () => {
  try {
    const response = await api.get('/academic/grades')
    grades.value = response.data
  } catch (e) {
    console.error(e)
  }
}

const fetchSections = async () => {
  try {
    const response = await api.get('/academic/sections')
    sections.value = response.data
  } catch (e) {
    console.error(e)
  }
}

const createYear = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    await api.post('/academic/years', yearForm.value)
    success.value = 'Año académico creado exitosamente'
    fetchYears()
    yearForm.value = { year: new Date().getFullYear() + 1, start_date: '', end_date: '', is_active: false }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al crear año académico'
  } finally {
    loading.value = false
  }
}

const createGrade = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    await api.post('/academic/grades', gradeForm.value)
    success.value = 'Grado creado exitosamente'
    fetchGrades()
    gradeForm.value = { name: '', level: 'Primaria' }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al crear grado'
  } finally {
    loading.value = false
  }
}

const createSection = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  
  try {
    await api.post('/academic/sections', sectionForm.value)
    success.value = 'Sección creada exitosamente'
    fetchSections()
    sectionForm.value = { name: '', capacity: 30, grade_id: 0 }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Error al crear sección'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchYears()
  fetchGrades()
  fetchSections()
})
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="text-danger">
        <i class="bi bi-gear-fill me-2"></i>Configuración Académica
      </h2>
    </div>

    <!-- Tabs Navigation -->
    <ul class="nav nav-tabs mb-4" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{active: activeTab === 'years'}" 
          @click="activeTab = 'years'" 
          type="button" 
          role="tab"
        >
          <i class="bi bi-calendar3 me-2"></i>Años Académicos
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{active: activeTab === 'grades'}" 
          @click="activeTab = 'grades'" 
          type="button" 
          role="tab"
        >
          <i class="bi bi-book me-2"></i>Grados
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{active: activeTab === 'sections'}" 
          @click="activeTab = 'sections'" 
          type="button" 
          role="tab"
        >
          <i class="bi bi-door-open me-2"></i>Secciones
        </button>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- TAB 1: Años Académicos -->
      <div class="tab-pane fade" :class="{show: activeTab === 'years', active: activeTab === 'years'}" role="tabpanel">
        <div class="row">
          <div class="col-md-4">
            <div class="card">
              <div class="card-header bg-danger text-white">
                <h6 class="mb-0"><i class="bi bi-plus-circle me-2"></i>Crear Año Académico</h6>
              </div>
              <div class="card-body">
                <form @submit.prevent="createYear">
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Año</label>
                    <input 
                      v-model.number="yearForm.year" 
                      type="number" 
                      class="form-control" 
                      required 
                      min="2020" 
                      max="2050"
                    >
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Fecha de Inicio</label>
                    <input 
                      v-model="yearForm.start_date" 
                      type="date" 
                      class="form-control" 
                      required
                    >
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Fecha de Fin</label>
                    <input 
                      v-model="yearForm.end_date" 
                      type="date" 
                      class="form-control" 
                      required
                    >
                  </div>
                  
                  <div class="form-check mb-3">
                    <input 
                      v-model="yearForm.is_active" 
                      class="form-check-input" 
                      type="checkbox" 
                      id="activeYear"
                    >
                    <label class="form-check-label" for="activeYear">
                      Año Activo
                    </label>
                  </div>

                  <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
                  <div v-if="success" class="alert alert-success py-2 small">{{ success }}</div>

                  <button type="submit" class="btn btn-danger w-100" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    Crear Año
                  </button>
                </form>
              </div>
            </div>
          </div>

          <div class="col-md-8">
            <div class="card">
              <div class="card-header bg-white">
                <h6 class="mb-0">Años Académicos Registrados</h6>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th class="ps-4">Año</th>
                        <th>Periodo</th>
                        <th>Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="year in years" :key="year.id">
                        <td class="ps-4 fw-bold">{{ year.year }}</td>
                        <td class="small">
                          {{ new Date(year.start_date).toLocaleDateString('es-PE') }} - 
                          {{ new Date(year.end_date).toLocaleDateString('es-PE') }}
                        </td>
                        <td>
                          <span v-if="year.is_active" class="badge bg-success">Activo</span>
                          <span v-else class="badge bg-secondary">Inactivo</span>
                        </td>
                      </tr>
                      <tr v-if="years.length === 0">
                        <td colspan="3" class="text-center py-5 text-muted">
                          No hay años académicos registrados
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

      <!-- TAB 2: Grados -->
      <div class="tab-pane fade" :class="{show: activeTab === 'grades', active: activeTab === 'grades'}" role="tabpanel">
        <div class="row">
          <div class="col-md-4">
            <div class="card">
              <div class="card-header bg-danger text-white">
                <h6 class="mb-0"><i class="bi bi-plus-circle me-2"></i>Crear Grado</h6>
              </div>
              <div class="card-body">
                <form @submit.prevent="createGrade">
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Nombre del Grado</label>
                    <input 
                      v-model="gradeForm.name" 
                      type="text" 
                      class="form-control" 
                      placeholder="Ej: 1° Primaria" 
                      required
                    >
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Nivel</label>
                    <select v-model="gradeForm.level" class="form-select" required>
                      <option value="Primaria">Primaria</option>
                      <option value="Secundaria">Secundaria</option>
                    </select>
                  </div>

                  <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
                  <div v-if="success" class="alert alert-success py-2 small">{{ success }}</div>

                  <button type="submit" class="btn btn-danger w-100" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    Crear Grado
                  </button>
                </form>
              </div>
            </div>
          </div>

          <div class="col-md-8">
            <div class="card">
              <div class="card-header bg-white">
                <h6 class="mb-0">Grados Registrados</h6>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th class="ps-4">Grado</th>
                        <th>Nivel</th>
                        <th>Secciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="grade in grades" :key="grade.id">
                        <td class="ps-4 fw-bold">{{ grade.name }}</td>
                        <td>
                          <span class="badge" :class="grade.level === 'Primaria' ? 'bg-info' : 'bg-primary'">
                            {{ grade.level }}
                          </span>
                        </td>
                        <td class="text-muted small">
                          {{ sections.filter(s => s.grade_id === grade.id).length }} sección(es)
                        </td>
                      </tr>
                      <tr v-if="grades.length === 0">
                        <td colspan="3" class="text-center py-5 text-muted">
                          No hay grados registrados
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

      <!-- TAB 3: Secciones -->
      <div class="tab-pane fade" :class="{show: activeTab === 'sections', active: activeTab === 'sections'}" role="tabpanel">
        <div class="row">
          <div class="col-md-4">
            <div class="card">
              <div class="card-header bg-danger text-white">
                <h6 class="mb-0"><i class="bi bi-plus-circle me-2"></i>Crear Sección</h6>
              </div>
              <div class="card-body">
                <form @submit.prevent="createSection">
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Grado</label>
                    <select v-model.number="sectionForm.grade_id" class="form-select" required>
                      <option :value="0">Seleccione un grado...</option>
                      <option v-for="grade in grades" :key="grade.id" :value="grade.id">
                        {{ grade.name }} - {{ grade.level }}
                      </option>
                    </select>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-semibold">Nombre de Sección</label>
                    <input 
                      v-model="sectionForm.name" 
                      type="text" 
                      class="form-control" 
                      placeholder="Ej: A, B, C" 
                      required
                      maxlength="2"
                    >
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label fw-semibold">Capacidad (Vacantes)</label>
                    <input 
                      v-model.number="sectionForm.capacity" 
                      type="number" 
                      class="form-control" 
                      required 
                      min="10" 
                      max="50"
                    >
                  </div>

                  <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>
                  <div v-if="success" class="alert alert-success py-2 small">{{ success }}</div>

                  <button type="submit" class="btn btn-danger w-100" :disabled="loading || sectionForm.grade_id === 0">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    Crear Sección
                  </button>
                </form>
              </div>
            </div>
          </div>

          <div class="col-md-8">
            <div class="card">
              <div class="card-header bg-white">
                <h6 class="mb-0">Secciones Registradas</h6>
              </div>
              <div class="card-body p-0">
                <div class="table-responsive">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th class="ps-4">Grado</th>
                        <th>Sección</th>
                        <th>Capacidad</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="section in sections" :key="section.id">
                        <td class="ps-4">
                          {{ grades.find(g => g.id === section.grade_id)?.name || 'N/A' }}
                        </td>
                        <td>
                          <span class="badge bg-secondary">Sección {{ section.name }}</span>
                        </td>
                        <td class="text-muted">{{ section.capacity }} vacantes</td>
                      </tr>
                      <tr v-if="sections.length === 0">
                        <td colspan="3" class="text-center py-5 text-muted">
                          No hay secciones registradas
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
    </div>
  </div>
</template>
