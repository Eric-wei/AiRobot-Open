import { createApp } from 'vue'
import App from './App.vue'
import Toast from "vue-toastification";
import "vue-toastification/dist/index.css";
const app = createApp(App)
// 配置 Toast 插件
const options = {
    // 你可以在这里设置全局选项，例如位置、超时等
    // position: "top-right",
    // timeout: 5000,
    // closeOnClick: true,
    // pauseOnFocusLoss: true,
    // pauseOnHover: true,
    // draggable: true,
    // draggablePercent: 0.6,
    // showCloseButtonOnHover: false,
    // hideProgressBar: false,
    // closeButton: "button",
    // icon: true,
    // rtl: false
  };
app.use(Toast, options);
app.mount('#app') 