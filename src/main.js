import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' // 引入刚刚写好的路由文件

const app = createApp(App)

app.use(router) // 告诉应用使用路由
app.mount('#app')
