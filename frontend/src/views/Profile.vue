<template>
  <div class="container mt-5">
    <button class="btn btn-secondary mb-3" @click="$router.go(-1)">&larr; Back</button>
    <h3>Edit Profile</h3>
    <div class="card p-4 mt-3" style="max-width: 500px">
      <form @submit.prevent="updateProfile">
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input class="form-control" :value="user.username" disabled>
          <small class="text-muted">Username cannot be changed</small>
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-control">
        </div>
        <div class="mb-3" v-if="user.role === 'patient'">
          <label class="form-label">Phone</label>
          <input v-model="form.phone" type="text" class="form-control">
        </div>
        <div class="mb-3">
          <label class="form-label">New Password (leave blank to keep current)</label>
          <input v-model="form.password" type="password" class="form-control">
        </div>
        <button class="btn btn-primary" :disabled="loading">Update Profile</button>
      </form>
      <div v-if="msg" class="alert alert-info mt-3">{{ msg }}</div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  data() {
    return {
      user: {},
      form: { email: '', password: '', phone: '' },
      msg: '',
      loading: false
    }
  },
  created() {
    this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
        try {
            const r = await api.get('/auth/profile');
            this.user = r.data;
            this.form.email = this.user.email || '';
            this.form.phone = this.user.phone || '';
        } catch(e) { console.error(e); }
    },
    async updateProfile() {
      this.loading = true;
      this.msg = '';
      try {
        const payload = { email: this.form.email };
        if (this.form.password) payload.password = this.form.password;
        if (this.form.phone) payload.phone = this.form.phone;

        await api.put('/auth/profile', payload);
        this.msg = 'Profile updated successfully';
        
        // Update local user object if email changed
        // Note: In a real app we might want to refresh the token or user details from backend
        this.user.email = this.form.email;
        localStorage.setItem('hms_user', JSON.stringify(this.user));

      } catch (e) {
        this.msg = e.response?.data?.msg || 'Error updating profile';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
