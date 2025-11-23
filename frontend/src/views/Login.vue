<template>
  <div class="mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow-sm">
          <div class="card-header bg-danger text-white text-center">
            <h4 class="mb-0">Iniciar Sesión</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="email" class="form-label">Correo Electrónico</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="email"
                  required
                  placeholder="admin@mrc.edu.pe"
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Contraseña</label>
                <input
                  type="password"
                  class="form-control"
                  id="password"
                  v-model="password"
                  required
                  placeholder="********"
                />
              </div>
              <div v-if="error" class="alert alert-danger" role="alert">
                {{ error }}
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-danger" :disabled="loading">
                  {{ loading ? 'Ingresando...' : 'Ingresar' }}
                </button>
              </div>
            </form>
          </div>
          <div class="card-footer text-center text-muted">
            <small>Sistema de Matrícula MRC</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const router = useRouter();

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const formData = new FormData();
    formData.append('username', email.value);
    formData.append('password', password.value);

    const response = await api.post('/login/access-token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    
    // Configurar el token en los headers por defecto para futuras peticiones
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    router.push('/');
  } catch (err: any) {
    console.error(err);
    error.value = 'Credenciales inválidas o error en el servidor.';
  } finally {
    loading.value = false;
  }
};
</script>
