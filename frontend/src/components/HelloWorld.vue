<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

defineProps<{ msg: string }>()

const apiStatus = ref<string>('Conectando...')

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:8000/health')
    apiStatus.value = `Backend Status: ${response.data.status}`
  } catch (error) {
    apiStatus.value = 'Error conectando al backend'
    console.error(error)
  }
})
</script>

<template>
  <h1>{{ msg }}</h1>

  <div class="card">
    <p>
      Estado del sistema: <strong>{{ apiStatus }}</strong>
    </p>
    <p>
      Bienvenido al sistema de matrícula escolar.
    </p>
  </div>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
