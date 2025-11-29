<template>
    <div>
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h3>Admin Dashboard</h3>
            <button class="btn btn-warning" @click="triggerReminders">Trigger Daily Reminders</button>
        </div>
        <div class="row">
            <div class="col-md-4" v-for="(v, k) in stats" :key="k">
                <div class="card p-3 mb-3 border-0 shadow-sm" :class="k === 'doctors' ? 'bg-soft-blue' : (k === 'patients' ? 'bg-soft-green' : 'bg-soft-purple')">
                    <h6 class="text-muted text-uppercase">{{ k }}</h6>
                    <h2 class="mb-0">{{ v }}</h2>
                </div>
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-md-6">
                <div class="input-group">
                    <input v-model="searchQuery" class="form-control" placeholder="Search doctors or patients..." @keyup.enter="doSearch">
                    <button class="btn btn-primary" @click="doSearch">Search</button>
                    <button class="btn btn-secondary" @click="viewAll">View All</button>
                </div>
            </div>
        </div>
        <div class="row" v-if="searchResults">
            <div class="col-12 mb-3">
                <div class="card p-3 border-0 shadow-sm">
                    <h5 class="text-primary">Search Results</h5>
                    <button class="btn btn-sm btn-outline-secondary mb-2" @click="searchResults=null">Clear</button>
                    <div v-if="searchResults.doctors.length">
                        <h6>Doctors</h6>
                        <ul class="list-group mb-3">
                            <li class="list-group-item d-flex justify-content-between align-items-center" v-for="d in searchResults.doctors" :key="d.id">
                                <span>
                                    {{d.username}} 
                                    <span v-if="d.is_blacklisted" class="badge bg-danger ms-1">Blacklisted</span>
                                    <span class="text-muted ms-2">
                                        ({{ d.spec }})
                                    </span>
                                </span>
                                <div>
                                    <button class="btn btn-sm btn-outline-info me-1" @click="viewUser(d, 'doctor')">View</button>
                                    <button class="btn btn-sm btn-outline-primary me-1" @click="openEditDoctor(d)">Edit</button>
                                    <button v-if="!d.is_blacklisted" class="btn btn-sm btn-outline-danger" @click="blacklistDoctor(d)">Blacklist</button>
                                    <button v-else class="btn btn-sm btn-outline-success" @click="unblacklistDoctor(d)">Unblacklist</button>
                                </div>
                            </li>
                        </ul>
                    </div>
                    <div v-if="searchResults.patients.length">
                        <h6>Patients</h6>
                        <ul class="list-group">
                            <li class="list-group-item d-flex justify-content-between align-items-center" v-for="p in searchResults.patients" :key="p.id">
                                <span>
                                    {{p.username}}
                                    <span v-if="p.is_active === false" class="badge bg-danger ms-1">Disabled</span>
                                    <span class="text-muted ms-2">({{ p.phone }})</span>
                                </span>
                                <div>
                                    <button class="btn btn-sm btn-outline-info me-1" @click="viewUser(p, 'patient')">View</button>
                                    <button class="btn btn-sm btn-outline-primary me-1" @click="openEditPatient(p)">Edit</button>
                                    <button v-if="p.is_active !== false" class="btn btn-sm btn-outline-danger" @click="blacklistPatient(p)">Blacklist</button>
                                    <button v-else class="btn btn-sm btn-outline-success" @click="unblacklistPatient(p)">Unblacklist</button>
                                </div>
                            </li>
                        </ul>
                    </div>
                    <div v-if="!searchResults.doctors.length && !searchResults.patients.length">No results found</div>
                </div>
            </div>
        </div>

        <!-- User Details Modal -->
        <div v-if="viewingUser" class="modal-backdrop fade show" style="background: rgba(0,0,0,0.5); z-index: 1060;"></div>
        <div v-if="viewingUser" class="modal d-block" tabindex="-1" style="z-index: 1065;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">User Details</h5>
                        <button class="btn-close" @click="viewingUser=null"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Username:</strong> {{ viewingUser.username }}</p>
                        <p v-if="viewingUser.role==='doctor'"><strong>Specialization:</strong> {{ viewingUser.spec }}</p>
                        <p v-if="viewingUser.role==='doctor' && viewingUser.availability"><strong>Availability:</strong> {{ viewingUser.availability }}</p>
                        <p v-if="viewingUser.role==='patient'"><strong>Phone:</strong> {{ viewingUser.phone }}</p>
                        <!-- Add more details if available from search result or fetch them -->
                        <p><strong>ID:</strong> {{ viewingUser.id }}</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" @click="viewingUser=null">Close</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Edit Doctor Modal -->
        <div v-if="editingDoc" class="modal-backdrop fade show" style="background: rgba(0,0,0,0.5); z-index: 1050;"></div>
        <div v-if="editingDoc" class="modal d-block" tabindex="-1" style="z-index: 1055;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Doctor: {{ editingDoc.username }}</h5>
                        <button class="btn-close" @click="editingDoc=null"></button>
                    </div>
                    <div class="modal-body">
                        <label>Name</label>
                        <input v-model="editingDoc.username" class="form-control mb-2">
                        <label>Specialization</label>
                        <input v-model="editingDoc.spec" class="form-control mb-2">
                        <label>Availability</label>
                        <div v-for="day in days" :key="day" class="mb-2 border-bottom pb-2">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" :id="'edit_doc_'+day" v-model="editingDoc.availabilityForm[day].enabled">
                                <label class="form-check-label" :for="'edit_doc_'+day">{{ dayLabels[day] || day }}</label>
                            </div>
                            <div v-if="editingDoc.availabilityForm[day].enabled" class="d-flex gap-2 mt-1">
                                <input type="time" class="form-control form-control-sm" v-model="editingDoc.availabilityForm[day].start">
                                <span>to</span>
                                <input type="time" class="form-control form-control-sm" v-model="editingDoc.availabilityForm[day].end">
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" @click="editingDoc=null">Close</button>
                        <button class="btn btn-primary" @click="saveDoctor">Save</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="card p-3 border-0 shadow-sm bg-light">
            <h5 class="text-success">Create Doctor</h5>
            <form @submit.prevent="createDoctor">
                <div class="row g-2">
                    <div class="col-md-3">
                        <input v-model="doc.username" class="form-control" placeholder="username" required />
                    </div>
                    <div class="col-md-3">
                        <input v-model="doc.email" class="form-control" placeholder="email" />
                    </div>
                    <div class="col-md-3">
                        <input v-model="doc.specialization" class="form-control" placeholder="specialization" />
                    </div>
                    <!-- <div class="col-md-3">
                        <input v-model="doc.department" class="form-control" placeholder="department" />
                    </div> -->

                    <!-- Availability field (JSON) -->
                    <!-- Availability field (Structured) -->
                    <div class="col-12 mt-2">
                        <label class="form-label">Availability</label>
                        <div class="row">
                            <div class="col-md-4 mb-2" v-for="day in days" :key="day">
                                <div class="border p-2 rounded">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" :id="'new_doc_'+day" v-model="doc.availabilityForm[day].enabled">
                                        <label class="form-check-label" :for="'new_doc_'+day">{{ dayLabels[day] || day }}</label>
                                    </div>
                                    <div v-if="doc.availabilityForm[day].enabled" class="d-flex gap-1 mt-1">
                                        <input type="time" class="form-control form-control-sm" v-model="doc.availabilityForm[day].start">
                                        <input type="time" class="form-control form-control-sm" v-model="doc.availabilityForm[day].end">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-12 mt-2">
                        <button class="btn btn-success">Create Doctor</button>
                    </div>
                </div>
            </form>
        </div>
        <div class="card p-3 mt-3 border-0 shadow-sm">
            <h5 class="text-info">All Appointments</h5><button class="btn btn-sm btn-secondary mb-2" @click="loadAppts">Reload</button>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient</th>
                        <th>Doctor</th>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="a in appts" :key="a.id">
                        <td>{{ a.id }}</td>
                        <td>{{ a.patient }}</td>
                        <td>{{ a.doctor }}</td>
                        <td>{{ a.date }}</td>
                        <td>{{ a.time }}</td>
                        <td>{{ a.status }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script>
import api, { setAuth } from '../services/api'
export default {
  data(){ return {
    stats: {},
    doc: { username:'', email:'', specialization:'', department:'', availability:'' },
    appts: [],
    searchQuery: '',
    searchResults: null,
    searchResults: null,
    editingDoc: null,
    editingPat: null,
    viewingUser: null,
    days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    dayLabels: {}
  }},
  created(){ 
      const token = localStorage.getItem('hms_token'); 
      if(token) setAuth(token); 
      this.initDocForm();
      this.initDocForm();
      this.loadStats(); 
      this.loadAppts();
      this.updateDayLabels();
  },
  methods:{
    initDocForm() {
        this.doc = { username:'', email:'', specialization:'', department:'', availabilityForm: {} };
        this.days.forEach(d => {
            this.doc.availabilityForm[d] = { enabled: false, start: '09:00', end: '17:00' };
        });
    },
    viewUser(u, role) {
        this.viewingUser = { ...u, role };
    },
    async viewAll() {
        this.searchQuery = '';
        await this.doSearch(true);
    },
    async doSearch(allowEmpty = false){
        if(!this.searchQuery && !allowEmpty) return;
        try{
            const r = await api.get('/admin/search?q='+this.searchQuery);
            this.searchResults = r.data;
        }catch(e){ console.error(e) }
    },
    async loadStats(){ try{ const r = await api.get('/admin/stats'); this.stats = r.data } catch(e){ console.error(e) }},
    async createDoctor(){
      try{
        // try to parse availability to send JSON object, otherwise send raw string
        let payload = { ...this.doc }
        
        let avail = {};
        for(let d of this.days) {
            if(this.doc.availabilityForm[d].enabled) {
                avail[d] = [this.doc.availabilityForm[d].start, this.doc.availabilityForm[d].end];
            }
        }
        payload.availability = avail;

        const r = await api.post('/admin/doctors', payload)
        alert('created')
        this.initDocForm();
        await this.loadStats()
      }catch(e){ alert(e.response?.data?.msg || 'Error creating doctor') }
    },
    async loadAppts(){ try{ const r = await api.get('/admin/appointments'); this.appts = r.data } catch(e){ console.error(e) } },
    
    openEditDoctor(d) {
        let availForm = {};
        this.days.forEach(day => availForm[day] = { enabled: false, start: '09:00', end: '17:00' });
        
        try {
            if(d.availability) {
                let parsed = typeof d.availability === 'string' ? JSON.parse(d.availability) : d.availability;
                for(let day in parsed) {
                    if(this.days.includes(day) && Array.isArray(parsed[day]) && parsed[day].length >= 2) {
                        availForm[day] = { enabled: true, start: parsed[day][0], end: parsed[day][1] };
                    }
                }
            }
        } catch(e) { console.log('Error parsing availability', e) }

        this.editingDoc = { ...d, availabilityForm: availForm }; 
    },
    openEditPatient(p) {
        this.editingPat = { ...p };
    },
    async saveDoctor() {
        try {
            let avail = {};
            for(let d of this.days) {
                if(this.editingDoc.availabilityForm[d].enabled) {
                    avail[d] = [this.editingDoc.availabilityForm[d].start, this.editingDoc.availabilityForm[d].end];
                }
            }
            await api.put(`/admin/doctors/${this.editingDoc.id}`, {
                username: this.editingDoc.username,
                specialization: this.editingDoc.spec,
                availability: avail
            });
            alert('Updated');
            this.editingDoc = null;
            this.viewAll();
        } catch(e) { alert('Error updating') }
    },
    async blacklistDoctor(d) {
        try {
            await api.put(`/admin/doctors/${d.id}`, { is_blacklisted: true });
            alert('Blacklisted');
            this.viewAll();
        } catch(e) { alert('Error') }
    },
    async blacklistPatient(p) {
        try {
            await api.post(`/admin/patients/${p.id}/blacklist`);
            alert('Blacklisted');
            this.viewAll();
        } catch(e) { alert('Error') }
    },
    async unblacklistPatient(p) {
        try {
            await api.post(`/admin/patients/${p.id}/unblacklist`);
            alert('Unblacklisted');
            this.viewAll();
        } catch(e) { alert('Error') }
    },
    async unblacklistDoctor(d) {
        try {
            await api.put(`/admin/doctors/${d.id}`, { is_blacklisted: false });
            alert('Unblacklisted');
            this.viewAll();
        } catch(e) { alert('Error') }
    },
    async triggerReminders() {
        if(!confirm('Are you sure you want to trigger daily reminders now?')) return;
        try {
            const r = await api.post('/admin/trigger_reminders');
            alert(r.data.msg);
        } catch(e) { alert(e.response?.data?.msg || 'Error triggering reminders') }
    },
    updateDayLabels() {
        const today = new Date();
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const todayIndex = today.getDay();
        
        // Reorder days to start from today
        const sortedDays = [];
        for(let i=0; i<7; i++) {
            sortedDays.push(dayNames[(todayIndex + i) % 7]);
        }
        this.days = sortedDays;

        const daysMap = { 'Sun':0, 'Mon':1, 'Tue':2, 'Wed':3, 'Thu':4, 'Fri':5, 'Sat':6 };
        this.days.forEach(d => {
            const targetDay = daysMap[d];
            const currentDay = today.getDay();
            let diff = targetDay - currentDay;
            if (diff < 0) diff += 7; // Next occurrence
            const nextDate = new Date(today);
            nextDate.setDate(today.getDate() + diff);
            const dateStr = nextDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            this.dayLabels[d] = `${d} (${dateStr})`;
        });
    }
  }
}
</script>

<style scoped>
.bg-soft-blue { background-color: #e3f2fd; }
.bg-soft-green { background-color: #e8f5e9; }
.bg-soft-purple { background-color: #f3e5f5; }
.card { border-radius: 10px; }
.btn { border-radius: 20px; }
</style>
