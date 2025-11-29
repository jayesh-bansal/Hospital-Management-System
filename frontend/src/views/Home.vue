<template>
  <div class="container-fluid d-flex justify-content-center align-items-center vh-100 bg-gradient-light">
    <div class="card p-5 shadow-lg border-0 text-center" style="max-width: 500px; border-radius: 20px;">
      <h1 class="display-4 text-primary mb-4 fw-bold">Welcome to HMS</h1>
      <p class="lead text-muted mb-4">Your health, our priority. Manage appointments with ease.</p>
      <div class="d-grid gap-3">
        <router-link to="/login" class="btn btn-primary btn-lg rounded-pill shadow-sm">Login</router-link>
        <router-link to="/register" class="btn btn-outline-primary btn-lg rounded-pill">Register</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-gradient-light {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>
