<template>
    <div>
        <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
            <div class="container"><a class="navbar-brand" href="/">HMS</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item" v-if="!user"><router-link class="nav-link" to="/login">Login</router-link>
                        </li>
                        <li class="nav-item" v-if="!user"><router-link class="nav-link"
                                to="/register">Register</router-link></li>
                        <li class="nav-item dropdown" v-if="user"><a class="nav-link dropdown-toggle" href="#"
                                role="button" data-bs-toggle="dropdown">{{ user.username }}</a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><a class="dropdown-item" href="#" @click.prevent="goProfile">Profile</a></li>
                                <li><a class="dropdown-item" href="#" @click.prevent="logout">Logout</a></li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
        <div class="container py-4"><router-view @auth-changed="onAuthChanged"></router-view></div>
    </div>
</template>

<script>
import { setAuth } from './services/api'

export default {
  data() {
    return { user: null }
  },

  created() {
    const rawUser = localStorage.getItem('hms_user');
    const token = localStorage.getItem('hms_token');

    // SAFE PARSE — prevents crashing on bad data
    if (rawUser && rawUser !== "undefined" && rawUser !== "null") {
      try {
        this.user = JSON.parse(rawUser);
      } catch (e) {
        console.warn("Corrupted user data, clearing storage.");
        localStorage.removeItem('hms_user');
      }
    }

    // Restore token
    if (token && token !== "undefined") {
      setAuth(token);
    }
  },

  methods: {
    logout() {
      setAuth(null);
      localStorage.removeItem('hms_token');
      localStorage.removeItem('hms_user');
      this.user = null;
      this.$router.push('/');
    },

    goProfile() {
      this.$router.push('/profile');
    },

    onAuthChanged(u) {
      this.user = u;
    }
  }
}
</script>
