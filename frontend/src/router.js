import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import DoctorDashboard from './views/DoctorDashboard.vue'
import PatientDashboard from './views/PatientDashboard.vue'
import Profile from './views/Profile.vue'
const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/admin', component: AdminDashboard },
    { path: '/doctor', component: DoctorDashboard },
    { path: '/patient', component: PatientDashboard },
    { path: '/profile', component: Profile }
]
export default createRouter({history:createWebHistory(),routes})
