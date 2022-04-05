import { createApp } from 'vue'
import App from './App.vue'
import GAuth from 'vue3-google-oauth2'

const vue_app = createApp(App)

// Setup gAuth.
const gClientId = '1085740345330-j4vl5avfsnfecdm1us5l7vgaqs99l273.apps.googleusercontent.com'
const gAuthOptions = { clientId: gClientId, scope: 'email', prompt: 'consent', fetch_basic_profile: true }
vue_app.use(GAuth, gAuthOptions)

vue_app.mount('#app')