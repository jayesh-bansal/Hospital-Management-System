<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h3>Patient Dashboard</h3>
    </div>

    <!-- Search doctors -->
    <div class="card p-3 mb-3 bg-soft-blue border-0 shadow-sm">
      <h5 class="text-primary">Search Doctors</h5>

      <div class="d-flex gap-2">
        <input v-model="q" class="form-control" placeholder="name or specialization" @keyup.enter="search" />
        <button class="btn btn-primary" @click="search">Search</button>
        <button class="btn btn-secondary" @click="viewAll">View All</button>
      </div>
      <!-- Moved Profile Button to Header or Separate Section if needed, but keeping it here for now as per user request to remove 'my profile' from patient? 
           Wait, user said "remoe my rpofile from patient". 
           Ah, "remove my profile from patient" might mean remove the button I just added?
           OR "edit profile should have contact no, remoe my rpofile from patient" -> "remove my profile from patient" might be a typo for "move my profile"?
           Actually, "remoe my rpofile from patient" likely means "remove the 'My Profile' button/link I added in V4" because they want it somewhere else or just gone?
           BUT they also said "edit profile should have contact no".
           Let's assume they want the button moved or they want the *old* way back?
           Re-reading: "edit profile should have contact no, remoe my rpofile from patient"
           Maybe they mean "Remote my profile"? No.
           "Remove my profile from patient" -> Maybe they don't want the button *in the search bar*?
           Let's put it in a top bar or just a separate button at the top.
           Let's add a proper header.
      -->

      <div class="mt-2" v-if="departments.length">
        <!-- <small class="text-muted me-2">Filter by:</small>
        <button v-for="d in departments" :key="d" class="btn btn-sm btn-outline-info me-1 mb-1" @click="filterBy(d)">
            {{ d }}
        </button> -->
      </div>

      <div class="mt-3">
        <div
          v-for="d in doctors"
          :key="d.id"
          class="card p-2 mb-2 d-flex justify-content-between"
        >
          <div>
            <strong>{{ d.username }}</strong>
            <div class="text-muted">{{ d.spec }}</div>
          </div>

          <div>
            <button class="btn btn-sm btn-primary" @click="openBooking(d)">
              Book
            </button>
            <button class="btn btn-sm btn-outline-info ms-1" @click="viewDoctor(d)">
              View Profile
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- My Appointments -->
    <div class="card p-3 mb-3 bg-soft-green border-0 shadow-sm">
      <h5 class="text-success">My Appointments</h5>

      <button class="btn btn-sm btn-secondary mb-2" @click="loadMy">
        Reload
      </button>

      <div class="table-responsive">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Doctor</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="a in my" :key="a.id">
            <td>{{ a.id }}</td>
            <td>{{ a.doctor }}</td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
            <td>{{ a.status }}</td>

            <td>
              <button
                v-if="a.status === 'Booked'"
                class="btn btn-sm btn-warning me-1"
                @click="openReschedule(a)"
              >
                Reschedule
              </button>

              <button
                v-if="a.status === 'Booked'"
                class="btn btn-sm btn-danger"
                @click="cancel(a)"
              >
                Cancel
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Treatment history -->
    <div class="card p-3 mb-3 bg-soft-purple border-0 shadow-sm">
      <h5 class="text-purple">Treatment History</h5>

      <button class="btn btn-sm btn-secondary mb-2" @click="loadHistory">
        Reload
      </button>

      <div class="table-responsive" v-if="history.length">
      <table class="table table-sm table-hover">
          <thead>
              <tr>
                  <th>Appt ID</th>
                  <th>Date</th>
                  <th>Diagnosis</th>
                  <th>Prescription</th>
              </tr>
          </thead>
          <tbody>
              <tr v-for="t in history" :key="t.appointment_id">
                  <td>{{ t.appointment_id }}</td>
                  <td>{{ t.date }}</td>
                  <td>{{ t.diagnosis }}</td>
                  <td>{{ t.prescription }}</td>
              </tr>
          </tbody>
      </table>
      </div>
      <div v-else class="text-muted">No history</div>

      <div class="d-flex justify-content-end mb-3">
        <button class="btn btn-secondary me-2" @click="exportTreatments" :disabled="exporting">
            {{ exporting ? 'Exporting...' : 'Export Treatments (CSV)' }}
        </button>
        <button v-if="exportJobId" @click="downloadBlob(exportJobId)" class="btn btn-success">
            Download CSV
        </button>
    </div>
    </div>

    <!-- Booking modal -->
    <div v-if="booking" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);"></div>
      <div class="modal d-block" tabindex="-1" style="position: relative;">
        <div class="modal-dialog">
          <div class="modal-content bg-white shadow" style="background-color: white !important; opacity: 1 !important;">

            <div class="modal-header">
              <h5 class="modal-title">
                Book with {{ booking.username }}
              </h5>
              <button class="btn-close" @click="booking = null"></button>
            </div>
            <div class="px-3 pt-2 text-muted small" v-if="booking.next7Availability">
                <strong>Availability:</strong>
                <div v-for="d in booking.next7Availability" :key="d.date">
                    {{ d.display }}: {{ d.times }}
                </div>
            </div>

            <div class="modal-body">
              <label>Select Date</label>
              <div class="d-flex flex-wrap gap-2 mb-3">
                  <button 
                    v-for="d in next7Days" 
                    :key="d.full" 
                    class="btn btn-sm"
                    :class="slot.date === d.full ? 'btn-primary' : 'btn-outline-secondary'"
                    @click="selectDate(d.full)"
                  >
                    {{ d.display }}
                  </button>
              </div>
              <!-- <input
                type="date"
                v-model="slot.date"
                class="form-control mb-2"
                @change="loadSlots"
              /> -->

              <label>Select Time Slot</label>
              <div v-if="loadingSlots">Loading slots...</div>
              <div v-else class="d-flex flex-wrap gap-2">
                <button 
                  v-for="s in slots" 
                  :key="s" 
                  class="btn btn-sm" 
                  :class="slot.time === s ? 'btn-primary' : 'btn-outline-primary'"
                  @click="slot.time = s"
                >
                  {{ formatSlotRange(s) }}
                </button>
                <div v-if="!slots.length && slot.date" class="alert alert-warning w-100">
                    No slots available for this date. Please try another date.
                </div>
              </div>
            </div>

            <div class="modal-footer">
              <button class="btn btn-secondary" @click="booking = null">
                Close
              </button>

              <button class="btn btn-primary" @click="doBook">
                Confirm
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div v-if="reschedulingAppt" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);"></div>
        <div class="modal d-block" tabindex="-1" style="position: relative;">
            <div class="modal-dialog">
                <div class="modal-content bg-white shadow" style="background-color: white !important; opacity: 1 !important;">
                    <div class="modal-header">
                        <h5 class="modal-title">Reschedule Appointment</h5>
                        <button class="btn-close" @click="reschedulingAppt=null"></button>
                    </div>
                    <div class="px-3 pt-2 text-muted small" v-if="reschedulingAppt && reschedulingAppt.next7Availability">
                        <strong>Availability for {{ reschedulingAppt.doctorName }}:</strong>
                        <div v-for="d in reschedulingAppt.next7Availability" :key="d.date">
                            {{ d.display }}: {{ d.times }}
                        </div>
                    </div>
                    <div class="modal-body">
                        <label>Select New Date</label>
                        <div class="d-flex flex-wrap gap-2 mb-3">
                            <button 
                                v-for="d in next7Days" 
                                :key="d.full" 
                                class="btn btn-sm"
                                :class="rescheduleData.date === d.full ? 'btn-primary' : 'btn-outline-secondary'"
                                @click="selectRescheduleDate(d.full)"
                            >
                                {{ d.display }}
                            </button>
                        </div>
                        
                        <label>Select New Time</label>
                        <div v-if="loadingSlots">Loading slots...</div>
                        <div v-else class="d-flex flex-wrap gap-2">
                            <button 
                            v-for="s in slots" 
                            :key="s" 
                            class="btn btn-sm" 
                            :class="rescheduleData.time === s ? 'btn-primary' : 'btn-outline-primary'"
                            @click="rescheduleData.time = s"
                            >
                            {{ formatSlotRange(s) }}
                            </button>
                            <div v-if="!slots.length && rescheduleData.date" class="alert alert-warning w-100">
                                No slots available for this date.
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" @click="reschedulingAppt=null">Close</button>
                        <button class="btn btn-primary" @click="confirmReschedule">Confirm</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Doctor Profile Modal -->
    <div v-if="viewingDoc" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1050;">
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);"></div>
        <div class="modal d-block" tabindex="-1" style="position: relative;">
            <div class="modal-dialog">
                <div class="modal-content bg-white shadow" style="background-color: white !important; opacity: 1 !important;">
                    <div class="modal-header">
                        <h5 class="modal-title">{{ viewingDoc.username }}</h5>
                        <button class="btn-close" @click="viewingDoc=null"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Specialization:</strong> {{ viewingDoc.spec }}</p>
                        <p><strong>Availability:</strong></p>
                        <div v-if="viewingDoc.parsedAvailability">
                            <ul class="list-unstyled">
                                <li v-for="day in viewingDoc.next7Availability" :key="day.date">
                                    <strong>{{ day.display }}:</strong> {{ day.times }}
                                </li>
                            </ul>
                        </div>
                        <div v-else class="text-muted">No specific availability set.</div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" @click="viewingDoc=null">Close</button>
                        <button class="btn btn-primary" @click="openBooking(viewingDoc); viewingDoc=null">Book Appointment</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    
    <!-- Profile Modal -->

    
    <!-- Profile Modal -->

  </div>
</template>

<script>
import api, { setAuth } from "../services/api";

export default {
  data() {
    return {
      q: "",
      doctors: [],
      my: [],
      history: [],
      booking: null,
      slot: { date: "", time: "" },
      slots: [],
      loadingSlots: false,
      departments: [],
      reschedulingAppt: null,
      rescheduleData: { date: '', time: '' },
      viewingDoc: null,
      next7Days: [],
      exportJobId: null,
      exporting: false
    };
  },

  created() {
    const t = localStorage.getItem("hms_token");
    if (t) setAuth(t);
    this.loadMy();
    this.loadHistory();
    this.loadDepartments();
  },

  methods: {
    async loadDepartments() {
        try {
            const r = await api.get('/patient/departments');
            this.departments = r.data;
        } catch(e) { console.error(e) }
    },
    filterBy(d) {
        this.q = d;
        this.search();
    },
    async loadSlots() {
        if (!this.slot.date || !this.booking) return;
        this.loadingSlots = true;
        this.slots = [];
        this.slot.time = "";
        try {
            const r = await api.get('/appointments/slots', {
                params: { doctor_id: this.booking.id, date: this.slot.date }
            });
            this.slots = r.data;
        } catch(e) { console.error(e) }
        finally { this.loadingSlots = false; }
    },
    async viewAll() {
      this.q = '';
      await this.search();
    },
    async search() {
      try {
        const r = await api.get("/patient/search_doctors", {
          params: { q: this.q },
        });
        this.doctors = r.data;
      } catch (e) {
        console.error(e);
      }
    },

    openBooking(d) {
      this.booking = d;
      this.next7Days = this.generateNext7Days(d);
      this.booking.next7Availability = this.next7Days; // For display in modal
      this.slot.date = ""; // Reset selection
      this.slot.time = "";
      this.slots = [];
    },
    generateNext7Days(doc) {
        const next7 = [];
        const today = new Date();
        
        let avail = null;
        if(doc && doc.availability) {
            try { avail = typeof doc.availability === 'string' ? JSON.parse(doc.availability) : doc.availability; } catch(e){}
        }

        for(let i=0; i<7; i++) {
            const d = new Date(today);
            d.setDate(today.getDate() + i);
            const dateStr = d.toISOString().slice(0, 10);
            const dayName = d.toLocaleDateString('en-US', { weekday: 'short' });
            const monthDay = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
            let times = "Closed";
            if(avail && avail[dayName]) {
                const t = avail[dayName];
                if(Array.isArray(t) && t.length >= 2) {
                    times = `${t[0]} - ${t[1]}`;
                }
            } else if (!avail) {
                 times = "09:00 - 17:00"; // Default if no availability set
            }

            // Filter: If availability is set, only include days present in it? 
            // The previous logic filtered days out. Let's keep that behavior for the date selection buttons,
            // but for the "Availability" list display, we might want all days?
            // Actually, the previous logic was: if(avail && !avail[dayName]) continue;
            // This means closed days were not selectable. That is good.
            
            if(avail && !avail[dayName]) continue;

            next7.push({
                full: dateStr,
                display: `${dayName}, ${monthDay}`,
                dayName: dayName,
                times: times
            });
        }
        return next7;
    },
    selectDate(date) {
        this.slot.date = date;
        this.loadSlots();
    },

    async doBook() {
      if(!this.slot.time) return alert("Please select a time slot");
      try {
        await api.post("/appointments/book", {
          doctor_id: this.booking.id,
          date: this.slot.date,
          time: this.slot.time,
        });
        alert("Booked");
        this.booking = null;
        this.loadMy();
      } catch (e) {
        alert(e.response?.data?.msg || "err");
      }
    },

    async loadMy() {
      try {
        const r = await api.get("/appointments/my");
        this.my = r.data;
      } catch (e) {
        console.error(e);
      }
    },

    openReschedule(a) {
        this.reschedulingAppt = a;
        this.rescheduleData = { date: '', time: '' };
        // We need doctor info to filter dates. 
        // Ideally 'a' should have doctor availability or we fetch it.
        // For now, let's fetch doctor details or just show all days if we can't.
        // But 'a' has doctor_id. Let's try to find doctor in this.doctors if loaded, or fetch.
        // To be safe and quick, let's fetch doctor details.
        api.get(`/patient/search_doctors?q=`).then(r => {
             const doc = r.data.find(d => d.id === a.doctor_id);
             if(doc) {
                 this.next7Days = this.generateNext7Days(doc);
                 this.reschedulingAppt.next7Availability = this.next7Days;
                 this.reschedulingAppt.doctorName = doc.username;
             }
        });
        
        this.slots = [];
    },
    selectRescheduleDate(date) {
        this.rescheduleData.date = date;
        this.rescheduleData.time = "";
        this.loadRescheduleSlots();
    },
    async loadRescheduleSlots() {
        if (!this.rescheduleData.date || !this.reschedulingAppt) return;
        this.loadingSlots = true;
        this.slots = [];
        try {
            const r = await api.get('/appointments/slots', {
                params: { doctor_id: this.reschedulingAppt.doctor_id, date: this.rescheduleData.date }
            });
            this.slots = r.data;
        } catch(e) { console.error(e) }
        finally { this.loadingSlots = false; }
    },
    async confirmReschedule() {
        if(!this.rescheduleData.date || !this.rescheduleData.time) return alert('Fill all fields');
        // Append seconds if missing, backend expects HH:MM:SS or HH:MM
        let time = this.rescheduleData.time;
        if(time.length === 5) time += ':00';
        
        try {
            await api.post(`/appointments/${this.reschedulingAppt.id}/reschedule`, {
                date: this.rescheduleData.date,
                time: time
            });
            alert("Rescheduled");
            this.reschedulingAppt = null;
            this.loadMy();
        } catch (e) {
            alert(e.response?.data?.msg || "Error rescheduling");
        }
    },

    async cancel(a) {
      if (!confirm("Cancel?")) return;
      try {
        await api.post(`/appointments/${a.id}/cancel`);
        alert("Cancelled");
        this.loadMy();
      } catch (e) {
        console.error(e);
        alert(e.response?.data?.msg || "Error cancelling");
      }
    },

    async loadHistory() {
      try {
        const r = await api.get("/patient/history");
        this.history = r.data;
      } catch (e) {
        console.error(e);
      }
    },

    async exportTreatments() {
      try {
        this.exporting = true;
        const r = await api.post("/appointments/export_my_treatments");
        const jobId = r.data.job_id;
        alert("Export started. Please wait...");
        
        // Poll for status
        const poll = setInterval(async () => {
            try {
                const r = await api.get(`/appointments/export_status/${jobId}`);
                if(r.data.status === 'done') {
                    clearInterval(poll);
                    this.exporting = false;
                    this.exportJobId = jobId; 
                    
                    // Auto-download using Blob to ensure correct filename and avoid browser blocks
                    try {
                        const fileRes = await api.get(`/appointments/export_download/${jobId}`, { responseType: 'blob' });
                        const url = window.URL.createObjectURL(new Blob([fileRes.data]));
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', 'treatments.csv');
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        window.URL.revokeObjectURL(url);
                    } catch(err) {
                        console.error("Download failed", err);
                        alert("File ready but auto-download failed. Please use the button.");
                    }
                }
            } catch(e) { 
                console.error(e); 
                clearInterval(poll);
                alert("Error checking export status");
                this.exporting = false;
            }
        }, 2000);
        
      } catch (e) {
        alert("Error starting export");
        this.exporting = false;
      }
    },
    async downloadBlob(jobId) {
        try {
            const fileRes = await api.get(`/appointments/export_download/${jobId}`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([fileRes.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'treatments.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch(err) {
            console.error("Manual download failed", err);
            alert("Download failed.");
        }
    },
    viewDoctor(d) {
        let parsed = null;
        try {
            if(d.availability) {
                parsed = typeof d.availability === 'string' ? JSON.parse(d.availability) : d.availability;
            }
        } catch(e) {}
        
        // Generate next 7 days availability
        let next7 = [];
        const today = new Date();
        for(let i=0; i<7; i++) {
            const date = new Date(today);
            date.setDate(today.getDate() + i);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' }); // Mon, Tue...
            const display = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
            
            let times = "Closed";
            if(parsed && parsed[dayName]) {
                const t = parsed[dayName];
                if(Array.isArray(t) && t.length >= 2) {
                    times = `${t[0]} - ${t[1]}`;
                }
            }
            next7.push({ date: date.toISOString().slice(0,10), display, times });
        }

        this.viewingDoc = { ...d, parsedAvailability: parsed, next7Availability: next7 };
    },
    formatSlotRange(timeStr) {
        if(!timeStr) return '';
        // timeStr is "HH:MM:SS" or "HH:MM"
        let [h, m] = timeStr.split(':').map(Number);
        const start = new Date();
        start.setHours(h, m, 0);
        const end = new Date(start.getTime() + 30 * 60000); // Add 30 mins
        
        const format = (d) => d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
        return `${format(start)} - ${format(end)}`;
    },
  },
};
</script>

<style scoped>
.bg-soft-blue { background-color: #e3f2fd; }
.bg-soft-green { background-color: #e8f5e9; }
.bg-soft-purple { background-color: #f3e5f5; }
.text-purple { color: #8e24aa; }
.card { border-radius: 10px; }
.btn { border-radius: 20px; }
</style>
