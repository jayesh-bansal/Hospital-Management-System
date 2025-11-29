<template>
  <div class="d-flex justify-content-center align-items-center vh-100 bg-gradient-light">
      <div class="card p-4 shadow-lg border-0" style="width: 350px; border-radius: 15px;">
        <h3 class="text-center mb-4 text-primary">Hospital Login</h3>

        <form @submit.prevent="login">
          <div class="mb-3">
              <label class="form-label text-muted">Username</label>
              <input v-model="username" class="form-control form-control-lg" placeholder="Enter username">
          </div>
          <div class="mb-3">
              <label class="form-label text-muted">Password</label>
              <input v-model="password" type="password" class="form-control form-control-lg" placeholder="Enter password">
          </div>
          <div v-if="errorMsg" class="alert alert-danger mt-2">{{ errorMsg }}</div>
          <button class="btn btn-primary w-100 mt-3 btn-lg" type="submit">Sign In</button>
        </form>
      </div>
  </div>
</template>

<script>
import api, { setAuth } from '../services/api'

export default {
  data() {
    return {
      username: "",
      password: "",
      errorMsg: null
    }
  },

  methods: {
    async login() {
      console.log("LOGIN CALLED, DATA:", this.username, this.password);  // debug

      try {
        const r = await api.post('/auth/login', {
          username: this.username,
          password: this.password
        });

        const token = r.data.access_token;
        const user = {
          username: r.data.username,
          role: r.data.role,
          id: r.data.id
        };

        localStorage.setItem('hms_token', token);
        localStorage.setItem('hms_user', JSON.stringify(user));
        
        setAuth(token);
        this.$emit('auth-changed', user);

        if (user.role === 'admin') this.$router.push('/admin');
        else if (user.role === 'doctor') this.$router.push('/doctor');
        else this.$router.push('/patient');
      } catch (e) {
        this.errorMsg = e.response?.data?.msg || "Login failed";
      }
    }
  }
}
</script>

<style scoped>
.bg-gradient-light {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.bg-light { background-color: #f8f9fa !important; }
.card { background: white; }
.btn { border-radius: 30px; }
.form-control { border-radius: 10px; background-color: #f1f3f5; border: none; }
.form-control:focus { background-color: white; box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15); }
</style>
