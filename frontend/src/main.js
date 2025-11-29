import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'   // <-- add this line

import api, { setAuth } from './services/api'

const token = localStorage.getItem('hms_token')
if (token) setAuth(token)

createApp(App).use(router).mount('#app')
