<template>
  <div class="d-flex justify-content-center align-items-center vh-100 bg-gradient-light">
    <div class="card p-4 shadow-lg border-0" style="width: 350px; border-radius: 15px;">
      <h3 class="text-center mb-4 text-success">Patient Registration</h3>
      <form @submit.prevent="doRegister">
        <div class="mb-3">
            <label class="form-label text-muted">Username</label>
            <input v-model="form.username" class="form-control form-control-lg" placeholder="Choose a username" required>
        </div>
        <div class="mb-3">
            <label class="form-label text-muted">Email</label>
            <input v-model="form.email" type="email" class="form-control form-control-lg" placeholder="Enter your email" required>
        </div>
        <div class="mb-3">
            <label class="form-label text-muted">Password</label>
            <input v-model="form.password" type="password" class="form-control form-control-lg" placeholder="Create a password" required>
        </div>
        <div class="mb-3">
            <label class="form-label text-muted">Phone</label>
            <input v-model="form.phone" class="form-control form-control-lg" placeholder="Contact number">
        </div>
        <button class="btn btn-success w-100 mt-3 btn-lg">Register & Login</button>
      </form>
      <div v-if="msg" class="alert alert-danger mt-3">{{ msg }}</div>
      <div class="text-center mt-3">
          <router-link to="/login" class="text-decoration-none">Already have an account? Login</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import api, { setAuth } from '../services/api';

export default {
  data() {
    return {
      form: { username: '', email: '', password: '', phone: '' },
      msg: null
    }
  },
  methods: {
    async doRegister() {
      try {
        await api.post('/auth/register', this.form);
        // Auto login
        const r = await api.post('/auth/login', { username: this.form.username, password: this.form.password });
        const token = r.data.access_token;
        const user = { username: r.data.username, role: r.data.role, id: r.data.id };
        localStorage.setItem('hms_token', token);
        localStorage.setItem('hms_user', JSON.stringify(user));
        setAuth(token);
        this.$emit('auth-changed', user);
        this.$router.push('/patient');
      } catch (e) {
        this.msg = e.response?.data?.msg || 'Registration failed';
      }
    }
  }
};
</script>

<style scoped>
.bg-gradient-light {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.card { background: white; }
.btn { border-radius: 30px; }
.form-control { border-radius: 10px; background-color: #f1f3f5; border: none; }
.form-control:focus { background-color: white; box-shadow: 0 0 0 0.25rem rgba(25, 135, 84, 0.15); }
</style>
