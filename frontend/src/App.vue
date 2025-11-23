<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const isAuthenticated = ref(false);

const checkAuth = () => {
  isAuthenticated.value = !!localStorage.getItem('token');
};

onMounted(() => {
  checkAuth();
});

watch(route, () => {
  checkAuth();
});

const logout = () => {
  localStorage.removeItem('token');
  isAuthenticated.value = false;
  router.push('/login');
};
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-mrc mb-4">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center gap-2" href="#">
        <i class="bi bi-mortarboard-fill fs-4"></i>
        <span>I.E. Mariscal Ramón Castilla</span>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" v-if="isAuthenticated">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav" v-if="isAuthenticated">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/students">Alumnos</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/enrollments">Matrícula</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/documents">Documentos</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/configuration">Configuración</router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="#" @click.prevent="logout">Salir</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container">
    <router-view></router-view>
  </div>
</template>

<style>
/* MRC Red Theme */
.bg-mrc {
  background-color: #b71c1c !important; /* Rojo oscuro institucional */
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

body {
  background-color: #f8f9fa;
}

.card {
  border: none;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  border-radius: 8px;
}

.btn-primary {
  background-color: #d32f2f;
  border-color: #d32f2f;
}

.btn-primary:hover {
  background-color: #b71c1c;
  border-color: #b71c1c;
}

.text-primary {
  color: #d32f2f !important;
}

.btn-outline-primary {
  color: #d32f2f;
  border-color: #d32f2f;
}

.btn-outline-primary:hover {
  background-color: #d32f2f;
  color: white;
}
</style>
