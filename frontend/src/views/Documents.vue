<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

// Interfaces
interface Document {
  id: number
  enrollment_id: number
  type: string
  file_url: string
  status: string
  uploaded_at: string
}

interface Enrollment {
  id: number
  student_id: number
  academic_year_id: number
  grade_id: number
  section_id: number
  status: string
  student?: {
    first_name: string
    last_name: string
    dni: string
  }
  grade?: { name: string }
  section?: { name: string }
}

// State
const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')

const enrollments = ref<Enrollment[]>([])
const documents = ref<Document[]>([])
const selectedEnrollment = ref<number | null>(null)

// Upload form
const uploadForm = ref({
  type: '',
  file: null as File | null
})

const documentTypes = [
  'DNI del Alumno',
  'DNI del Apoderado',
  'Certificado de Estudios',
  'Partida de Nacimiento',
  'Certificado de Vacunación',
  'Foto Tamaño Carnet',
  'Otro'
]

// Computed
const filteredDocuments = computed(() => {
  if (!selectedEnrollment.value) return []
  return documents.value.filter(doc => doc.enrollment_id === selectedEnrollment.value)
})

const selectedEnrollmentData = computed(() => {
  return enrollments.value.find(e => e.id === selectedEnrollment.value)
})

// Methods
async function fetchEnrollments() {
  try {
    loading.value = true
    const response = await api.get('/enrollments')
    enrollments.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al cargar matrículas'
  } finally {
    loading.value = false
  }
}

async function fetchDocuments() {
  if (!selectedEnrollment.value) return
  
  try {
    loading.value = true
    const response = await api.get('/documents', {
      params: { enrollment_id: selectedEnrollment.value }
    })
    documents.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al cargar documentos'
  } finally {
    loading.value = false
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadForm.value.file = target.files[0]
  }
}

async function uploadDocument() {
  if (!selectedEnrollment.value || !uploadForm.value.type || !uploadForm.value.file) {
    error.value = 'Por favor complete todos los campos'
    return
  }

  try {
    loading.value = true
    error.value = ''
    
    const formData = new FormData()
    formData.append('enrollment_id', selectedEnrollment.value.toString())
    formData.append('type', uploadForm.value.type)
    formData.append('file', uploadForm.value.file)

    await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    success.value = 'Documento subido correctamente'
    uploadForm.value = { type: '', file: null }
    
    // Reset file input
    const fileInput = document.getElementById('fileInput') as HTMLInputElement
    if (fileInput) fileInput.value = ''
    
    await fetchDocuments()
    
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al subir documento'
  } finally {
    loading.value = false
  }
}

async function changeDocumentStatus(docId: number, newStatus: string) {
  try {
    await api.patch(`/documents/${docId}/status?status=${newStatus}`)
    success.value = 'Estado actualizado correctamente'
    await fetchDocuments()
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al cambiar estado'
  }
}

async function deleteDocument(docId: number) {
  if (!confirm('¿Está seguro de eliminar este documento?')) return

  try {
    await api.delete(`/documents/${docId}`)
    success.value = 'Documento eliminado correctamente'
    await fetchDocuments()
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al eliminar documento'
  }
}

function selectEnrollment(enrollmentId: number) {
  selectedEnrollment.value = enrollmentId
  fetchDocuments()
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'Validado': return 'bg-success'
    case 'Observado': return 'bg-warning'
    default: return 'bg-secondary'
  }
}

onMounted(async () => {
  await fetchEnrollments()
  
  // Auto-seleccionar matrícula si viene del query param
  const enrollmentIdParam = router.currentRoute.value.query.enrollment
  if (enrollmentIdParam) {
    const enrollmentId = parseInt(enrollmentIdParam as string)
    if (!isNaN(enrollmentId) && enrollments.value.find((e: Enrollment) => e.id === enrollmentId)) {
      selectEnrollment(enrollmentId)
    }
  }
})
</script>

<template>
  <div class="container-fluid py-4">
    <div class="row mb-4">
      <div class="col">
        <h2 class="mb-0">
          <i class="bi bi-file-earmark-text"></i> Gestión de Documentos
        </h2>
        <p class="text-muted">Administra los documentos requeridos para cada matrícula</p>
      </div>
    </div>

    <!-- Alerts -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = ''"></button>
    </div>

    <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ success }}
      <button type="button" class="btn-close" @click="success = ''"></button>
    </div>

    <div class="row">
      <!-- Lista de Matrículas -->
      <div class="col-md-4">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Matrículas Activas</h5>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush" style="max-height: 600px; overflow-y: auto;">
              <button
                v-for="enrollment in enrollments"
                :key="enrollment.id"
                @click="selectEnrollment(enrollment.id)"
                class="list-group-item list-group-item-action"
                :class="{ 'active': selectedEnrollment === enrollment.id }"
              >
                <div class="d-flex w-100 justify-content-between">
                  <h6 class="mb-1">
                    {{ enrollment.student?.first_name }} {{ enrollment.student?.last_name }}
                  </h6>
                  <small>
                    <span class="badge" :class="enrollment.status === 'Matriculado' ? 'bg-success' : 'bg-warning'">
                      {{ enrollment.status }}
                    </span>
                  </small>
                </div>
                <p class="mb-1 small">
                  DNI: {{ enrollment.student?.dni }}
                </p>
                <small class="text-muted">
                  {{ enrollment.grade?.name }} - {{ enrollment.section?.name }}
                </small>
              </button>
              <div v-if="enrollments.length === 0" class="text-center py-4 text-muted">
                No hay matrículas registradas
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Gestión de Documentos -->
      <div class="col-md-8">
        <div v-if="!selectedEnrollment" class="card shadow-sm">
          <div class="card-body text-center py-5">
            <i class="bi bi-arrow-left-circle" style="font-size: 3rem; color: #6c757d;"></i>
            <p class="text-muted mt-3">Seleccione una matrícula para gestionar sus documentos</p>
          </div>
        </div>

        <div v-else>
          <!-- Info de la matrícula seleccionada -->
          <div class="card shadow-sm mb-3">
            <div class="card-body">
              <h5>
                <i class="bi bi-person-badge"></i>
                {{ selectedEnrollmentData?.student?.first_name }} {{ selectedEnrollmentData?.student?.last_name }}
              </h5>
              <p class="mb-0 text-muted">
                {{ selectedEnrollmentData?.grade?.name }} - {{ selectedEnrollmentData?.section?.name }}
              </p>
            </div>
          </div>

          <!-- Formulario de subida -->
          <div class="card shadow-sm mb-3">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">
                <i class="bi bi-cloud-upload"></i> Subir Documento
              </h5>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-5">
                  <label class="form-label">Tipo de Documento</label>
                  <select v-model="uploadForm.type" class="form-select" required>
                    <option value="">Seleccione...</option>
                    <option v-for="type in documentTypes" :key="type" :value="type">
                      {{ type }}
                    </option>
                  </select>
                </div>
                <div class="col-md-5">
                  <label class="form-label">Archivo (PDF, JPG, PNG, DOC)</label>
                  <input
                    id="fileInput"
                    type="file"
                    class="form-control"
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                    @change="handleFileChange"
                    required
                  />
                </div>
                <div class="col-md-2 d-flex align-items-end">
                  <button
                    @click="uploadDocument"
                    class="btn btn-success w-100"
                    :disabled="loading || !uploadForm.type || !uploadForm.file"
                  >
                    <i class="bi bi-upload"></i> Subir
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Lista de documentos -->
          <div class="card shadow-sm">
            <div class="card-header bg-info text-white">
              <h5 class="mb-0">
                <i class="bi bi-file-earmark-check"></i> Documentos Subidos
              </h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Tipo</th>
                      <th>Fecha de Subida</th>
                      <th>Estado</th>
                      <th class="text-center">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="doc in filteredDocuments" :key="doc.id">
                      <td>
                        <i class="bi bi-file-earmark-pdf text-danger"></i>
                        {{ doc.type }}
                      </td>
                      <td>{{ new Date(doc.uploaded_at).toLocaleDateString('es-PE') }}</td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(doc.status)">
                          {{ doc.status }}
                        </span>
                      </td>
                      <td class="text-center">
                        <div class="btn-group" role="group">
                          <button
                            v-if="doc.status !== 'Validado'"
                            @click="changeDocumentStatus(doc.id, 'Validado')"
                            class="btn btn-sm btn-success"
                            title="Validar documento"
                          >
                            <i class="bi bi-check-circle"></i>
                          </button>
                          <button
                            v-if="doc.status !== 'Observado'"
                            @click="changeDocumentStatus(doc.id, 'Observado')"
                            class="btn btn-sm btn-warning"
                            title="Observar documento"
                          >
                            <i class="bi bi-exclamation-triangle"></i>
                          </button>
                          <button
                            @click="deleteDocument(doc.id)"
                            class="btn btn-sm btn-danger"
                            title="Eliminar documento"
                          >
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="filteredDocuments.length === 0">
                      <td colspan="4" class="text-center text-muted py-4">
                        <i class="bi bi-inbox" style="font-size: 2rem;"></i>
                        <p class="mb-0 mt-2">No hay documentos subidos aún</p>
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
</template>

<style scoped>
.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-group .btn {
  padding: 0.25rem 0.5rem;
}
</style>
