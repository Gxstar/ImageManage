import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

/* 引入 Font Awesome 核心库和 Vue 组件 */
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/* 引入所有需要的图标 */
import {
  faCamera,
  faImages,
  faClock,
  faStar,
  faSyncAlt,
  faPlus,
  faChevronDown,
  faFolder,
  faTimes,
  faTimesCircle,
  faMountain,
  faUtensils,
  faBirthdayCake,
  faUser,
  faMapMarkerAlt,
  faCalendarAlt,
  faCog,
  faEdit,
  faShareAlt,
  faTrashAlt,
  faTags,
  faImage
} from '@fortawesome/free-solid-svg-icons'

import App from './App.vue'
import router from './router'
import './assets/style.css'

// 添加图标到库中
library.add(
  faCamera,
  faImages,
  faClock,
  faStar,
  faSyncAlt,
  faPlus,
  faChevronDown,
  faFolder,
  faTimes,
  faTimesCircle,
  faMountain,
  faUtensils,
  faBirthdayCake,
  faUser,
  faMapMarkerAlt,
  faCalendarAlt,
  faCog,
  faEdit,
  faShareAlt,
  faTrashAlt,
  faTags,
  faImage
)

const app = createApp(App)

app.use(ElementPlus)
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)

// 定义一个挂载应用的函数
const mountApp = () => {
  app.mount('#app')
  console.log('pywebview is ready, Vue App has been mounted.')
}

// 监听 pywebviewready 事件
// 当 pywebview 的 API 注入完成后，这个事件会被触发
window.addEventListener('pywebviewready', mountApp)