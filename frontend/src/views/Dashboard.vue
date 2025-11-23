<script setup lang="ts">
</script>

<template>
  <div class="row">
    <div class="col-12 mb-4">
      <h2 class="fw-light">Panel de Control</h2>
      <p class="text-muted">Bienvenido al sistema de gestión escolar.</p>
    </div>

    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body text-center p-4">
          <i class="bi bi-people text-primary display-4 mb-3"></i>
          <h5 class="card-title">Alumnos</h5>
          <p class="card-text">Gestionar registro de alumnos y apoderados.</p>
          <router-link to="/students" class="btn btn-outline-primary btn-sm">Ir a Alumnos</router-link>
        </div>
      </div>
    </div>

    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body text-center p-4">
          <i class="bi bi-journal-check text-success display-4 mb-3"></i>
          <h5 class="card-title">Matrículas</h5>
          <p class="card-text">Procesar nuevas matrículas y vacantes.</p>
          <router-link to="/enrollments" class="btn btn-outline-success btn-sm">Ir a Matrículas</router-link>
        </div>
      </div>
    </div>

    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body text-center p-4">
          <i class="bi bi-gear text-danger display-4 mb-3"></i>
          <h5 class="card-title">Configuración</h5>
          <p class="card-text">Años académicos, grados y secciones.</p>
          <router-link to="/configuration" class="btn btn-outline-danger btn-sm">Ir a Configuración</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
