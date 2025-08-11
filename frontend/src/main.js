import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import './assets/style.css'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)

// 定义一个挂载应用的函数
const mountApp = () => {
  app.mount('#app')
  console.log('pywebview is ready, Vue App has been mounted.')
}

// 监听 pywebviewready 事件
// 当 pywebview 的 API 注入完成后，这个事件会被触发
window.addEventListener('pywebviewready', mountApp)