<template>
  <div>
    <h3>Doctor Dashboard</h3>
    
    <div class="row">
        <div class="col-md-6">
            <div class="card p-3 mb-3 bg-soft-blue border-0 shadow-sm">
                <h5 class="text-primary">Active Appointments</h5>
                <button class="btn btn-sm btn-secondary mb-2" @click="loadAppts">Reload</button>
                <ul class="list-group">
                    <li class="list-group-item" v-for="a in activeAppts" :key="a.id">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <strong>{{ a.date }} {{ a.time }}</strong>
                                <div class="text-muted">{{ a.patient }}</div>
                            </div>
                            <div><button class="btn btn-sm btn-success" @click="completeAppt(a)">Complete</button></div>
                        </div>
                    </li>
                    <li v-if="!activeAppts.length" class="list-group-item text-muted">No active appointments</li>
                </ul>
            </div>

            <div class="card p-3 mb-3 bg-soft-purple border-0 shadow-sm">
                <h5 class="text-purple">Appointment History</h5>
                <div class="table-responsive" v-if="historyAppts.length">
                <table class="table table-sm table-hover">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Date</th>
                            <th>Patient</th>
                            <th>Diagnosis</th>
                            <th>Prescription</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="a in historyAppts" :key="a.id">
                            <td>{{ a.id }}</td>
                            <td>{{ a.date }} {{ a.time }}</td>
                            <td>{{ a.patient }}</td>
                            <td>{{ a.diagnosis }}</td>
                            <td>{{ a.prescription }}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" @click="editTreatment(a)">Edit</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                </div>
                <div v-else class="text-muted">No completed appointments</div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card p-3 mb-3 bg-soft-green border-0 shadow-sm">
                <h5 class="text-success">My Patients</h5>
                <ul class="list-group">
                    <li class="list-group-item" v-for="p in patients" :key="p.id">
                        <strong>{{ p.username }}</strong> 
                        <div class="text-muted small">
                            {{ p.gender }} {{ p.phone }} <br>
                            {{ p.email }}
                        </div>
                    </li>
                    <li v-if="!patients.length" class="list-group-item text-muted">No patients yet</li>
                </ul>
            </div>
            
            <div class="card p-3 mb-3 bg-soft-orange border-0 shadow-sm">
                <h5 class="text-orange">Set Availability</h5>
                <div v-for="day in days" :key="day" class="mb-2">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" :id="'doc_avail_'+day" v-model="availabilityForm[day].enabled">
                        <label class="form-check-label" :for="'doc_avail_'+day">{{ dayLabels[day] || day }}</label>
                    </div>
                    <div v-if="availabilityForm[day].enabled" class="d-flex gap-2 mt-1">
                        <input type="time" class="form-control form-control-sm" v-model="availabilityForm[day].start">
                        <span>to</span>
                        <input type="time" class="form-control form-control-sm" v-model="availabilityForm[day].end">
                    </div>
                </div>
                <button class="btn btn-primary w-100 mt-2" @click="saveAvailability">Save Availability</button>
            </div>
        </div>
    </div>
  </div>
</template>
<script>
import api, { setAuth } from '../services/api';

export default {
  data() {
    return {
      appts: [],
      patients: [],
      days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      dayLabels: {},
      availabilityForm: {
        Mon: { enabled: false, start: '09:00', end: '17:00' },
        Tue: { enabled: false, start: '09:00', end: '17:00' },
        Wed: { enabled: false, start: '09:00', end: '17:00' },
        Thu: { enabled: false, start: '09:00', end: '17:00' },
        Fri: { enabled: false, start: '09:00', end: '17:00' },
        Sat: { enabled: false, start: '09:00', end: '17:00' },
        Sun: { enabled: false, start: '09:00', end: '17:00' }
      }
    }
  },
  computed: {
    activeAppts() {
        return this.appts.filter(a => a.status !== 'Completed' && a.status !== 'Cancelled');
    },
    historyAppts() {
        return this.appts.filter(a => a.status === 'Completed');
    }
  },
  created() {
    const t = localStorage.getItem('hms_token');
    if (t) setAuth(t);
    this.loadAppts();
    this.loadPatients();
    this.updateDayLabels();
  },
  methods: {
    async loadAppts() {
      try {
        const r = await api.get('/doctor/dashboard'); // Updated endpoint to get availability too
        this.appts = r.data.appointments;
        if(r.data.availability) {
            this.prefillAvailability(r.data.availability);
        }
      } catch (e) { console.error(e) }
    },
    prefillAvailability(jsonStr) {
        try {
            const parsed = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
            for(const day in parsed) {
                if(this.days.includes(day) && Array.isArray(parsed[day]) && parsed[day].length >= 2) {
                    this.availabilityForm[day].enabled = true;
                    this.availabilityForm[day].start = parsed[day][0];
                    this.availabilityForm[day].end = parsed[day][1];
                }
            }
        } catch(e) { console.error("Error parsing availability", e); }
    },
    async completeAppt(a) {
      const diagnosis = prompt('Diagnosis');
      if (!diagnosis) return;
      const prescription = prompt('Prescription') || ''; 
      try {
        await api.post(`/appointments/${a.id}/complete`, { diagnosis, prescription });
        alert('Completed');
        this.loadAppts();
      } catch (e) { 
          console.error(e);
          alert(e.response?.data?.msg || 'Error completing appointment');
      }
    },
    async editTreatment(a) {
        const diagnosis = prompt('New Diagnosis (leave empty to keep current)');
        const prescription = prompt('New Prescription (leave empty to keep current)');
        if(diagnosis === null && prescription === null) return; // Cancelled

        let payload = {};
        if(diagnosis) payload.diagnosis = diagnosis;
        if(prescription) payload.prescription = prescription;
        
        if(Object.keys(payload).length === 0) return;

        try {
            await api.put(`/doctor/appointments/${a.id}/treatment`, payload);
            alert('Treatment updated');
        } catch(e) {
            console.error(e);
            alert('Error updating treatment');
        }
    },
    async loadPatients() {
      try {
        const r = await api.get('/doctor/my_patients');
        this.patients = r.data;
      } catch (e) { console.error(e) }
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
            if (diff < 0) diff += 7; 
            const nextDate = new Date(today);
            nextDate.setDate(today.getDate() + diff);
            const dateStr = nextDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            this.dayLabels[d] = `${d} (${dateStr})`;
        });
    },
    async saveAvailability() {
      try {
        let payload = {};
        for (const day of this.days) {
            if (this.availabilityForm[day].enabled) {
                payload[day] = [this.availabilityForm[day].start, this.availabilityForm[day].end];
            }
        }
        await api.post('/doctor/set_availability', { availability: payload });
        alert('Availability Saved');
      } catch (e) { alert('Error saving') }
    }
  }
};
</script>

<style scoped>
.bg-soft-blue { background-color: #e3f2fd; }
.bg-soft-green { background-color: #e8f5e9; }
.bg-soft-purple { background-color: #f3e5f5; }
.bg-soft-orange { background-color: #fff3e0; }
.text-purple { color: #8e24aa; }
.text-orange { color: #ef6c00; }
.card { border-radius: 10px; }
.btn { border-radius: 20px; }
</style>
